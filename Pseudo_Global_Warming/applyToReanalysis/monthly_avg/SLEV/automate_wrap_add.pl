#!/usr/bin/perl

# this script automates add perterbation to all required variables for SLEV and 3D
# example: perl automate_wrap_add.pl 2019-05-01 2022-12-31

$startdate = shift; #(YYYY-MM-DD)
$enddate = shift; #(YYYY-MM-DD)

# Single layer elevation (SLEV) ---------------------

$script_dt_2d = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.dt.2d.pl";
$script_mrsoR_swvl = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.mrsoR.swvl.pl";
$script_ps_sp = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.ps.sp.pl";
$script_psl_msl = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.psl.msl.pl";
$script_tas_2t = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.tas.2t.pl";
$script_tos_skt = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.tos.skt.pl";
$script_tos_sst = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.tos.sst.pl";
$script_tsl_stl = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.tsl.stl.pl";
$script_uas_10u = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.uas.10u.pl";
$script_vas_10v = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/SLEV/wrap_add_CMIP6_perturbation_ERA5_slev.perlmutter.vas.10v.pl";

# run scripts
$cmd = "perl $script_tas_2t $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_dt_2d $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_mrsoR_swvl $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_ps_sp $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_psl_msl $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_tos_skt $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_tos_sst $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_tsl_stl $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_uas_10u $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_vas_10v $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

# 3-D -----------------------------------------------

$script_hur = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/3D/wrap_add_CMIP6_perturbation_ERA5_3D.perlmutter.hur.pl";
$script_ta = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/3D/wrap_add_CMIP6_perturbation_ERA5_3D.perlmutter.ta.pl";
$script_ua = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/3D/wrap_add_CMIP6_perturbation_ERA5_3D.perlmutter.ua.pl";
$script_va = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/3D/wrap_add_CMIP6_perturbation_ERA5_3D.perlmutter.va.pl";
$script_zg = "/glade/derecho/scratch/kdo/gcm_downscale/PGW/NCAR_ERA5_scripts/applyToReanalysis/monthly_avg/3D/wrap_add_CMIP6_perturbation_ERA5_3D.perlmutter.zg.pl";

# run scripts
$cmd = "perl $script_hur $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_ta $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_ua $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_va $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";

$cmd = "perl $script_zg $startdate $enddate";
print "$cmd\n";
(system($cmd)==0) or die "$0: ERROR: $cmd failed\n";