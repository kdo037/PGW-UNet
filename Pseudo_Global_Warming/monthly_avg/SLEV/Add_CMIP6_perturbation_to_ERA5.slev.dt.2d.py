#!/usr/bin/env python3

import numpy as np
import xarray as xr
import netCDF4 as nc
import datetime
import sys

param_model = 'E5'
outfile = sys.argv[1]
print('outfile: ', outfile)
a = outfile.split('.')
outfile_2t = a[0] + '.' + a[1] + '.' + a[2] + '.' + a[3] + '.' + '128_167_2t.' + a[5] + '.' + a[6] + '.' + a[7] + '.' + a[8]
print('outfile_2t: ', outfile_2t)
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



def construct_singal_SingleLevel(invar, inmonth_raw, inmodel='none'):
    
    inmonth = [i-1 for i in inmonth_raw]
    
    infile = '/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    with xr.open_dataset(infile) as inds:
        outdata = inds[invar].values[inmonth].mean(axis=0)
            
    return outdata

def construct_singal_Soil(invar, inmonth_raw, in_level=0, inmodel='none'):
    
    inmonth = [i-1 for i in inmonth_raw]
    infile = '/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    with xr.open_dataset(infile) as inds:
        outdata = inds[invar].values[inmonth][:,in_level,:,:].mean(axis=0)

    return outdata



# month = [2,3,4,5,6,7,8,9,10,11,12,1]
month = [int(outfile.split('.')[6][4:6])]
PGWdata = {}
for var in ['hurs', 'tas']:
    my_data = construct_singal_SingleLevel(var, month, inmodel=param_model)
    #print(my_data.shape, CMIP6_mask.shape)
    PGWdata[var] = my_data
    
    
for i in np.arange(4):
    my_data = construct_singal_Soil('tsl', month, in_level=i, inmodel=param_model)
    PGWdata['tsl%d'%i] = my_data


# Use RH to update "RH", then back to Td. Note use the update T2 for Td calculation
with xr.open_dataset(outfile) as inds:
    nt,nx,ny = inds['var168'].shape[0:3]
    
    Td_data = inds['var168'].values
Td_data = np.nan_to_num(Td_data, nan=-100)
Td_data[Td_data > 500] = np.median(Td_data)

# var167 = 2t
with xr.open_dataset(outfile_2t) as inds:
    T_data = inds['var167'].values

T_data[T_data > 500] = np.median(T_data)

RH_orig = sub_DewT_to_RH(T_data, Td_data)
RH_PGW = np.zeros(RH_orig.shape)
T2_PGW = np.zeros(RH_orig.shape)

for i in np.arange(RH_orig.shape[0]):
    RH_PGW[i] =  RH_orig[i] + PGWdata['hurs']
    my_data = RH_PGW[i].copy()
    RH_PGW[i][np.where(my_data>100)] = 100
    RH_PGW[i][np.where(my_data<0)] = 0.00001
    
    T2_PGW[i] = T_data[i] + PGWdata['tas']

Td_PGW = sub_RH_to_DewT(T2_PGW, RH_PGW)

print(np.count_nonzero(np.isnan(Td_PGW)))
Td_PGW = np.nan_to_num(Td_PGW, nan=100)

rootgroup = nc.Dataset(outfile, 'a', format='NETCDF4')

for t in np.arange(nt):
    
    print(t)
    
    # adjust data, using same delta for all the time steps
    # TD, var168 = 2d (Dew point T2)
    rootgroup.variables['var168'][t,:,:] = Td_PGW[t]

rootgroup.close()
