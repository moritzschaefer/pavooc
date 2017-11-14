import pandas as pd


def mock_read_gtf_as_dataframe(filename):
    # 'start' AND 'end' are included and are 1-indexed. to transform to proper
    # indexing, just do start-=1 and leave end as is.
    # in our case here, all exons are in-frame (dividable by 3)

    # gene 1 is a valid reverse strand gene with two transcripts
    # all these entries don't vary too much actually.. TODO merge them together
    gene1 = {
        'feature': 'gene', 'gene_id': 'GA', 'transcript_id': 'GA',
        'start': 10, 'end': 30, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }

    gene1_transcript1 = {
        'feature': 'transcript', 'gene_id': 'GA', 'transcript_id': 'TA1',
        'start': 10, 'end': 30, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript1_exon1 = {
        'feature': 'exon', 'gene_id': 'GA', 'transcript_id': 'TA1',
        'start': 25, 'end': 30, 'exon_id': 'EA1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript1_exon2 = {
        'feature': 'exon', 'gene_id': 'GA', 'transcript_id': 'TA1',
        'start': 10, 'end': 18, 'exon_id': 'EA2', 'exon_number': '2',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript2 = {
        'feature': 'transcript', 'gene_id': 'GA', 'transcript_id': 'TA2',
        'start': 25, 'end': 30, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA2',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }
    gene1_transcript2_exon1 = {
        'feature': 'exon', 'gene_id': 'GA', 'transcript_id': 'TA2',
        'start': 25, 'end': 30, 'exon_id': 'EA1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '-',
        'gene_type': 'protein_coding', 'tag': 'basic,abc', 'protein_id': 'PA2',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'ENSEMBL',
    }

    # gene 2 is valid forward strand gene with one transcript which exists on
    # ENSEMBL AND HAVANA with minor difference in its single exon
    gene2 = {
        'feature': 'gene', 'gene_id': 'GB', 'transcript_id': 'GB',
        'start': 5, 'end': 10, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene2_transcript1 = {
        'feature': 'transcript', 'gene_id': 'GB', 'transcript_id': 'TB1',
        'start': 5, 'end': 10, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': 'basic', 'protein_id': 'PB',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene2_transcript1_exon1 = {
        'feature': 'exon', 'gene_id': 'GB', 'transcript_id': 'TB1',
        'start': 5, 'end': 10, 'exon_id': 'EB1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': 'basic', 'protein_id': 'PB',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene2E = {**gene2}
    gene2E['source'] = 'ENSEMBL'
    gene2_transcript1E = {**gene2_transcript1}
    gene2_transcript1E['source'] = 'ENSEMBL'
    gene2_transcript1_exon1E = {**gene2_transcript1_exon1}
    gene2_transcript1_exon1E['source'] = 'ENSEMBL'

    # gene 3 has only transcripts/exons which are not basic
    gene3 = {
        'feature': 'gene', 'gene_id': 'GC', 'transcript_id': 'GC',
        'start': 50, 'end': 70, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': '',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene3_transcript1 = {
        'feature': 'transcript', 'gene_id': 'GC', 'transcript_id': 'TC1',
        'start': 50, 'end': 70, 'exon_id': '', 'exon_number': '',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': 'PC',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    gene3_transcript1_exon1 = {
        'feature': 'exon', 'gene_id': 'GB', 'transcript_id': 'TC1',
        'start': 50, 'end': 70, 'exon_id': 'EC1', 'exon_number': '1',
        'gene_name': 'NA', 'transcript_type': 'protein_coding', 'strand': '+',
        'gene_type': 'protein_coding', 'tag': '', 'protein_id': 'PC',
        'score': float('nan'), 'seqname': 'chrA', 'source': 'HAVANA',
    }

    df = pd.DataFrame([
        gene1,
        gene1_transcript1, gene1_transcript1_exon1, gene1_transcript1_exon2,
        gene1_transcript2, gene1_transcript2_exon1,
        gene2, gene2_transcript1, gene2_transcript1_exon1,
        gene2E, gene2_transcript1E, gene2_transcript1_exon1E,
        gene3, gene3_transcript1, gene3_transcript1_exon1
    ])

    # add unused keys
    for key in [
            'ccdsid', 'frame', 'gene_status', 'havana_gene',
            'havana_transcript', 'level', 'ont', 'transcript_name',
            'transcript_status']:
        df[key] = ''
    return df
