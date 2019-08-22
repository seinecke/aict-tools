import click
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.externals import joblib
from ..configuration import AICTConfig
import fact.io

from ..plotting import (
    plot_regressor_confusion,
    plot_bias_resolution,
    plot_bias,
    plot_resolution,
    plot_feature_importances,
)


@click.command()
@click.argument('configuration_path', 
                type=click.Path(exists=True, dir_okay=False))
@click.argument('performance_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('model_path', type=click.Path(exists=True, dir_okay=False))
@click.option('-o', '--output', type=click.Path(exists=False, dir_okay=False))
@click.option('-k', '--key', help='HDF5 key for hdf5', default='data')
def main(configuration_path, performance_path, model_path, output, key):
    ''' Create some performance evaluation plots for the separator '''
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()

    log.info('Loading perfomance data')
    df = fact.io.read_data(performance_path, key=key)

    log.info('Loading model')
    model = joblib.load(model_path)

    config = AICTConfig.from_yaml(configuration_path)
    model_config = config.x_max
    figures = []

    # Plot confusion
    figures.append(plt.figure())
    ax = figures[-1].add_subplot(1, 1, 1)
    ax = plot_regressor_confusion(df, ax=ax, 
                label='x_max', pred='x_max_prediction')

    ax.set_xlabel(r'$Xmax_{\mathrm{true}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_ylabel(r'$Xmax_{\mathrm{rec}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')


    # Plot confusion for different energies
    figures.append(plt.figure())
    ax = figures[-1].add_subplot(2, 2, 1)
    ax = plot_regressor_confusion(df[df[config.energy.target_column]<2], 
        ax=ax, log_xy=False, label='x_max', pred='x_max_prediction')
    ax.set_ylabel(r'$Xmax_{\mathrm{rec}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_xlim([200,700])
    ax.set_ylim([200,700])
    ax.plot([0,700], [0,700], color='#D03A3B', alpha=0.5)
    ax.text(0.1,0.9,'< 2 TeV', fontsize=8,
        transform=ax.transAxes, horizontalalignment='left')

    ax = figures[-1].add_subplot(2, 2, 2)
    ax = plot_regressor_confusion(df[(df[config.energy.target_column]>2) 
        & (df[config.energy.target_column]<10)], 
        ax=ax, log_xy=False, label='x_max', pred='x_max_prediction')
    ax.set_xlim([200,700])
    ax.set_ylim([200,700])
    ax.plot([0,700], [0,700], color='#D03A3B', alpha=0.5)
    ax.text(0.1,0.9,'2 - 10 TeV', fontsize=8,
        transform=ax.transAxes, horizontalalignment='left')

    ax = figures[-1].add_subplot(2, 2, 3)
    ax = plot_regressor_confusion(df[(df[config.energy.target_column]>10) 
        & (df[config.energy.target_column]<50)], 
        ax=ax, log_xy=False, label='x_max', pred='x_max_prediction')
    ax.set_xlabel(r'$Xmax_{\mathrm{true}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_ylabel(r'$Xmax_{\mathrm{rec}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_xlim([200,700])
    ax.set_ylim([200,700])
    ax.plot([0,700], [0,700], color='#D03A3B', alpha=0.5)
    ax.text(0.1,0.9,'10 - 100 TeV', fontsize=8,
        transform=ax.transAxes, horizontalalignment='left')

    ax = figures[-1].add_subplot(2, 2, 4)
    ax = plot_regressor_confusion(df[df[config.energy.target_column]>50], 
        ax=ax, log_xy=False, label='x_max', pred='x_max_prediction')
    ax.set_xlabel(r'$Xmax_{\mathrm{true}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_xlim([200,700])
    ax.set_ylim([200,700])
    ax.plot([0,700], [0,700], color='#D03A3B', alpha=0.5)
    ax.text(0.1,0.9,'> 100 TeV', fontsize=8,
        transform=ax.transAxes, horizontalalignment='left')

    # Plot bias
    figures.append(plt.figure())
    ax = figures[-1].add_subplot(1, 1, 1)
    ax = plot_bias(df, bins=15, ax=ax, log_x=False,
        label='x_max', pred='x_max_prediction')
    ax.set_xlabel(r'$Xmax_{\mathrm{true}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_ylabel('Bias')

    # Plot resolution
    figures.append(plt.figure())
    ax = figures[-1].add_subplot(1, 1, 1)
    ax = plot_resolution(df, bins=15, ax=ax, log_x=False,
        label='x_max', pred='x_max_prediction')
    ax.set_xlabel(r'$Xmax_{\mathrm{true}} \,\, / \,\, \mathrm{g\ cm}^{-2}$')
    ax.set_ylabel('Resolution')

    # Plot feature importances
    figures.append(plt.figure())
    ax = figures[-1].add_subplot(1, 1, 1)
    features = model_config.features
    plot_feature_importances(model, features, ax=ax)

    if output is None:
        plt.show()
    else:
        with PdfPages(output) as pdf:
            for fig in figures:
                pdf.savefig(fig)
