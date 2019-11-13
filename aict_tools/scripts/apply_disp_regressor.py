import click
import numpy as np
import pandas as pd
from sklearn.externals import joblib
import logging
import h5py
from tqdm import tqdm

from ..io import append_to_h5py, read_telescope_data_chunked
from ..apply import predict_disp
from ..configuration import AICTConfig
from ..preprocessing import camera_to_horizontal

from fact.io import read_data


@click.command()
@click.argument('configuration_path', 
                type=click.Path(exists=True, dir_okay=False))
@click.argument('data_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('disp_model_path', type=click.Path(exists=False, dir_okay=False))
@click.argument('sign_model_path', type=click.Path(exists=False, dir_okay=False))
@click.option('-n', '--n-jobs', type=int, help='Number of cores to use')
@click.option('-y', '--yes', help='Do not prompt for overwrites', is_flag=True)
@click.option('-v', '--verbose', help='Verbose log output', is_flag=True)
@click.option(
    '-N', '--chunksize', type=int,
    help='If given, only process the given number of events at once',
)
@click.option('-c', '--column_name', help='Name of column to be added', 
              default='disp')
def main(configuration_path, data_path, disp_model_path, sign_model_path, 
         chunksize, n_jobs, yes, verbose, column_name):
    '''
    Apply given model to data. 
    Columns specifying the predicted source position (in camera coordinates 
    and in AltAz) and the prdicted distance between the CoG and the predicted
    source position are added to the file.

    CONFIGURATION_PATH: Path to the config yaml file
    DATA_PATH: path to the CTA data in a h5py hdf5 file
    DISP_MODEL_PATH: Path to the pickled disp model.
    SIGN_MODEL_PATH: Path to the pickled sign model.
    '''
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    log = logging.getLogger()

    config = AICTConfig.from_yaml(configuration_path)
    model_config = config.disp

    columns_to_delete = [
        'source_x',
        'source_y',
        'source_alt',
        'source_az',
        'source_alt_mean',
        'source_az_mean',
        'disp',
        'theta',
        'theta_deg',
        'theta_rec_pos',
    ]
    for i in range(1, 6):
        columns_to_delete.extend([
            'theta_off_' + str(i),
            'theta_deg_off_' + str(i),
            'theta_off_rec_pos_' + str(i),
        ])

    n_del_cols = 0
    with h5py.File(data_path, 'r+') as f:
        for column in columns_to_delete:

            if column in f[config.array_events_key].keys():
                if not yes:
                    click.confirm(
                        'Dataset "{}" exists in file, overwrite?'.format(column),
                        abort=True,
                    )
                    yes = True
                del f[config.array_events_key][column]
                log.warn("Deleted {} from the feature set.".format(column))
                n_del_cols += 1

            if column in f[config.telescope_events_key].keys():
                if not yes:
                    click.confirm(
                        'Dataset "{}" exists in file, overwrite?'.format(column),
                        abort=True,
                    )
                    yes = True
                del f[config.telescope_events_key][column]
                log.warn("Deleted {} from the feature set.".format(column))
                n_del_cols += 1

    if n_del_cols > 0:
        log.warn("Source dependent features need to be calculated from the predicted source possition. "
                 + "Use e.g. `fact_calculate_theta` from https://github.com/fact-project/pyfact.")

    log.info('Loading model')
    disp_model = joblib.load(disp_model_path)
    sign_model = joblib.load(sign_model_path)
    log.info('Done')

    if n_jobs:
        disp_model.n_jobs = n_jobs
        sign_model.n_jobs = n_jobs

    # Add focal_length to be read for coordinate transformation
    columns = model_config.columns_to_read_apply
    columns.append('focal_length')
    columns.append('run_id')
    columns.append('array_event_id')

    df_generator = read_telescope_data_chunked(
        data_path, config, chunksize, columns,
        feature_generation_config=model_config.feature_generation
    )

    log.info('Predicting on data...')

    chunked_frames = []

    for df_data, start, end in tqdm(df_generator):

        disp = predict_disp(
            df_data[model_config.features], disp_model, sign_model
        )

        source_x = ( df_data[model_config.cog_x_column] 
                    + disp * np.cos(df_data[model_config.delta_column]) )
        source_y = ( df_data[model_config.cog_y_column] 
                    + disp * np.sin(df_data[model_config.delta_column]) )

        source_alt, source_az = camera_to_horizontal(
                        x=source_x, y=source_y,
                        az_pointing=df_data[model_config.pointing_az_column],
                        alt_pointing=df_data[model_config.pointing_alt_column],
                        focal_length=df_data['focal_length'])

        d = df_data[['run_id', 'array_event_id']].copy()
        d['source_alt'] = source_alt
        d['source_az'] = source_az
        chunked_frames.append(d)

        with h5py.File(data_path, 'r+') as f:
            append_to_h5py(f, source_x, config.telescope_events_key, 'source_x')
            append_to_h5py(f, source_y, config.telescope_events_key, 'source_y')
            append_to_h5py(f, source_alt, config.telescope_events_key, 'source_alt')
            append_to_h5py(f, source_az, config.telescope_events_key, 'source_az')
            append_to_h5py(f, disp, config.telescope_events_key, column_name)

            # if config.has_multiple_telescopes == False:
            #     append_to_h5py(f, source_alt, config.array_events_key, 'source_alt_mean')
            #     append_to_h5py(f, source_az, config.array_events_key, 'source_az_mean')

    d = pd.concat(chunked_frames).groupby(
            ['run_id', 'array_event_id'], sort=False
        ).agg(['mean', 'std'])

    mean_alt = d['source_alt']['mean'].values
    mean_az = d['source_az']['mean'].values
    std_alt = d['source_alt']['std'].values
    std_az = d['source_az']['std'].values

    with h5py.File(data_path, 'r+') as f:
        append_to_h5py(f, mean_alt, config.array_events_key, 'source_alt_mean')
        append_to_h5py(f, mean_az, config.array_events_key, 'source_az_mean')
        append_to_h5py(f, std_alt, config.array_events_key, 'source_alt_std') 
        append_to_h5py(f, std_az, config.array_events_key, 'source_az_std')            



if __name__ == '__main__':
    main()
