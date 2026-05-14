load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
 
 a = addfile("/home/khanh/Documents/pgw/test/NCAR_ERA5_scripts/CMIP6_period/<MODEL>/CMIP6.r1i1p1f1.<MODEL>.historical.<VAR>.1991-2020.nc","w")
  
  
 indata = a-><VAR>
 nscan = 2000 ; usually *much* fewer
 eps = 0.001 ; variable depended
 gtype = True ; "gendat" does not generate cyclic fields
 guess = 0 ; use zonal means
 relc = 0.6 ; standard relaxation coef
 opt = 0
 
 poisson_grid_fill(indata, gtype, guess, nscan, eps, relc, opt)
 
 a-><VAR>=indata
