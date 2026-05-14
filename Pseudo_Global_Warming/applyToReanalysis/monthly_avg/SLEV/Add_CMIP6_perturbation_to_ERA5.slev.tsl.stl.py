#!/usr/bin/env python3

import numpy as np
import xarray as xr
import netCDF4 as nc
import datetime
import sys

param_model = 'E5'
outfile = sys.argv[1]
stl = outfile.split('_')[4]
print('outfile: ', stl)

def construct_singal_Soil(invar, inmonth_raw, in_level=0, inmodel='none'):
    
    inmonth = [i-1 for i in inmonth_raw]
    infile = '/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    with xr.open_dataset(infile) as inds:
        outdata = inds[invar].values[inmonth][:,in_level,:,:].mean(axis=0)

    return outdata
    
# month = [2,3,4,5,6,7,8,9,10,11,12,1]
month = [int(outfile.split('.')[6][4:6])]
PGWdata = {}
    
for i in np.arange(1):
    my_data = construct_singal_Soil('tsl', month, in_level=i, inmodel=param_model)
    PGWdata['var' + str(stl)] = my_data


# Use RH to update "RH", then back to Td. Note use the update T2 for Td calculation
with xr.open_dataset(outfile) as inds:
    nt,nx,ny = inds['var' + stl].shape[0:3]

rootgroup = nc.Dataset(outfile, 'a', format='NETCDF4')

for t in np.arange(nt):
    
    print(t)
    
    # adjust data, using same delta for all the time steps
    # ST000007, var139 = tsl
    rootgroup.variables['var' + stl][t,:,:] += PGWdata['var' + str(int(stl))]
    # # ST007028, var170
    # rootgroup.variables['stl2'][t,:,:] += PGWdata['tsl1']
    # # ST028100, var183
    # rootgroup.variables['stl3'][t,:,:] += PGWdata['tsl2']
    # # ST100289, var236
    # rootgroup.variables['stl4'][t,:,:] += PGWdata['tsl3']

rootgroup.close()
