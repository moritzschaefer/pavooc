from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

# TODO add license
# with open('LICENSE') as f:
#   license = f.read()
description = 'PAVOOC - Prediction and visualization \
        of on- and off-targets for CRISPR',
setup(
        name='pavooc',
        version='0.1.0',
        description=description,
        long_description=readme,
        author='Moritz Schaefer',
        author_email='mail@moritzs.de',
        url='https://github.com/andreassteffen/credit',
        # license=license,
        packages=find_packages(exclude=('tests', 'data', 'docs'))
)
