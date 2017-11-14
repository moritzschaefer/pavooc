from pavooc.db import guide_collection
from pavooc.config import GUIDE_BED_FILE


def guide_to_bed(gene, guide):
    """
    Serialize one guide into bed format
    :returns: A string containing one line with the bed-data of the provided
    guide
    """
    strand = '+' if guide['orientation'] == 'FWD' else '-'

    exon_start = [exon['start'] for exon in gene['exons']
                  if exon['exon_id'] == guide['exon_id']][0]

    # BED is 0-based
    return '\t'.join([str(v) for v in [
        gene['chromosome'],
        guide['start'] + exon_start - 1,
        guide['start'] + exon_start - 1 + 23,
        guide['target'],
        min(100,  max(int(guide['score'] * 100), 0)),
        strand,
        guide['start'] + exon_start - 1,
        guide['start'] + exon_start - 1 + 23,
        ','.join([str(v) for v in [0, 255, 0]]),
        '1',
        '23',
        '0'
    ]])


def main():
    with open(GUIDE_BED_FILE, 'w') as f:
        for gene_guides in guide_collection.find():
            for guide in gene_guides['guides']:
                f.write(guide_to_bed(gene_guides, guide))
                f.write('\n')


if __name__ == "__main__":
    main()
