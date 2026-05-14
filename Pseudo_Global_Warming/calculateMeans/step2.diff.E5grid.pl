#!/usr/bin/env perl

# Note: mrso is used as ratio, so take the step3 to calculate it (Since it does not need teh intlevel logic here also).

# $model = shift; #"ACCESS-CM2";
$model = "ACCESS-CM2";

# $rootdir = "/pscratch/sd/x/xdchen/PS/PGW";
$rootdir = '/home/khanh/Documents/pgw/test/NCAR_ERA5_scripts';
`mkdir -p $rootdir/CMIP6_delta/E5/$model`;

if ($model eq "CESM2-WACCM" or $model eq "E3SM-1-1" or $model eq "NorESM2-LM") {
	@VarsSingle = ("hurs", "ps", "psl", "tas", "tos");
}
else {
	@VarsSingle = ("hurs", "uas", "vas", "ps", "psl", "tas", "tos");
}
@VarsAtmos = ("hur", "ta", "ua", "va", "zg");
@VarsSoil = ("tsl");


@VarsSoilRatio = ("mrso");

# debug
# @VarsSingle = ();
# @VarsAtmos = ();
# @VarsSoil = ();
# @VarsSoilRatio = ();

for $var(@VarsAtmos) {
	#$cmd = "cdo intlevel,10000,12500,15000,17500,20000,22500,25000,30000,35000,40000,45000,50000,55000,60000,65000,70000,75000,77500,80000,82500,85000,87500,90000,92500,95000,97500,100000 $rootdir/CMIP6_ERA5/$model/CMIP6.$model.historical.$var.E5grid.nc $rootdir/tmp/tmp.$model.$var.historical.atmos.nc";
	# 37 layers based on NCAR ds633.0
	$cmd = "cdo intlevel,100.00001,200,300,500,700,1000,2000,3000,5000,7000,10000,12500,15000,17500,20000,22500,25000,30000,35000,40000,45000,50000,55000,60000,65000,70000,75000,77500,80000,82500,85000,87500,90000,92500,95000,97500,100000 $rootdir/CMIP6_ERA5/$model/CMIP6.$model.historical.$var.E5grid.nc $rootdir/tmp/tmp.$model.$var.historical.atmos.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	# $cmd = "cdo intlevel,10000,12500,15000,17500,20000,22500,25000,30000,35000,40000,45000,50000,55000,60000,65000,70000,75000,77500,80000,82500,85000,87500,90000,92500,95000,97500,100000 $rootdir/CMIP6_ERA5/$model/CMIP6.$model.ssp585.$var.E5grid.nc $rootdir/tmp/tmp.$model.$var.ssp585.atmos.nc";
	# 37 layers based on NCAR ds633.0
	$cmd = "cdo intlevel,100.00001,200,300,500,700,1000,2000,3000,5000,7000,10000,12500,15000,17500,20000,22500,25000,30000,35000,40000,45000,50000,55000,60000,65000,70000,75000,77500,80000,82500,85000,87500,90000,92500,95000,97500,100000 $rootdir/CMIP6_ERA5/$model/CMIP6.$model.ssp585.$var.E5grid.nc $rootdir/tmp/tmp.$model.$var.ssp585.atmos.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncdiff $rootdir/tmp/tmp.$model.$var.ssp585.atmos.nc $rootdir/tmp/tmp.$model.$var.historical.atmos.nc $rootdir/CMIP6_delta/E5/$model/CMIP6.$model.diff.$var.E5grid.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "rm $rootdir/tmp/tmp.$model.$var.ssp585.atmos.nc $rootdir/tmp/tmp.$model.$var.historical.atmos.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";
}

for $var(@VarsSingle) {
	$cmd = "ncdiff $rootdir/CMIP6_ERA5/$model/CMIP6.$model.ssp585.$var.E5grid.nc $rootdir/CMIP6_ERA5/$model/CMIP6.$model.historical.$var.E5grid.nc $rootdir/CMIP6_delta/E5/$model/CMIP6.$model.diff.$var.E5grid.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";
}

for $var(@VarsSoil) {
	$cmd = "cdo intlevel,0.035,0.175,0.64,1.775 $rootdir/CMIP6_ERA5/$model/CMIP6.$model.historical.$var.E5grid.nc $rootdir/tmp/tmp.$model.historical.$var.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "cdo intlevel,0.035,0.175,0.64,1.775 $rootdir/CMIP6_ERA5/$model/CMIP6.$model.ssp585.$var.E5grid.nc $rootdir/tmp/tmp.$model.ssp585.$var.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncdiff $rootdir/tmp/tmp.$model.ssp585.$var.nc $rootdir/tmp/tmp.$model.historical.$var.nc $rootdir/CMIP6_delta/E5/$model/CMIP6.$model.diff.$var.E5grid.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "rm $rootdir/tmp/tmp.$model.ssp585.$var.nc $rootdir/tmp/tmp.$model.historical.$var.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";
}


for $var(@VarsSoilRatio) {

	$cmd = "cp $rootdir/CMIP6_ERA5/$model/CMIP6.$model.historical.mrso.E5grid.nc  $rootdir/tmp/$model.hist.mrso.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "cp $rootdir/CMIP6_ERA5/$model/CMIP6.$model.ssp585.mrso.E5grid.nc  $rootdir/tmp/$model.ssp585.mrso.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncrename -v mrso,mrsoh $rootdir/tmp/$model.hist.mrso.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncrename -v mrso,mrsof $rootdir/tmp/$model.ssp585.mrso.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncks -A $rootdir/tmp/$model.ssp585.mrso.nc $rootdir/tmp/$model.hist.mrso.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncap2 -s \"mrsoR=mrsof/mrsoh\" $rootdir/tmp/$model.hist.mrso.nc $rootdir/tmp/$model.out.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "ncks -v mrsoR $rootdir/tmp/$model.out.nc $rootdir/CMIP6_delta/E5/$model/CMIP6.$model.ratio.mrsoR.E5grid.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "rm $rootdir/tmp/$model.hist.mrso.nc $rootdir/tmp/$model.ssp585.mrso.nc $rootdir/tmp/$model.out.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

}
