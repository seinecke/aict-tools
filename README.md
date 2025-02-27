# aict-tools - CHEC Fork

## Installation

Pre-requisities: ctapipe (development version)

```
source activate cta-dev
pip install pyfact
git clone https://github.com/seinecke/aict-tools.git
cd aict-tools
pip install -e .
```

## Configuration

Download `Makefile`, `configs/chec_mono.yml` and `matplotlibrc` from https://github.com/cta-chec/CHECOnskySB/tree/master/CHECOnskySB/scripts/sabrina/d190228_analysis_chec and store them in the same folder (preferably not in `aict-tools`).

## Pre-Processing

It is assumed that you have files that have been processed with `extract_dl1.py`, `extract_hillas.py`, `merge_hillas.py` and `convert_hillas.py`. 
If not, check here: https://github.com/cta-chec/CHECOnskySB/tree/master/CHECOnskySB/scripts

## Processing

Adapt `build_dir` and `data_dir` paths in the `Makefile`.
Go to the folder where the `Makefile` is stored and type: 
```
source activate cta-dev
make
```
Check your `build_dir` for created plots, files and models ;-)


## Post-Processing

If you are interested in the performance of your analysis, check here: https://github.com/cta-chec/CHECOnskySB/tree/master/CHECOnskySB/scripts/sabrina/d190301_performance


## Data Input Format

The input hdf5 files include 3 tables: `telescope_events`, `array_events` and `runs`. The columns are described below.

`telescope_events`:
(The following features need to be in the file in the specified units)
- `array_event_id`: The id of the event
- `run_id`: The id of the MC simulation run
- `altitude_raw` [rad]: Telescope pointing altitude
- `azimuth_raw` [rad]: Telescope pointing azimuth
- `true_source_alt` [rad]: True source position (altitude)
- `true_source_az` [rad]: True source position (azimuth)
- `x` [m]: The x-coordinate of the Center of Gravity (mean of pixel coordinates weighted with pixel charge)
- `y` [m]: The y-coordinate of the Center of Gravity (mean of pixel coordinates weighted with pixel charge)
- `intensity`: The total charge

(The following features are not mandatory)
- `psi` [rad]: Angle between `length` and x-axis
- `r` [m]: Center of Gravity in polar coordinates
- `phi` [rad]: Center of Gravity in polar coordinates
- `length` [m]: Eigen value of PCA
- `width` [m]: Eigen value of PCA
- `skewness`: The 3rd moment along the major axis
- `kurtosis`: The 4th moment along the major axis
- `nislands`: Number of islands that survived image cleaning
- `n_survived_pixels`: Number of pixels that survived image cleaning
- `leakage1_intensity`: Ratio between charge in the outer ring of the camera and total charge
- `leakage1_pixel`: Ratio between number of pixels in the outer ring of the camera and number of survived pixels
- `leakage2_intensity`: Ratio between charge in the 2 outer rings of the camera and total charge
- `leakage2_pixel`: Ratio between number of pixels in the 2 outer rings of the camera and number of survived pixels
- `concentration_1`: Ratio between highest charge and total charge
- `concentration_2`: Ratio between 2 highest charges and total charge
- `concentration_3`: Ratio between 3 highest charges and total charge
- `tdeviation` [?]:
- `tduration` [ns]: Duration between minimum and maximum extracted time of survived pixels
- `tgradient` [?}:


`array_events`:
- `array_event_id`: The id of the event
- `mc_core_x` [m]: True core position (x-coordinate)
- `mc_core_y` [m]: True core position (y-coordinate)
- `mc_energy` [TeV]: True energy
- `mc_h_first_int` [m]: True height of first interaction
- `mc_x_max [m]`: Height of the shower maximum
- `shower_primary_id`: Id of the primary incident (0: gamma)
- `t_cpu`

`runs`:
- `atmosphere`
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


## Data Output Format

The output hdf5 files include 3 tables: `telescope_events`, `array_events` and `runs`. The columns are the same as of the input PLUS the following:

`telescope_events`:
- `disp` [m]: Distance between CoG and predicted source position
- `source_x` [m]: Predicted source position in camera coordinates (x-coordinate)
- `source_y` [m]: Predicted source position in camera coordinates (y-coordinate)
- `source_alt` [rad]: Predicted source position (altitude)
- `source_az` [rad]: Predicted source position (azimuth)
- `energy [TeV]`: Predicted energy
- `gamma_score`: Predicted score of being a gamma-ray event


`array_events`:
- `energy_mean` [TeV]: Mean (over multiple telescopes) of the predicted energy
- `energy_std`: Standard deviation (over multiple telescopes) of the predicted energy
- `gamma_score_mean`: Mean (over multiple telescopes) of the predicted gamma score
- `source_alt_mean` [rad]: Mean (over multiple telescopes) of the predicted source position
- `source_az_mean` [rad]: Mean (over multiple telescopes) of the predicted source position

## Validation Output Format

In addition, hdf5 files containing data for the validation of the models are stored. For each reconstruction task, one files is created.
The output hdf5 files include ?? tables: `data`. The columns are described below.

`aict_predictions_gh.hdf5`:
- `cv_fold`: Index of the cross validation
- `label`: True label (0: background, 1: signal)
- `label_prediction`: Predicted label, assuming a threshold of 0.5 (0: background, 1: signal)
- `probabilities`: Score of being signal (related to probability)

`aict_predictions_energy.hdf5`:
- `cv_fold`: Index of the cross validation
- `label` [TeV]: True energy
- `label_prediction` [TeV]: Predicted energy

`aict_predictions_direction.hdf5`:
- `cv_fold`: Index of the cross validation
- `disp` [mm]: True disp
- `disp_prediction` [mm]: Predicted disp
- `mc_energy` [TeV]: True energy
- `sign`: True sign
- `sign_prediction`: Predicted sign (assuming threshold 0.5)
- `sign_probabilities`: Score of being plus sign (related to probability)

