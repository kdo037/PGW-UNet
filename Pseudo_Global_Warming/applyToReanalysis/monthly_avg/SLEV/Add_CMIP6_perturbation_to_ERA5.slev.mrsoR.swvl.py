#!/usr/bin/env python3

import numpy as np
import xarray as xr
import netCDF4 as nc
import datetime
import sys

param_model = 'E5'
outfile = sys.argv[1]

swvl = outfile.split('_')[4][1:3]

def construct_singal_SingleLevel(invar, inmonth_raw, inmodel='none'):
    
    inmonth = [i-1 for i in inmonth_raw]
    
    infile = '/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    with xr.open_dataset(infile) as inds:
        outdata = inds[invar].values[inmonth].mean(axis=0)
            
    return outdata

# month = [2,3,4,5,6,7,8,9,10,11,12,1]
month = [int(outfile.split('.')[6][4:6])]
PGWdata = {}
for var in ['mrsoR']:
    my_data = construct_singal_SingleLevel(var, month, inmodel=param_model)
    #print(my_data.shape, CMIP6_mask.shape)
    PGWdata[var] = my_data

# Use RH to update "RH", then back to Td. Note use the update T2 for Td calculation
with xr.open_dataset(outfile) as inds:
    nt,nx,ny = inds['var' + swvl].shape[0:3]

rootgroup = nc.Dataset(outfile, 'a', format='NETCDF4')

for t in np.arange(nt):
    
    print(t)
    
    # SMxxxxxx, var39-42 (var39 = swvl)
    rootgroup.variables['var' + swvl][t,:,:] *= PGWdata['mrsoR']
    tmp_data = rootgroup.variables['var' + swvl][t,:,:].copy()
    rootgroup.variables['var' + swvl][t,:,:][np.where(tmp_data>1.0)] = 1.0

rootgroup.close()
