#!/usr/bin/env python

import numpy as np
import netCDF4 as nc
import sys

# tag_grid = sys.argv[0]
print(sys.argv[0])
# infile = '/home/khanh/Documents/pgw/test/PGW/CMIP6_delta/%s/CMIP6.MPI-ESM1-2-LR.ratio.mrsoR.%sgrid.nc' % (tag_grid, tag_grid)

infile = '/home/khanh/Documents/pgw/test/NCAR_ERA5_scripts/CMIP6_delta/E5/ACCESS-CM2/CMIP6.ACCESS-CM2.ratio.mrsoR.E5grid.nc'
ingroup = nc.Dataset(infile, 'a', format='NETCDF4')

indata = ingroup.variables['mrsoR'][:].copy()
indata[np.isnan(indata)] = 1

ingroup.variables['mrsoR'][:] = indata


ingroup.close()