#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 15:03:40 2025

@author: khanh
"""

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import time
#from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
#from sklearn.linear_model import LinearRegression
import pandas as pd
import csv
import netCDF4 as nc
import math
from math import radians, cos, sin, asin, sqrt
import datetime as tdelta

###################################################################################################################
# paths
ssp = '2010'
wrfDir = f'/glade/campaign/univ/uncs0034/kdo/wrfout_backup/base_noFDDA/'
t2ML = f'/glade/campaign/univ/uncs0034/kdo/ML/downscale/downscale_paper/ML_Predicted/{ssp}/t2/'
q2ML = f'/glade/campaign/univ/uncs0034/kdo/ML/downscale/downscale_paper/ML_Predicted/{ssp}/'
domain = 'd03'
# model base time
modelTime = datetime.strptime('2010' + '-' + '05' + '-' + '01' + ' ' + '00', '%Y-%m-%d %H')
# Define desired date range
starts = datetime(2010,5,1,0,0,0)  # start date
ends = datetime(2010,9,27,0,0,0) # end date
numberOfDay = 3
outNetCDFName = f'rh2_{ssp}_d03_'
outDir = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/downscale_paper/ML_Predicted/rh2/'
############################ MODIFY ###############################################################################

# eval function
def compute_metrics(o: np.ndarray, m: np.ndarray):
    cc = sum((m-np.mean(m))*(o-np.mean(o)))/(sum((m-np.mean(m))**2)*sum((o-np.mean(o))**2))**0.5
    mbe = np.mean(m-o)
    mae = np.mean(np.abs(m-o))
    nmb = sum(m-o)/sum(o)*100
    corr_matrix = np.corrcoef(m, o)
    corr = corr_matrix[0, 1]
    r2 = corr**2
    mmean = np.mean(m)
    mmax = np.max(m)
    mmin = np.min(m)
    omean = np.mean(o)
    omax = np.max(o)
    omin = np.min(o)
    
    return cc, r2, mbe, mae, nmb, mmin, mmean, mmax, omin, omean, omax

# import all wrfout files
wrftmp = []
uwind10 = []
vwind10 = []
wrfpsfc = []
wrfq2 = []
wrftime = []
test = []
initFlag = True
start = starts
end = ends

while start <= end:
    if start.month < 10: 
        smonth = '0' + str(start.month)
    else:
        smonth = str(start.month)
    if start.day < 10: 
        sdate = '0' + str(start.day)
    else:
        sdate = str(start.day)
    syear = str(start.year)
    file = 'wrfout_'+domain+'_' + syear + '-' + smonth + '-' + sdate + '_00:00:00'
    inFile = wrfDir + '/' + file
    ds_in = nc.Dataset(inFile)
    
    if initFlag == True:
        # xlat = np.array(ds_in['XLAT'][0,:,:])
        # xlong = np.array(ds_in['XLONG'][0,:,:])
        # wrftmp = np.array(ds_in['T2']) # [time, south_north, west_east]
        # uwind10 = np.array(ds_in['U10'])
        # vwind10 = np.array(ds_in['V10'])
        wrfpsfc = np.array(ds_in['PSFC'])
        print(np.shape(np.array(ds_in['PSFC'])))
        # wrfq2 = np.array(ds_in['Q2'])
        wrftime.append(start)
        initFlag = False
    else:
        # wrftmp = np.vstack((wrftmp, np.array(ds_in['T2'])))
        # uwind10 = np.vstack((uwind10, np.array(ds_in['U10'])))
        # vwind10 =  np.vstack((vwind10, np.array(ds_in['V10'])))
        wrfpsfc = np.vstack((wrfpsfc, np.array(ds_in['PSFC'])))
        # wrfq2 = np.vstack((wrfq2, np.array(ds_in['Q2'])))
        wrftime.append(start)
        print(np.shape(np.array(ds_in['PSFC'])))

    start += tdelta.timedelta(days=1)
    print('Date: ' + str(start))

# import Q2 from ML
startDate = starts + tdelta.timedelta(days=numberOfDay) # start date
endDate = ends + tdelta.timedelta(days=numberOfDay) # end date

dnt = []
init = True
while startDate <= endDate:
    # import ML Q2
    # p = 't2_ssp585_46_56_d03_' + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2)
    p_q2 = f'q2_2006_d03_' + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2)
    q2_in = nc.Dataset(q2ML+p_q2+'.nc')
    q2_unet = np.array(q2_in['Q2'])

    p_t2 = f't2_2010_d03_' + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2)
    t2_in = nc.Dataset(t2ML+p_t2+'.nc')
    t2_unet = np.array(t2_in['T2'])
    
    if init == True:
        init = False
        unetDomainQ2 = q2_unet
        unetDomainT2 = t2_unet
    else:
        unetDomainQ2 = np.vstack((unetDomainQ2, q2_unet))
        unetDomainT2 = np.vstack((unetDomainT2, t2_unet))
    
    for i in range(0, numberOfDay*24):
        dnt.append(startDate + tdelta.timedelta(hours=i) - tdelta.timedelta(days=numberOfDay))
    
    startDate = startDate + tdelta.timedelta(days = numberOfDay)
   
    print(startDate)
    
## compute wrf relative humidity
#e = wrfq2*wrfpsfc/0.622
#es = 610.8*np.exp(17.3*(wrftmp - 273.15) / (wrftmp - 273.15 + 237.3))
#wrfRh1 = 100*e/es
#wrfRh1[wrfRh1 > 100] = 100

wrfq2 = np.array(unetDomainQ2)
wrfpsfc = wrfpsfc[0:len(unetDomainQ2)]
wrftmp = np.array(unetDomainT2[0:len(unetDomainQ2)])
unetRh = 0.263*wrfq2*wrfpsfc*(np.exp((17.67*(wrftmp - 273.15)) / (wrftmp - 29.65)))**(-1)
unetRh[unetRh > 100] = 100

# write to nc
startDate = starts  + tdelta.timedelta(days=numberOfDay) # start date
endDate = ends + tdelta.timedelta(days=numberOfDay) # end date

dayCount = 0
while startDate <= endDate:
    # creating ds_out file
    p = outNetCDFName + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2)
    ds_out = nc.Dataset(outDir+p+'.nc', "w")
    
    # create dimensions
    _ = ds_out.createDimension('time', None)
    _ = ds_out.createDimension('lon', 606)
    _ = ds_out.createDimension('lat', 750)
    
    # m2dArrayResize = cv2.resize(m2dArray[:, :, :], (606, 750))
    
    v_in = np.array(unetRh[dayCount*24:(dayCount+numberOfDay)*24])
    v_in_unit = '%'
    v_out = ds_out.createVariable(
        'RH2',
        np.float32,
        ("time", "lon", "lat"),
        zlib=True,
        complevel=1,
    )
    # Note: `zlib=True` is deprecated in favor of `compression='zlib'`
    # Note: complevel=4 is default, 0--9 with 9 most compression
    v_out.units = v_in_unit
    v_out[:] = 0
    
    v_out[:] = v_in[:]
    ds_out.close()
    
    dayCount = dayCount + 3
    
    startDate = startDate + tdelta.timedelta(days = numberOfDay)
    
#wrfDomainAvg = np.mean(wrfRh1, axis=(0))
#unetDomainAvg = np.mean(unetRh, axis=(0))
#
#cc, r2, mbe, mae, nmb, mmin, mmean, mmax, omin, omean, omax = compute_metrics(np.reshape(wrfDomainAvg, 606*750), np.reshape(unetDomainAvg, 606*750))

