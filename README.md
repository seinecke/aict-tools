# aict-tools - CHEC Fork

## Data Input Format

The input hdf5 files include 3 tables: `telescope_events`, `array_events` and `runs`. The columns are described below.

`telescope_events`:
- `array_event_id`: The id of the event
- `run_id`: The id of the MC simulation run
- `intensity`: The total charge
- `x` [mm]: The x-coordinate of the Center of Gravity (mean of pixel coordinates weighted with pixel charge)
- `y` [mm]: The y-coordinate of the Center of Gravity (mean of pixel coordinates weighted with pixel charge)
- `psi` [rad]: Angle between `length` and x-axis
- `r` [deg]: Center of Gravity in polar coordinates
- `phi` [rad]: Center of Gravity in polar coordinates
- `length` [deg]: Eigen value of PCA
- `width` [deg]: Eigen value of PCA
- `skewness` [deg]: The 3rd moment along the major axis
- `kurtosis` [deg]: The 4th moment along the major axis


`array_events`:
- `array_event_id`: The  of the event
- `altitude_raw` [rad]: Telescope pointing altitude
- `azimuth_raw` [rad]: Telescope pointing azimuth
- `mc_alt` [rad]: True source position (altitude)
- `mc_az` [rad]: True source position (azimuth)
- `mc_core_x` [m]: True core position (x-coordinate)
- `mc_core_y` [m]: True core position (x-coordinate)
- `mc_energy` [TeV]: True energy
- `mc_h_first_int` [m]: True height of first interaction
- `mc_x_max [m]`: Height of the shower maximum
- `shower_primary_id`: Id of the primary incident (0: gamma)
- `t_cpu`

`runs`:
- `atmosphere'
- `core_pos_mode`
- `corsika_bunchsize`
- `corsika_high_E_detail`
- `corsika_high_E_model`
- `corsika_iact_options`
- `corsika_low_E_detail`
- `corsika_low_E_model`
- `corsika_version`
- `corsika_wlen_max`
- `corsika_wlen_min`
- `detector_prog_id`
- `detector_prog_start`
- `diffuse`
- `energy_range_max [TeV]`
- `energy_range_min [TeV]`
- `injection_height`
- `max_alt`
- `max_az`
- `max_scatter_range`
- `max_viewcone_radius`
- `min_alt`
- `min_az`
- `min_scatter_range`
- `min_viewcone_radius`
- `num_showers`
- `prod_site_B_declination`
- `prod_site_B_inclination`
- `prod_site_B_total`
- `prod_site_alt`
- `run_id`
- `shower_prog_id`
- `shower_prog_start`
- `shower_reuse`
- `simtel_version`
- `spectral_index`
