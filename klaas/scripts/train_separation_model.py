import pandas as pd
import click
from sklearn import model_selection
from tqdm import tqdm
import numpy as np
from sklearn import metrics
import logging
from fact.io import check_extension, write_data

from ..configuration import KlaasConfig
from ..io import pickle_model, read_and_sample_data
from ..preprocessing import convert_to_float32

from ..features import has_source_dependent_columns


logging.basicConfig()
log = logging.getLogger()


@click.command()
@click.argument('configuration_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('signal_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('background_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('predictions_path', type=click.Path(exists=False, dir_okay=False))
@click.argument('model_path', type=click.Path(exists=False, dir_okay=False))
@click.option('-k', '--key', help='HDF5 key for h5py hdf5', default='events')
@click.option('-v', '--verbose', help='Verbose log output', is_flag=True)
def main(configuration_path, signal_path, background_path, predictions_path, model_path, key, verbose):
    '''
    Train a classifier on signal and background monte carlo data and write the model
    to MODEL_PATH in pmml or pickle format.

    CONFIGURATION_PATH: Path to the config yaml file

    SIGNAL_PATH: Path to the signal data

    BACKGROUND_PATH: Path to the background data

    PREDICTIONS_PATH : path to the file where the mc predictions are stored.

    MODEL_PATH: Path to save the model to. Allowed extensions are .pkl and .pmml.
        If extension is .pmml, then both pmml and pkl file will be saved
    '''

    logging.getLogger().setLevel(logging.DEBUG if verbose else logging.INFO)

    check_extension(predictions_path)
    check_extension(model_path, allowed_extensions=['.pmml', '.pkl'])


    klaas_config = KlaasConfig(configuration_path)
    tc = klaas_config.training_config

    if has_source_dependent_columns(klaas_config.columns_to_read):
        raise click.ClickException(
            'Using source dependent features in the model is not supported'
        )

    log.info('Loading signal data')
    df_signal = read_and_sample_data(signal_path, klaas_config, tc.n_signal)
    df_signal['label_text'] = 'signal'
    df_signal['label'] = 1

    log.info('Loading background data')
    df_background = read_and_sample_data(background_path, klaas_config, tc.n_background)
    df_background['label_text'] = 'background'
    df_background['label'] = 0

    df_full = pd.concat([df_background, df_signal], ignore_index=True)


    df_training = convert_to_float32(df_full[klaas_config.training_variables])
    log.info('Total training events: {}'.format(len(df_training)))

    df_training.dropna(how='any', inplace=True)
    log.info('Training events after dropping nans: {}'.format(len(df_training)))

    label = df_full.loc[df_training.index, 'label']

    n_gammas = len(label[label == 1])
    n_protons = len(label[label == 0])
    log.info('Training classifier with {} background and {} signal events'.format(
        n_protons, n_gammas
    ))
    log.info(klaas_config.training_variables)

    # save prediction_path for each cv iteration
    cv_predictions = []

    # iterate over test and training sets
    X = df_training.values
    y = label.values
    n_cross_validations = tc.n_cross_validations
    classifier = tc.model

    log.info('Starting {} fold cross validation... '.format(n_cross_validations))

    stratified_kfold = model_selection.StratifiedKFold(
        n_splits=n_cross_validations, shuffle=True, random_state=tc.seed
    )

    aucs = []
    for fold, (train, test) in enumerate(tqdm(stratified_kfold.split(X, y), total=n_cross_validations)):
        # select data
        xtrain, xtest = X[train], X[test]
        ytrain, ytest = y[train], y[test]

        # fit and predict
        classifier.fit(xtrain, ytrain)

        y_probas = classifier.predict_proba(xtest)[:, 1]
        y_prediction = classifier.predict(xtest)

        cv_predictions.append(pd.DataFrame({
            'label': ytest,
            'label_prediction': y_prediction,
            'probabilities': y_probas,
            'cv_fold': fold,
        }))
        aucs.append(metrics.roc_auc_score(ytest, y_probas))

    log.info('Mean AUC ROC : {}'.format(np.array(aucs).mean()))

    predictions_df = pd.concat(cv_predictions, ignore_index=True)
    log.info('Writing predictions from cross validation')
    write_data(predictions_df, predictions_path, mode='w')

    log.info('Training model on complete dataset')
    classifier.fit(X, y)

    log.info('Pickling model to {} ...'.format(model_path))
    pickle_model(
        classifier=classifier,
        model_path=model_path,
        label_text='label',
        feature_names=list(df_training.columns)
    )


if __name__ == '__main__':
    main()
