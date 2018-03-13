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
            # if gene_id[:15] != 'ENSG00000010671':
            #     continue
            unique_exons = exons.reset_index().groupby('exon_id').first()
            # if len(unique_exons) < len(exons):
                # we should filter by chromosome. not by something else..
                # __import__('ipdb').set_trace()
            sorted_exons = unique_exons.sort_values('start')

            gene_start = min(unique_exons.start)
            gene_end = max(unique_exons.end)
            strand = unique_exons.iloc[0]['strand']

            if strand == '+':
                exon_frames = [0]
                for _, exon in sorted_exons.iterrows():
                    exon_frames.append((exon_frames[-1] + (exon.end-exon.start)) % 3)
                exon_frames.pop()
            else:
                exon_frames = [0]
                for _, exon in sorted_exons[::-1].iterrows():
                    exon_frames.append((exon_frames[-1] + (exon.end-exon.start)) % 3)
                exon_frames.pop()
                exon_frames = reversed(exon_frames)

            # Gencode GTF holds 1-based index data
            # https://genome.ucsc.edu/goldenpath/help/bigGenePred.html
            data = [[unique_exons.iloc[0]['seqname']][0],
                    gene_start,
                    gene_end,
                    gene_id,  # TODO "Name or ID of item, ideally both human-readable and unique"
                    0,
                    strand,
                    gene_start,
                    gene_end,
                    ','.join([str(v) for v in [255, 0, 0]]),
                    len(unique_exons),
                    ','.join(
                        (sorted_exons.end -
                            (sorted_exons.start)).map(str)),
                    ','.join((sorted_exons.start - gene_start).map(str)),
                    # "Alternative/human readable name"
                    sorted_exons.iloc[0].swissprot_id,
                    'cmpl',  # https://www.biostars.org/p/152555/
                    'cmpl',  # "enum('none','unk','incmpl','cmpl')"
                    # "Exon frame {0,1,2}, or -1 if no frame for exon. list"
                    ','.join([str(v) for v in exon_frames]),
                    'none',  # "Transcript type wtf?
                    gene_id,  # "Primary identifier for gene"
                    # "Alternative/human-readable gene name"
                    sorted_exons.iloc[0].gene_name,
                    'protein_coding',  # "Gene type"
                    ]

            f.write('\t'.join([str(v) for v in data]))
            f.write('\n')


if __name__ == "__main__":
    main()
