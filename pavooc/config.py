import os

CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']
CHROMOSOMES = ['chr22']
BASEDIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
DATADIR = os.path.join(BASEDIR, 'data')
EXON_INTERVAL_TREES_FILE = os.path.join(DATADIR, 'interval_trees.pkl')
PROTOSPACER_POSITIONS_FILE = os.path.join(DATADIR, 'protospacer_positions.csv')

GENCODE_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
CHROMOSOME_FILE = os.path.join(DATADIR, '{}.fa')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')
EXON_DIR = os.path.join(DATADIR, 'exons/')
GENOME_FILE = os.path.join(DATADIR, 'genome.fa')
GUIDES_FILE = os.path.join(EXON_DIR, '{}.guides')
EXON_PADDING = 18


JAVA_RAM = os.environ.get('JAVA_RAM', '4')
FLASHFRY_TMP_DIR = os.path.join(DATADIR, 'flashfry_tmp')
FLASHFRY_DB_FILE = os.path.join(DATADIR, 'flashfry_genome_db')

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost:27017')
