import os
import stat
import subprocess
import glob

from pavooc.config import BIG_BED_EXE, CHROM_SIZES_FILE, PDB_BED_FILE, \
    EXON_BED_FILE, GUIDE_BED_FILE, DATADIR, MUTATION_BED_FILE, CNS_BED_FILE
from pavooc.data import celllines
from pavooc.data_integration.downloader import main as main_downloader
from pavooc.preprocessing.preprocessing import main as main_preprocessing
from pavooc.preprocessing.prepare_flashfry import main as main_ff
# from pavooc.preprocessing.sgrna_finder import main as main_sgrna
from pavooc.preprocessing.exon_guide_search import main as main_guide_search
from pavooc.preprocessing.guides_to_db import main as main_guides_to_db

from pavooc.preprocessing.generate_pdb_bed import main as generate_pdb_bed
from pavooc.preprocessing.generate_exon_bed import main as generate_exon_bed
from pavooc.preprocessing.generate_guide_bed import main as generate_guide_bed
from pavooc.preprocessing.generate_snp_bed import main as generate_snp_bed
from pavooc.preprocessing.generate_cns_bed import main as generate_cns_bed


def generate_bed_files(skip_generation=False):
    if not skip_generation:
        generate_pdb_bed()
        generate_exon_bed()
        generate_guide_bed()
        generate_snp_bed()
        generate_cns_bed()

    SORTED_TMP_FILE = os.path.join(DATADIR, 'sorted.bed')
    os.chmod(BIG_BED_EXE, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    bedfiles = [EXON_BED_FILE, PDB_BED_FILE, GUIDE_BED_FILE]
    mutation_bedfiles = glob.glob(MUTATION_BED_FILE.format('*'))
    cns_bedfiles = glob.glob(CNS_BED_FILE.format('*'))
    bedfiles.extend(mutation_bedfiles)
    bedfiles.extend(cns_bedfiles)
    for bedfile in bedfiles:
        with open(SORTED_TMP_FILE, 'w') as sorted_file:
            result = subprocess.run(
                ['sort', '-k1,1', '-k2,2n', bedfile],
                stdout=sorted_file, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise RuntimeError(
                    'sort failed for some reason: {}'.format(result.stderr))
        base, _ = os.path.splitext(bedfile)
        result = subprocess.run(
            [BIG_BED_EXE, SORTED_TMP_FILE,
                CHROM_SIZES_FILE, '{}.bb'.format(base)],
            stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError('{} failed for some reason: {}'.format(
                BIG_BED_EXE, result.stderr))


if __name__ == "__main__":
    main_downloader()
    main_preprocessing()
    main_ff()
    main_guide_search()  # ff search
    main_guides_to_db()
    generate_bed_files()
