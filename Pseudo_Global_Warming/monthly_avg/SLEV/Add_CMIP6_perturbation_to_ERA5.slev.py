#!/usr/bin/env python3

import numpy as np
import xarray as xr
import netCDF4 as nc
import datetime
import sys

param_model = 'E5'
outfile = sys.argv[1]

# See https://bmcnoldy.earth.miami.edu/Humidity.html

def sub_DewT_to_RH(in_T, in_DT):
    
    '''
    in_T and in_DT in K
    '''
    in_Tc = in_T - 273.15
    in_DTc = in_DT - 273.15
    
    outdata = 100 * (np.exp(17.625*in_DTc/(243.04+in_DTc))/np.exp(17.625*in_Tc/(243.04+in_Tc)))
    
    return outdata


def sub_RH_to_DewT(in_T, in_RH):
    
    '''
    in_T in K, RH in % (so 0-100)
    '''
    
    in_Tc = in_T - 273.15
    
    outdata = 243.04 *(np.log(in_RH/100)+((17.625*in_Tc)/(243.04+in_Tc)))/(17.625-np.log(in_RH/100)-((17.625*in_Tc)/(243.04+in_Tc)))
    
    outdata += 273.15
    
    return outdata



def construct_singal_SingleLevel(invar, inmonth_raw=[11,12,1], inmodel='none'):
    
    inmonth = [i-1 for i in inmonth_raw]
    
    infile = '/home/khanh/Documents/pgw/test/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    with xr.open_dataset(infile) as inds:
        outdata = inds[invar].values[inmonth].mean(axis=0)
            
    return outdata

def construct_singal_Soil(invar, inmonth_raw=[11,12,1], in_level=0, inmodel='none'):
    
    inmonth = [i-1 for i in inmonth_raw]
    infile = '/home/khanh/Documents/pgw/test/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    with xr.open_dataset(infile) as inds:
        outdata = inds[invar].values[inmonth][:,in_level,:,:].mean(axis=0)

    return outdata



month = [11,12,1]
PGWdata = {}
for var in ['hurs', 'tas', 'uas', 'vas', 'ps', 'tos', 'mrsoR', 'psl']:
    my_data = construct_singal_SingleLevel(var, month, inmodel=param_model)
    #print(my_data.shape, CMIP6_mask.shape)
    PGWdata[var] = my_data
    
    
for i in np.arange(4):
    my_data = construct_singal_Soil('tsl', month, in_level=i, inmodel=param_model)
    PGWdata['tsl%d'%i] = my_data


# Use RH to update "RH", then back to Td. Note use the update T2 for Td calculation
with xr.open_dataset(outfile) as inds:
    nt,nx,ny = inds['sp'].shape[0:3]
    
    T_data = inds['2t'].values
    Td_data = inds['2d'].values


RH_orig = sub_DewT_to_RH(T_data, Td_data)
RH_PGW = np.zeros(RH_orig.shape)
T2_PGW = np.zeros(RH_orig.shape)

for i in np.arange(RH_orig.shape[0]):
    RH_PGW[i] =  RH_orig[i] + PGWdata['hurs']
    my_data = RH_PGW[i].copy()
    RH_PGW[i][np.where(my_data>100)] = 100
    RH_PGW[i][np.where(my_data<0)] = 0
    
    T2_PGW[i] = T_data[i] + PGWdata['tas']

Td_PGW = sub_RH_to_DewT(T2_PGW, RH_PGW)


rootgroup = nc.Dataset(outfile, 'a', format='NETCDF4')

for t in np.arange(nt):
    
    print(t)
    
    # adjust data, using same delta for all the time steps
    # TS, skin temperature, var235
    rootgroup.variables['skt'][t,:,:] += PGWdata['tos']
    # TS, SST, var34
    rootgroup.variables['sst'][t,:,:] += PGWdata['tos']
    # T2, var167
    rootgroup.variables['2t'][t,:,:] += PGWdata['tas']
    # U10, var165
    rootgroup.variables['10u'][t,:,:] += PGWdata['uas']
    # V10, var166
    rootgroup.variables['10v'][t,:,:] += PGWdata['vas']
    # TD, var168 (Dew point T2)
    rootgroup.variables['2d'][t,:,:] = Td_PGW[t]

    # PMSL or SLP, var151
    rootgroup.variables['msl'][t,:,:] += PGWdata['psl']
    # PSFC or PS, var134
    rootgroup.variables['sp'][t,:,:] += PGWdata['ps']
    
    # ST000007, var139
    rootgroup.variables['stl1'][t,:,:] += PGWdata['tsl0']
    # ST007028, var170
    rootgroup.variables['stl2'][t,:,:] += PGWdata['tsl1']
    # ST028100, var183
    rootgroup.variables['stl3'][t,:,:] += PGWdata['tsl2']
    # ST100289, var236
    rootgroup.variables['stl4'][t,:,:] += PGWdata['tsl3']
    
    # SMxxxxxx, var39-42
    for varid in ['swvl1', 'swvl2', 'swvl3', 'swvl4']:
        rootgroup.variables[varid][t,:,:] *= PGWdata['mrsoR']
        tmp_data = rootgroup.variables[varid][t,:,:].copy()
        rootgroup.variables[varid][t,:,:][np.where(tmp_data>1.0)] = 1.0

rootgroup.close()
