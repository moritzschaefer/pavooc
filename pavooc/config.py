import os

BASEDIR = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')
DATADIR = os.path.join(BASEDIR, 'data')
try:
    os.mkdir(DATADIR)
except FileExistsError:
    pass
try:
    os.mkdir(os.path.join(DATADIR, 'pdbs'))
except FileExistsError:
    pass

S3_BUCKET_URL = 'https://s3.eu-central-1.amazonaws.com/pavooc/{}'
DEBUG = os.environ.get('DEBUG', 'True') in \
    ['True', 'true', '1', 'y', 'yes', 't']
GENOME = os.environ.get('GENOME', 'mm10')
MOUSE_CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 20)] + ['chrX', 'chrY']
HUMAN_CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']
if DEBUG:
    CHROMOSOMES = ['chrY']
else:
    if 'hg' in GENOME:
        CHROMOSOMES = HUMAN_CHROMOSOMES
    else:
        CHROMOSOMES = MOUSE_CHROMOSOMES
TRAIN_MODEL = os.environ.get('TRAIN_MODEL', 'False') in \
    ['True', 'true', '1', 'y', 'yes', 't']

PROTOSPACER_POSITIONS_FILE = os.path.join(DATADIR, 'protospacer_positions.csv')
SIFTS_FILE = os.path.join(DATADIR, 'sifts', '{}')
SIFTS_TARBALL = os.path.join(DATADIR, 'sifts.tar')

# TODO, these three..
GENCODE_HG19_FILE = os.path.join(DATADIR, 'gencode.v19.annotation.gtf')
GENCODE_HG38_FILE = os.path.join(DATADIR, 'gencode.v30.annotation.gtf')
GENCODE_MM10_FILE = os.path.join(DATADIR, 'gencode.vM21.annotation.gtf')
BIG_BED_EXE = os.path.join(DATADIR, 'bedToBigBed')
CHROM_SIZES_FILE = os.path.join(DATADIR, f'{GENOME}.chrom.sizes')
APPRIS_FILE = os.path.join(DATADIR, 'appris_data.principal.txt')
PROTEIN_ID_MAPPING_FILE = os.path.join(DATADIR, f'{"HUMAN_9606" if "hg" in GENOME else "MOUSE_10090"}_idmapping.dat')
PDB_LIST_FILE = os.path.join(DATADIR, 'pdb_chain_uniprot.csv')
CONSERVATION_FEATURES_FILE = os.path.join(
    DATADIR, 'conservations_features.csv')
ACHILLES_CONSERVATION_FEATURES_FILE = os.path.join(
    DATADIR, 'achilles_conservations_features.csv')

CHROMOSOME_FILE = os.path.join(DATADIR, '{}.fa')
CHROMOSOME_RAW_FILE = os.path.join(DATADIR, '{}.raw')
EXON_DIR = os.path.join(DATADIR, 'exons/')
GENOME_FILE = os.path.join(DATADIR, 'genome_{}.fa')
GUIDES_FILE = os.path.join(EXON_DIR, '{}.guides')
SCORES_FILE = os.path.join(EXON_DIR, '{}.guides.scores')
MUTATIONS_FILE = os.path.join(DATADIR, 'ccle2maf_081117.txt')
CNS_FILE = os.path.join(DATADIR, 'CCLE_copynumber_2013-12-03.seg.txt')
EXON_BED_FILE = os.path.join(DATADIR, f'exome_{GENOME}.bed')
SINGLE_PDBS = os.path.join(DATADIR, 'pdbs', f'{GENOME}_{{}}.bed')
PDB_BED_FILE = os.path.join(DATADIR, f'pdbs_{GENOME}.bed')
GUIDE_BED_FILE = os.path.join(DATADIR, f'guides_{GENOME}.bed')
DOMAIN_BED_FILE = os.path.join(DATADIR, f'domains_{GENOME}.bed')
CELLLINES_PATH = os.path.join(DATADIR, 'celllines')
MUTATION_BED_FILE = os.path.join(CELLLINES_PATH, '{}_mutations.bed')
CNS_BED_FILE = os.path.join(CELLLINES_PATH, '{}_cns.bed')
EXON_PADDING = 18
ACHILLES_GUIDE_ACTIVITY_SCORES_FILE = os.path.join(
    DATADIR, 'guide_activity_scores.tsv')
ACHILLES_GUIDE_MAPPING = os.path.join(DATADIR, 'sgRNA_mapping.tsv')
HAEUSSLER_SCORES_FILE = os.path.join(DATADIR,
                                     '13059_2016_1012_MOESM14_ESM.tsv')
WEIGHTS_DIR = os.path.join(DATADIR, 'weights')
SCALER_FILE = os.path.join(DATADIR, 'scaler.pkl')

FLASHFRY_EXE = 'FlashFry-assembly-1.7.5.jar'
JAVA_RAM = os.environ.get('JAVA_RAM', '3')
COMPUTATION_CORES = int(os.environ.get('COMPUTATION_CORES', '1'))
FLASHFRY_TMP_DIR = os.path.join(DATADIR, 'flashfry_tmp')
FLASHFRY_DB_FILE = os.path.join(DATADIR, 'flashfry_genome_db')

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))

# ML

MAX_EPOCHS = 2000
BATCH_SIZE = 128
