from pavooc.config import GENOME, GUIDE_BED_FILE
from pavooc.db import guide_collection


def guide_to_bed(gene, guide, index):
    """
    Serialize one guide into bed format
    :gene: The gene where the guide is contained in
    :guide: guide information
    :index: the index of the guide
    :returns: A string containing one line with the bed-data of the provided
    guide
    """
    strand = '+' if guide['orientation'] == 'FWD' else '-'

    # BED is 0-based
    return '\t'.join([str(v) for v in [
        gene['chromosome'],
        guide['start'],
        guide['start'] + 23,
        '{}:{}'.format(index+1, guide['target']),
        min(100,  max(int(guide['scores']['azimuth'] * 100), 0)),  # TODO
        strand,
        guide['start'],
        guide['start'] + 23,
        ','.join([str(v) for v in [0, 255, 0]]),
        '1',
        '23',
        '0'
    ]])


def guides_to_bed(guides, gene, bed_file):
    with open(bed_file, 'w') as f:
        for guide_index, guide in enumerate(guides):
            f.write(guide_to_bed(gene, guide, guide_index))
            f.write('\n')


def main():
    with open(GUIDE_BED_FILE, 'w') as f:
        for gene_guides in guide_collection.find({'genome': GENOME}):
            for guide_index, guide in enumerate(gene_guides['guides']):
                f.write(guide_to_bed(gene_guides, guide, guide_index))
                f.write('\n')


if __name__ == "__main__":
    main()
