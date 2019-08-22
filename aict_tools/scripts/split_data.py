import click
import numpy as np
import logging

from fact.io import read_data, write_data
import warnings
from math import ceil

log = logging.getLogger()


def split_indices(idx, n_total, fractions):
    '''
    splits idx containing n_total distinct events into fractions given in fractions list.
    returns the number of events in each split
    '''
    num_ids = [ceil(n_total * f) for f in fractions]
    if sum(num_ids) > n_total:
        num_ids[-1] -= sum(num_ids) - n_total
    return num_ids


@click.command()
@click.argument('input_path', type=click.Path(exists=True, file_okay=True))
@click.argument('output_basename')
@click.option('--fraction', '-f', multiple=True, type=float,
                help='Fraction of events to use for this part')
@click.option('--name','-n', multiple=True, help='name for one dataset')
@click.option('-i', '--inkey', help='HDF5 key for h5py hdf5 of the input file',
              default='events', show_default=True)
@click.option('--key', '-k', help='Name for the hdf5 group in the output',
              default='events', show_default=True)
@click.option('--telescope', '-t', type=click.Choice(['fact', 'cta']), 
             default='cta', show_default=True, 
             help='Which telescope created the data')
@click.option('--fmt', type=click.Choice(['csv', 'hdf5', 'hdf', 'h5']), 
              default='hdf5', show_default=True, help='The output format')
@click.option('-s', '--seed', help='Random Seed', type=int, default=0, show_default=True)
@click.option('-v', '--verbose', is_flag=True, help='Verbose log output',)
def main(input_path, output_basename, fraction, name, inkey, key, telescope, 
         fmt, seed, verbose):
    '''
    Split dataset in INPUT_PATH into multiple parts for given fractions and names
    Outputs hdf5 or csv files to OUTPUT_BASENAME_NAME.FORMAT

    Example call: klaas_split_data input.hdf5 output_base -n test -f 0.5 -n train -f 0.5
    '''

    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    log.debug("input_path: {}".format(input_path))

    np.random.seed(seed)

    split_telescope_data(input_path, output_basename, fraction, name)


def split_telescope_data(input_path, output_basename, fraction, name):

    array_events = read_data(input_path, key='array_events')
    telescope_events = read_data(input_path, key='telescope_events')
    runs = read_data(input_path, key='runs')

    # split by runs
    ids = set(runs.run_id)
    log.debug(f'All runs:{ids}')
    n_total = len(ids)

    log.info(f'Found a total of {n_total} runs in the file')
    num_runs = split_indices(ids, n_total, fractions=fraction)

    for n, part_name in zip(num_runs, name):
        selected_run_ids = np.random.choice(list(ids), size=n, replace=False)
        selected_runs = runs[runs.run_id.isin(selected_run_ids)]
        selected_array_events = array_events[array_events.run_id.isin(selected_run_ids)]
        selected_telescope_events = telescope_events[telescope_events.run_id.isin(selected_run_ids)]

        path = output_basename + '_' + part_name + '.hdf5'
        log.info('Writing {} runs events to: {}'.format(n, path))
        write_data(selected_runs, path, key='runs', use_h5py=True, mode='w')
        write_data(selected_array_events, path, key='array_events', 
                    use_h5py=True, mode='a')
        write_data(selected_telescope_events, path, key='telescope_events', 
                    use_h5py=True, mode='a')
        log.debug(f'selected runs {set(selected_run_ids)}')
        log.debug(f'Runs minus selected runs {ids - set(selected_run_ids)}')
        ids = ids - set(selected_run_ids)

