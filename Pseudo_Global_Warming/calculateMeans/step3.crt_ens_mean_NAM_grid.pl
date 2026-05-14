#!/usr/bin/env perl

# Note: run sub_fix.bf_step3.mrso_in_MPI.py before this script!

# $grid = shift; # "NARR" or "E5"
$grid = "E5";

$rootdir = "/home/khanh/Documents/pgw/test/NCAR_ERA5_scripts";
`mkdir -p $rootdir/CMIP6_delta/ens_mean/$grid`;

@VarsDiff = ("hur", "ta", "ua", "va", "zg", "hurs", "tas", "uas", "vas", "ps", "psl", "tos", "tsl", "mrsoR");
# debug
# @VarsDiff = ("tsl");

for $var(@VarsDiff) {

	$cmd = "ncecat $rootdir/CMIP6_delta/$grid/*/CMIP6.*.$var.${grid}grid.nc  $rootdir/tmp/tmp.ens.$var.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	if($var eq "mrsoR") {
		$cmd = "ncwa -a record $rootdir/tmp/tmp.ens.$var.nc $rootdir/CMIP6_delta/ens_mean/$grid/CMIP6.ens_mean.ratio.$var.${grid}grid.nc";
	}
	else {
		$cmd = "ncwa -a record $rootdir/tmp/tmp.ens.$var.nc $rootdir/CMIP6_delta/ens_mean/$grid/CMIP6.ens_mean.diff.$var.${grid}grid.nc";
	}
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$cmd = "rm $rootdir/tmp/tmp.ens.$var.nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

}