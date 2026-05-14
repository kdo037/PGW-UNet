#!/usr/bin/env python3

import numpy as np
import xarray as xr
import netCDF4 as nc
import datetime
import sys

param_model = 'E5'
outfile = sys.argv[1]

def construct_singal_3D_full(invar, inmonth_raw, inmodel='none'):
    
    nmonth = len(inmonth_raw)
    inmonth = [i-1 for i in inmonth_raw]
    print("inmonth: ", inmonth)
    outdata = np.zeros((nmonth, 37, 721, 1440))
    infile = '/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/CMIP6_delta/ens_mean/%s/CMIP6.ens_mean.diff.%s.%sgrid.nc' % (inmodel, invar, inmodel)
    outdata = xr.open_dataset(infile)[invar].values[inmonth]
    return outdata.mean(axis=(0))


# month = [2,3,4,5,6,7,8,9,10,11,12,1]
month = [int(outfile.split('.')[6][4:6])]
PGWdata = {}
for var in ['ta']:
    my_data = construct_singal_3D_full(var, month, inmodel=param_model)
    PGWdata[var] = my_data


with xr.open_dataset(outfile) as inds:
    # temperature t = var130
    nt, nlev = inds['var130'].shape[0:2]
    
rootgroup = nc.Dataset(outfile, 'a', format='NETCDF4')

# for t in np.arange(nt):
    
#     print(t)

#     # adjust data, using same delta for all the time steps
#     # TT, var130
#     rootgroup.variables['var130'][t,:,:,:] += PGWdata['ta']

rootgroup.variables['var130'][:,:,:,:] += PGWdata['ta']

rootgroup.close()
