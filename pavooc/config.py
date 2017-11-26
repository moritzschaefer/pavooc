import os

CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']
CHROMOSOMES = ['chr22']
BASEDIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
DATADIR = os.path.join(BASEDIR, 'data')
PROTOSPACER_POSITIONS_FILE = os.path.join(DATADIR, 'protospacer_positions.csv')
SIFTS_FILE = os.path.join(DATADIR, 'sifts', '{}')
SIFTS_TARBALL = os.path.join(DATADIR, 'sifts.tar')

GENCODE_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
BIG_BED_EXE = os.path.join(DATADIR, 'bedToBigBed')
CHROM_SIZES_FILE = os.path.join(DATADIR, 'hg19.chrom.sizes')
APPRIS_FILE = os.path.join(DATADIR, 'appris_data.principal.txt')
PROTEIN_ID_MAPPING_FILE = os.path.join(DATADIR, 'HUMAN_9606_idmapping.dat')
PDB_LIST_FILE = os.path.join(DATADIR, 'pdb_chain_uniprot.csv')
CHROMOSOME_FILE = os.path.join(DATADIR, '{}.fa')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')
EXON_DIR = os.path.join(DATADIR, 'exons/')
GENOME_FILE = os.path.join(DATADIR, 'genome.fa')
GUIDES_FILE = os.path.join(EXON_DIR, '{}.guides')
EXON_BED_FILE = os.path.join(DATADIR, 'exome.bed')
PDB_BED_FILE = os.path.join(DATADIR, 'pdbs.bed')
GUIDE_BED_FILE = os.path.join(DATADIR, 'guides.bed')
EXON_PADDING = 18

DEBUG = os.environ.get('DEBUG', 'True') in \
        ['True', 'true', '1', 'y', 'yes', 't']
JAVA_RAM = os.environ.get('JAVA_RAM', '3')
COMPUTATION_CORES = int(os.environ.get('COMPUTATION_CORES', '1'))
FLASHFRY_TMP_DIR = os.path.join(DATADIR, 'flashfry_tmp')
FLASHFRY_DB_FILE = os.path.join(DATADIR, 'flashfry_genome_db')

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost:27017')
