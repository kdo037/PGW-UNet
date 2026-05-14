#!/usr/bin/env perl

# $model = shift; #"ACCESS-CM2";
$model = "ACCESS-CM2";
$rootdir = '/home/khanh/Documents/pgw/test/NCAR_ERA5_scripts';
`mkdir -p $rootdir/CMIP6_NARR/$model`;
`mkdir -p $rootdir/CMIP6_ERA5/$model`;
`mkdir -p $rootdir/CMIP6_G1/$model`;
`mkdir -p $rootdir/NAM/$model`;

if($model eq "CESM2-WACCM" or $model eq "E3SM-1-1" or $model eq "NorESM2-LM") {
	@vars_fill = ("hur", "ta", "ua", "va", "zg",  "hurs", "ps", "psl", "tas");
}
else {
	@vars_fill = ("hur", "ta", "ua", "va", "zg",  "hurs", "uas", "vas", "ps", "psl", "tas");
}
@vars_fill2 = ("mrso", "tsl", "tos");

# debug:
# @vars_fill = ();
# @vars_fill2 = ('mrso');

@periods = ("historical", "ssp585");

for $var(@vars_fill) {
		
	for $period(@periods) {

		# 1. fill missing values
		$cmd = "sed 's/<MODEL>/$model/g' mod_nc.$period.master.ncl | sed 's/<VAR>/$var/g' > mod_nc.$model.ncl";
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

		$cmd = "ncl -Q mod_nc.$model.ncl";
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


		# 2. ymonmean
		if($period eq "historical") {
			$cmd = "cdo ymonmean $rootdir/CMIP6_period/$model/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.nc $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo ymonmean $rootdir/CMIP6_period/$model/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.nc $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


		# 3. regrid to NARR grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NARR  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/CMIP6_NARR/$model/CMIP6.$model.$period.$var.NARRgrid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NARR  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/CMIP6_NARR/$model/CMIP6.$model.$period.$var.NARRgrid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


		# 4. regrid to ERA5 grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile_highres.ERA5_PugetSound  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/CMIP6_ERA5/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile_highres.ERA5_PugetSound  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/CMIP6_ERA5/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

		# 5. regrid to global 1x1 grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,global_1  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/CMIP6_G1/$model/CMIP6.$model.$period.$var.G1grid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,global_1  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/CMIP6_G1/$model/CMIP6.$model.$period.$var.G1grid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

		# 6. regrid to NAM grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NAM  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/NAM/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NAM  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/NAM/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	}

	# 5. clean
	$cmd = "rm mod_nc.$model.ncl $rootdir/tmp/CMIP6.r1i1p1f1.$model.historical.$var.1991-2020.ymonmean.nc $rootdir/tmp/CMIP6.r1i1p1f1.$model.ssp585.$var.2041-2070.ymonmean.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

}


for $var(@vars_fill2) {
		
	for $period(@periods) {

		# 1. ymonmean
		if($period eq "historical") {
			$cmd = "cdo ymonmean $rootdir/CMIP6_period/$model/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.nc $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo ymonmean $rootdir/CMIP6_period/$model/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.nc $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


		# 1.1 also fix the nodata value in mrso in selected models
		if($model eq "CanESM5" or $model eq "CMCC-CM2-SR5" or $model eq "E3SM-1-1" or $model eq "GFDL-ESM4" or $model eq "NorESM2-LM") {
			if($var eq "mrso") {
				$cmd = "sub_fix_mrso_nodata.py $model $period";
				print "$cmd\n";
				(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";
			}
		}

		# 2. fill missing values
		$cmd = "sed 's/<MODEL>/$model/g' mod_nc.$period.master2.ncl | sed 's/<VAR>/$var/g' > mod_nc.$model.ncl";
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

		$cmd = "ncl -Q mod_nc.$model.ncl";
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


		# 3. regrid to NARR grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NARR  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/CMIP6_NARR/$model/CMIP6.$model.$period.$var.NARRgrid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NARR  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/CMIP6_NARR/$model/CMIP6.$model.$period.$var.NARRgrid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


		# 4. regrid to ERA5 grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile_highres.ERA5_PugetSound  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/CMIP6_ERA5/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile_highres.ERA5_PugetSound  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/CMIP6_ERA5/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

		# 5. regrid to global 1x1 grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,global_1  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/CMIP6_G1/$model/CMIP6.$model.$period.$var.G1grid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,global_1  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/CMIP6_G1/$model/CMIP6.$model.$period.$var.G1grid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

		# 6. regrid to NAM grids
		if($period eq "historical") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NAM  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.1991-2020.ymonmean.nc $rootdir/NAM/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		elsif($period eq "ssp585") {
			$cmd = "cdo remapbil,$rootdir/calculateMeans/gridfile.NAM  $rootdir/tmp/CMIP6.r1i1p1f1.$model.$period.$var.2041-2070.ymonmean.nc $rootdir/NAM/$model/CMIP6.$model.$period.$var.E5grid.nc";
		}
		print "$cmd\n";
		(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";
	}

	# 5. clean
	$cmd = "rm mod_nc.$model.ncl $rootdir/tmp/CMIP6.r1i1p1f1.$model.historical.$var.1991-2020.ymonmean.nc $rootdir/tmp/CMIP6.r1i1p1f1.$model.ssp585.$var.2041-2070.ymonmean.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

}


