from setuptools import setup

setup(
    name='fact-classifier',
    version='0.0.2',
    description='classifier -- tools to build models on FACT MC data  ',
    url='https://github.com/fact-project/erna',
    author='Kai Brügge',
    author_email='kai.bruegge@tu-dortmund.de',
    license='MIT',
    py_modules=[
                'classifier/apply_regression_model',
                'classifier/apply_separation_model',
                'classifier/train_separation_model',
                'classifier/train_energy_regressor',
                ],
    # dependency_links = ['git+https://github.com/mackaiver/gridmap.git#egg=gridmap'],
    install_requires=[
        'pandas',           # in anaconda
        'numpy',            # in anaconda
        'matplotlib>=1.4',  # in anaconda
        'python-dateutil',  # in anaconda
        'pytz',             # in anaconda
        'pyyaml',             # in anaconda
        'tables',           # needs to be installed by pip for some reason
        # 'hdf5',
        'click',
        'numexpr',
        'pytest', # also in  conda
    ],
   zip_safe=False,
   entry_points={
    'console_scripts': [
        'apply_separation_model = classifier.apply_separation_model:main',
        'apply_regression_model =classifier.apply_regression_model:main',
        'train_separation_model =classifier.train_separation_model:main',
        'train_energy_regressor =classifier.train_energy_regressor:main',
    ],
  }
)