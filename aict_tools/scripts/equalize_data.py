import click
import numpy as np
import pandas as pd
import logging

from fact.io import read_data, write_data
import warnings
from math import ceil

from ..configuration import AICTConfig

log = logging.getLogger()

@click.command()
@click.argument('configuration_path', 
                type=click.Path(exists=True, dir_okay=False))
@click.argument('input_path1', type=click.Path(exists=True, file_okay=True))
@click.argument('input_path2', type=click.Path(exists=True, file_okay=True))
@click.argument('output_path1')
@click.argument('output_path2')
#@click.option('--features', '-f', multiple=True,
#                help='Feature to be equalized')
#@click.option('--bins', '-b', multiple=True, type=float,
#                help='Number of bins of the feature')

def main(configuration_path, input_path1, input_path2, output_path1, output_path2): #features, bins):
    '''
    Equalize two datasets in INPUT_PATH1 and INPUT_PATH2 in the feature `intensity`.
    In case of multiple telescopes, the feature is averaged.
    Outputs hdf5 files to OUTPUT_BASENAME_NAME.FORMAT

    Important remark: No run information is stored in the output file,
    since it is no longer valid due to sampling. Therefore, these output files
    should only be used for training. 

    '''

    config = AICTConfig.from_yaml(configuration_path)

    array_events1 = read_data(input_path1, key='array_events')
    array_events1['arr_id_unique'] = array_events1.index
    telescope_events1 = read_data(input_path1, key='telescope_events')
    telescope_events1['tel_id_unique'] = telescope_events1.index
    df1 = pd.merge(array_events1, telescope_events1,
        on=['run_id', 'array_event_id'], how='left')

    array_events2 = read_data(input_path2, key='array_events')
    array_events2['arr_id_unique'] = array_events2.index
    telescope_events2 = read_data(input_path2, key='telescope_events')
    telescope_events2['tel_id_unique'] = telescope_events2.index
    df2 = pd.merge(array_events2, telescope_events2,
        on=['run_id', 'array_event_id'])

    print('Number of events before: ', 
        '\nFile 1: ', len(array_events1), 
        '\nFile 2: ', len(array_events2))

    if config.has_multiple_telescopes:
        feature = 'average_intensity'
    else:
        feature = 'intensity'

    minimum = np.min([np.nanmin(df1[feature]), np.nanmin(df2[feature])])
    maximum = np.max([np.nanmax(df1[feature]), np.nanmax(df2[feature])])

    minimum_log = np.log10(minimum)
    maximum_log = np.log10(maximum)

    binning = np.logspace(minimum_log, maximum_log, int((maximum_log - minimum_log)/0.05) )

    arr_ids1 = np.array([])
    arr_ids2 = np.array([])

    for start, end in zip(binning[:-1], binning[1:]):

        ids1 = df1[(df1[feature] > start) & (df1[feature] < end)].arr_id_unique
        ids2 = df2[(df2[feature] > start) & (df2[feature] < end)].arr_id_unique


        if len(ids1) < len(ids2):
            arr_ids1 = np.append(arr_ids1, ids1)
            arr_ids2 = np.append(arr_ids2, np.random.choice(ids2, size=len(ids1), replace=False))

        else:
            arr_ids2 = np.append(arr_ids2, ids2)
            arr_ids1 = np.append(arr_ids1, np.random.choice(ids1, size=len(ids2), replace=False))
        
    print('Number of events after: ', 
        '\nFile 1: ', len(arr_ids1), 
        '\nFile 2: ', len(arr_ids2))

    tel_ids1 = df1[df1.arr_id_unique.isin(arr_ids1)].tel_id_unique
    selected_telescope_events1 = telescope_events1[telescope_events1.tel_id_unique.isin(tel_ids1)]
    selected_telescope_events1.drop(columns=['tel_id_unique'], inplace=True)
    write_data(selected_telescope_events1, output_path1, key='telescope_events', 
                use_h5py=True, mode='w')
    selected_array_events1 = array_events1[array_events1.arr_id_unique.isin(arr_ids1)]
    selected_array_events1.drop(columns=['arr_id_unique'], inplace=True)
    write_data(array_events1, output_path1, key='array_events', 
                    use_h5py=True, mode='a')

    tel_ids2 = df2[df2.arr_id_unique.isin(arr_ids2)].tel_id_unique
    selected_telescope_events2 = telescope_events2[telescope_events2.tel_id_unique.isin(tel_ids2)]
    selected_telescope_events2.drop(columns=['tel_id_unique'], inplace=True)
    write_data(selected_telescope_events2, output_path2, key='telescope_events', 
                use_h5py=True, mode='w')
    selected_array_events2 = array_events2[array_events2.arr_id_unique.isin(arr_ids2)]
    selected_array_events2.drop(columns=['arr_id_unique'], inplace=True)
    write_data(array_events2, output_path2, key='array_events', 
                    use_h5py=True, mode='a')


