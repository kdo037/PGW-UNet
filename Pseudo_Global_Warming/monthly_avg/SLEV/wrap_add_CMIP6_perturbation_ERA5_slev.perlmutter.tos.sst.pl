#!/usr/bin/perl

$startdate = shift; #(YYYY-MM-DD)
$enddate = shift; #(YYYY-MM-DD)

$script_name = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/Add_CMIP6_perturbation_to_ERA5.slev.tos.sst.py";

@month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

($startyear,$startmonth,$startday) = split /-/, $startdate;
($endyear,$endmonth,$endday) = split /-/, $enddate;

$year = $startyear;
$month = $startmonth;
$day = $startday;


while ($year < $endyear || ($year == $endyear && ($month < $endmonth || ($month == $endmonth && $day <= $endday) ) ) ) {

	if ($month == 1 || $month == 3 || $month == 5 || $month == 7 || $month == 8 || $month == 10 || $month == 12){
		$dd = 31;
	}elsif ($month == 2) {
			if (($year % 400 == 0 || ($year%4==0 && $year%100!=0)) && $month == 2) {
					$dd = 29;
			}
			else{
					$dd = 28;
			}
	}else{
			$dd = 30;
	}

	$year = sprintf "%04d", $year;
	$month = sprintf "%02d", $month;
	$day = sprintf "%02d", $day;

	print "\n$year  $month  $day\n";

	$file_in_grib = sprintf "/glade/derecho/scratch/kdo/gcm_downscale/PGW/ERA5_Data/SFC/e5.oper.an.sfc.128_034_sstk.ll025sc.%d%02d%02d00_%d%02d%02d23.grb", $year, $month, $day, $year, $month, $dd;
	$file_in_nc = sprintf "/glade/derecho/scratch/kdo/gcm_downscale/PGW/ERA5_Data/SFC/tmp_nc/e5.oper.an.sfc.128_034_sstk.ll025sc.%d%02d%02d00_%d%02d%02d23.nc", $year, $month, $day, $year, $month, $dd;
	$file_pert_nc = sprintf "/glade/derecho/scratch/kdo/gcm_downscale/PGW/ERA5_Data/SFC/tmp_nc/e5.oper.an.sfc.128_034_sstk.ll025sc.%d%02d%02d00_%d%02d%02d23.pert.nc", $year, $month, $day, $year, $month, $dd;
	$file_pert_grib = sprintf "/glade/derecho/scratch/kdo/gcm_downscale/PGW/ERA5_Data/SFC/pert_grib/e5.oper.an.sfc.128_034_sstk.ll025sc.%d%02d%02d00_%d%02d%02d23.grb", $year, $month, $day, $year, $month, $dd;


	# 1. convert to nc
	$cmd = "cdo -f nc copy $file_in_grib $file_in_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 2. copy file
	$cmd = "cp $file_in_nc $file_pert_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 3. modify the file
	$cmd = "python $script_name $file_pert_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 4. convert back to grib
	$cmd = "cdo -f grb copy $file_pert_nc $file_pert_grib";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# # 5. clean
	# $cmd = "rm $file_in_nc $file_pert_nc";
	# print "$cmd\n";
	# (system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

	$month++;
	if ($month > 12) {
			$month = 1;
			$year++;
	}

}
