import click
import yaml
import h5py
import logging
import pandas as pd

from fact.io import h5py_get_n_rows, read_data, write_data
from ..apply import create_mask_h5py, apply_cuts_h5py_chunked


@click.command()
@click.argument('configuration_path', 
                type=click.Path(exists=True, dir_okay=False))
@click.argument('input_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', type=click.Path(exists=False, dir_okay=False))
@click.option('-k', '--key', help='Name of the hdf5 group', default='telescope_events')
@click.option('-v', '--verbose', help='Verbose log output', is_flag=True)
def main(configuration_path, input_path, output_path, chunksize, key, verbose):
    '''
    Apply cuts given in CONFIGURATION_PATH to the data in INPUT_PATH and
    write the result to OUTPUT_PATH.

    example:
    ```
    selection:
        length:
          - '<'
          - 0.06
    ```
    '''
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    log = logging.getLogger()

    with open(configuration_path) as f:
        config = yaml.safe_load(f)

    selection = config.get('selection', {})

    array_events = read_data(input_path, key='array_events')
    telescope_events = read_data(input_path, key='telescope_events')

    mask_telescope = create_mask_h5py(input_path, selection, key='telescope_events')
    selected_telescope_events = telescope_events[mask_telescope]

    array_events['idx'] = array_events.index
    merge = pd.merge(
        selected_telescope_events[['run_id', 'array_event_id']], 
        array_events[['run_id', 'array_event_id', 'idx']],
        on=['run_id', 'array_event_id'],
        how='left')
    selected_array_events = array_events[array_events.idx.isin(merge.idx)]

    write_data(selected_telescope_events, output_path, key='telescope_events', 
                use_h5py=True, mode='w')
    write_data(selected_array_events, output_path, key='array_events', 
                    use_h5py=True, mode='a')

    with h5py.File(input_path, mode='r') as infile, h5py.File(output_path, 'r+') as outfile:
        if 'runs' in infile.keys():
            log.info('Copying runs group to outputfile')
            infile.copy('/runs', outfile['/'])

