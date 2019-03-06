# aict-tools - CHEC Fork

## Data Input Format

The input hdf5 files include 3 tables: `telescope_events`, `array_events` and `runs`. The columns are described below.

`telescope_events`:
- `array_event_id`: The id of the event
- `run_id`: 
- `intensity`: The total charge
- `skewness`: The 3rd moment along the major axis
- `kurtosis`: The 4th moment along the major axis
- `length` [deg]: The 2nd moment along the major axis
- `width` [deg]: The 2nd moment along the minor axis
- `x` [mm]: The x-coordinate of the Center of Gravity
- `y` [mm]: The y-coordinate of the Center of Gravity
- `psi`: Angle between `length` and x-axis
- `r`: Center of Gravity in polar coordinates
- `phi`: Center of Gravity in polar coordinates


`array_events`:
- `array_event_id`: The id of the event
- `altitude_raw`:
- `azimuth_raw`
- `mc_alt`
- `mc_az`
- `mc_core_x`
- `mc_core_y`
- `mc_energy`
- `mc_h_first_int`
- `mc_x_max`
- `shower_primary_id`
- `t_cpu`

`runs`:
- `atmosphere
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
- `energy_range_max`
- `energy_range_min`
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
