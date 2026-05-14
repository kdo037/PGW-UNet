#!/usr/bin/perl

$startdate = shift; #(YYYY-MM-DD)
$enddate = shift; #(YYYY-MM-DD)

$script_name = "/home/khanh/Documents/pgw/test/PGW.ERA5/Add_CMIP6_perturbation_to_ERA5.slev.py";

@month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

($startyear,$startmonth,$startday) = split /-/, $startdate;
($endyear,$endmonth,$endday) = split /-/, $enddate;

$year = $startyear;
$month = $startmonth;
$day = $startday;


while ($year < $endyear || ($year == $endyear && ($month < $endmonth || ($month == $endmonth && $day <= $endday) ) ) ) {

	$year = sprintf "%04d", $year;
	$month = sprintf "%02d", $month;
	$day = sprintf "%02d", $day;

	print "\n$year  $month  $day\n";

	$file_in_grib = sprintf "/home/khanh/Documents/pgw/test/ERA5_download_from_CDS/ERA5.slev.%d.%02d.%02d.grib", $year, $month, $day;
	$file_in_nc = sprintf "/home/khanh/Documents/pgw/test/ERA5_download_from_CDS/ERA5.%d.%02d.%02d.slev.nc", $year, $month, $day;
	$file_pert_nc = sprintf "/home/khanh/Documents/pgw/test/ERA5_download_from_CDS/ERA5.%d.%02d.%02d.slev.pert.nc", $year, $month, $day;
	$file_pert_grib = sprintf "/home/khanh/Documents/pgw/test/ERA5_download_from_CDS/ERA5.%d.%02d.%02d.slev.grib", $year, $month, $day;


	# 1. convert to nc
	$cmd = "cdo -f nc copy $file_in_grib $file_in_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 2. copy file
	$cmd = "cp $file_in_nc $file_pert_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 3. modify the file
	$cmd = "$script_name $file_pert_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 4. convert back to grib
	$cmd = "cdo -f grb copy $file_pert_nc $file_pert_grib";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";


	# 5. clean
	$cmd = "rm $file_in_nc $file_pert_nc";
	print "$cmd\n";
	(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";



	$day++;
	$days_in_month = @month_days[$month-1];
	if (($year % 400 == 0 || ($year%4==0 && $year%100!=0)) && $month == 2) {
		$days_in_month++;
	}
	if ($day > $days_in_month) {
		$day = 1;
		$month++;
		if ($month > 12) {
			$month = 1;
			$year++;
		}
	}

}
