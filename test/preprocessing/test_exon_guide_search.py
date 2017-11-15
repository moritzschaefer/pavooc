import os
from pavooc.util import read_guides
from pavooc.preprocessing import exon_guide_search

from nose.tools import eq_

# TODO improve relative->absolute paths?
exon_guide_search.EXON_DIR = './test/data'
exon_guide_search.GUIDES_FILE = './test/data/{}.guides'


# TODO need to generate flashfry-database first..!
def test_flashfry_guides():
    gene_id = 'G1'
    with open(os.path.join(
            exon_guide_search.EXON_DIR,
            gene_id), 'w') as f:
        f.write('''>E1;-;0;9;T1:2.0,T2:1.0
AAAAAAAAAAAAAAAATCCTTTGGTAAAAAAAAAAAAAAAA
>E2;-;33;39;T1:1.0
AAAAAAAAAAAACCAATTTTTTAAAAAAAAAAAAAAAA''')

    target_file = exon_guide_search.flashfry_guides(gene_id)

    eq_(target_file,
        os.path.join(exon_guide_search.EXON_DIR, gene_id + '.guides'))

    df = read_guides(target_file)
    eq_(len(df), 3)

    # check that the GG sequence is FWD and the CC is reverse
    eq_(list(df[df['orientation'] == 'FWD'].target),
        ['AAAAAAAAAAAAAAATCCTTTGG'])
    eq_(list(df[df['orientation'] == 'FWD'].start), [1])

    # target is reverse-complemented in flashfry
    eq_(set(df[df['orientation'] == 'RVS'].target),
        {'TTTTTTTTTTTTTAAAAAATTGG', 'TTTTTTTTTTTTTTTACCAAAGG'})
    eq_(set(df[df['orientation'] == 'RVS'].start), {12, 17})
