from gtfparse import read_gtf_as_dataframe

from pavooc.config import GENCODE_FILE


def read_gencode():
    '''
    Buffered gencode
    '''
    if not read_gencode.buffered:
        read_gencode.buffered = read_gtf_as_dataframe(GENCODE_FILE)
    return read_gencode.buffered


read_gencode.buffered = None
