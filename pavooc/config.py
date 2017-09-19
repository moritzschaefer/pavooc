import os

CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']
BASEDIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
DATADIR = os.path.join(BASEDIR, 'data')
