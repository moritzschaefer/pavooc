import subprocess
import os
import shutil
import logging

from pavooc.config import JAVA_RAM, FLASHFRY_TMP_DIR, FLASHFRY_DB_FILE, \
        GENOME_FILE


def main():
    try:
        os.mkdir(FLASHFRY_TMP_DIR)
    except FileExistsError:
        pass
    logging.info('Running FlashFry to build up off-target database')
    subprocess.Popen([
            'java',
            '-Xmx{}g'.format(JAVA_RAM),
            '-jar', 'FlashFry-assembly-1.6.jar',
            '--analysis', 'index',
            '--tmpLocation', FLASHFRY_TMP_DIR,
            '--database', FLASHFRY_DB_FILE,
            '--reference', GENOME_FILE,
            '--enzyme', 'spcas9ngg']).wait()

    # free memory
    shutil.rmtree(FLASHFRY_TMP_DIR)


if __name__ == "__main__":
    main()
