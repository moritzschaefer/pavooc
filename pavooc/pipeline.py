import os
import stat
import subprocess
import glob
import logging

from pavooc.config import BIG_BED_EXE, CHROM_SIZES_FILE, PDB_BED_FILE, \
    EXON_BED_FILE, GUIDE_BED_FILE, DATADIR, MUTATION_BED_FILE, CNS_BED_FILE, \
    DOMAIN_BED_FILE
from pavooc.data_integration.downloader import main as main_downloader
from pavooc.preprocessing.preprocessing import main as main_preprocessing
from pavooc.preprocessing.preprocessing import generate_raw_chromosomes, combine_genome
from pavooc.preprocessing.prepare_flashfry import main as main_ff
# from pavooc.preprocessing.sgrna_finder import main as main_sgrna
from pavooc.preprocessing.exon_guide_search import main as main_guide_search
from pavooc.preprocessing.guides_to_db import main as main_guides_to_db
from pavooc.preprocessing.extract_conservation_scores import main as \
    main_extract_conservation_scores

from pavooc.preprocessing.generate_pdb_bed import main as generate_pdb_bed
from pavooc.preprocessing.generate_exon_bed import main as generate_exon_bed
from pavooc.preprocessing.generate_guide_bed import main as generate_guide_bed
from pavooc.preprocessing.generate_snp_bed import main as generate_snp_bed
from pavooc.preprocessing.generate_cns_bed import main as generate_cns_bed
from pavooc.preprocessing.generate_domain_bed import main as \
    generate_domain_bed
from pavooc.scoring.training import generate_final_model

logging.basicConfig(level=logging.INFO)


def generate_bed_files(skip_generation=False):
    if not skip_generation:
        generate_pdb_bed()
        generate_exon_bed()
        generate_guide_bed()
        generate_snp_bed()
        generate_cns_bed()
        generate_domain_bed()

    SORTED_TMP_FILE = os.path.join(DATADIR, 'sorted.bed')
    os.chmod(BIG_BED_EXE, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    bedfiles = [EXON_BED_FILE, GUIDE_BED_FILE, PDB_BED_FILE, DOMAIN_BED_FILE]
    mutation_bedfiles = glob.glob(MUTATION_BED_FILE.format('*'))
    cns_bedfiles = glob.glob(CNS_BED_FILE.format('*'))
    # bedfiles.extend(mutation_bedfiles)
    # bedfiles.extend(cns_bedfiles)
    for bedfile in bedfiles:  # TODO is bigbed necessary here??
        logging.info(f'Bed->BB for {bedfile}')
        with open(SORTED_TMP_FILE, 'w') as sorted_file:
            result = subprocess.run(
                ['sort', '-k1,1', '-k2,2n', bedfile],
                stdout=sorted_file, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise RuntimeError(
                    'sort failed for some reason: {}'.format(result.stderr))
        base, _ = os.path.splitext(bedfile)
        arguments = [BIG_BED_EXE, SORTED_TMP_FILE,
                     CHROM_SIZES_FILE, '{}.bb'.format(base)]
        if bedfile == EXON_BED_FILE:
            arguments.extend(
                ['-as=pavooc/preprocessing/bigGenePred.as', '-type=bed12+8'])
        result = subprocess.run(arguments, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError('{} failed for some reason: {}'.format(
                BIG_BED_EXE, result.stderr))


def initialize_db():
    '''
    This is the quick way, that downloads all preprocessed data and inserts it in the DB
    '''
    main_downloader()
    generate_raw_chromosomes()
    combine_genome()
    result = subprocess.run(
        ['mongorestore', '--host', 'mongo', os.path.join(DATADIR, 'dump')],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(
            'Failed restoring mongo: {}'.format(result.stderr))
    generate_bed_files()


def build_db():
    '''
    This is the long way, that downloads all raw data and computes all necessary data
    to then insert it into mongoDB
    '''
    main_downloader()
    main_preprocessing()
    main_extract_conservation_scores()
    main_ff()
    main_guide_search()  # ff search
    main_guides_to_db()
    generate_bed_files()
    generate_final_model()
    print('finished pipeline')


if __name__ == '__main__':
    if os.environ.get('ONLY_INIT', 'True') in \
            ['True', 'true', '1', 'y', 'yes', 't']:
        initialize_db()
    else:
        build_db()
