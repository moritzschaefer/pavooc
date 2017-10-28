import os

CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']
CHROMOSOMES = ['chr20', 'chr21', 'chr22']
BASEDIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
DATADIR = os.path.join(BASEDIR, 'data')
EXON_INTERVAL_TREES_FILE = os.path.join(DATADIR, 'interval_trees.pkl')
PROTOSPACER_POSITIONS_FILE = os.path.join(DATADIR, 'protospacer_positions.csv')

GENCODE_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
PROTEIN_ID_MAPPING_FILE = os.path.join(DATADIR, 'HUMAN_9606_idmapping.dat')
PDB_LIST_FILE = os.path.join(DATADIR, 'pdb_chain_uniprot.csv')
CHROMOSOME_FILE = os.path.join(DATADIR, '{}.fa')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')
EXON_DIR = os.path.join(DATADIR, 'exons/')
GENOME_FILE = os.path.join(DATADIR, 'genome.fa')
GUIDES_FILE = os.path.join(EXON_DIR, '{}.guides')
EXON_BED_FILE = os.path.join(DATADIR, 'exome.bed')
EXON_PADDING = 18

DEBUG = os.environ.get('DEBUG', 'True') in \
        ['True', 'true', '1', 'y', 'yes', 't']
JAVA_RAM = os.environ.get('JAVA_RAM', '3')
COMPUTATION_CORES = int(os.environ.get('COMPUTATION_CORES', '1'))
FLASHFRY_TMP_DIR = os.path.join(DATADIR, 'flashfry_tmp')
FLASHFRY_DB_FILE = os.path.join(DATADIR, 'flashfry_genome_db')

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost:27017')
