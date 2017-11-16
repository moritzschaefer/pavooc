'''
Create a bed file for the exome
'''
from pavooc.config import EXON_BED_FILE
from pavooc.data import gencode_exons


def main():
    """
    https://www.ensembl.org/info/website/upload/bed.html
    https://genome.ucsc.edu/goldenpath/help/customTrack.html
    """
    with open(EXON_BED_FILE, 'w') as f:
        for gene_id, exons in gencode_exons().groupby('gene_id'):
            unique_exons = exons.reset_index().groupby('exon_id').first()
            sorted_exons = unique_exons.sort_values('start')

            gene_start = min(unique_exons.start)
            gene_end = max(unique_exons.end)

            # Gencode GTF holds 1-based index data
            data = [[unique_exons.iloc[0]['seqname']][0],
                    gene_start,
                    gene_end,
                    gene_id,
                    0,
                    unique_exons.iloc[0]['strand'],
                    gene_start,
                    gene_end,
                    ','.join([str(v) for v in [255, 0, 0]]),
                    len(unique_exons),
                    ','.join(
                        (sorted_exons.end -
                            (sorted_exons.start)).map(str)),
                    ','.join((sorted_exons.start - gene_start).map(str))]

            f.write('\t'.join([str(v) for v in data]))
            f.write('\n')


if __name__ == "__main__":
    main()
