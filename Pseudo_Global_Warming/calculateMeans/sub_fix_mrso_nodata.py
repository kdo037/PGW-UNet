#!/usr/bin/env python3

import numpy as np
import netCDF4 as nc
import xarray as xr
import sys

model = sys.argv[1]
period = sys.argv[2]

if period=='historical':
	reffile = "/home/khanh/Documents/pgw/test/CMIP6_period/%s/CMIP6.r1i1p1f1.%s.%s.tsl.1991-2020.nc" % (model, model, period)
	infile = "/home/khanh/Documents/pgw/test/tmp/CMIP6.r1i1p1f1.%s.%s.mrso.1991-2020.ymonmean.nc" % (model ,period)
	print("infile: ", infile)
elif period=='ssp585':
	reffile = "/home/khanh/Documents/pgw/test/CMIP6_period/%s/CMIP6.r1i1p1f1.%s.%s.tsl.2041-2070.nc" % (model, model, period)
	infile = "/home/khanh/Documents/pgw/test/tmp/CMIP6.r1i1p1f1.%s.%s.mrso.2041-2070.ymonmean.nc" % (model, period)


with xr.open_dataset(reffile) as inds:
	ref_tsl = inds['tsl'][0:12,0,:,:].values


ingroup = nc.Dataset(infile, 'a', format='NETCDF4')
indata = ingroup.variables['mrso'][:].copy()

indata[np.isnan(ref_tsl)] = 1e+20
ingroup.variables['mrso'][:]  = indata

ingroup.close()