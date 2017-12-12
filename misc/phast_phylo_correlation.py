# coding: utf-8
import numpy as np
import re


with open('chr22.phastCons100way.wigFix') as phast_file, \
        open('chr22.phyloP100way.wigFix') as phylo_file:
    phylo_pos, phast_pos = 0, 0
    phylo_lines = iter(phylo_file)
    phast_lines = iter(phast_file)
    phylos = []
    phasts = []
    try:
        while True:
            if phylo_pos < phast_pos:
                # try phylo
                phylo_line = next(phylo_lines)
                if phylo_line[0] == 'f':
                    phylo_pos = int(
                        re.search('start=(\d+)', phylo_line).groups()[0])
                    phylo_line = next(phylo_lines)
                else:
                    phylo_pos += 1
            else:
                phast_line = next(phast_lines)
                if phast_line[0] == 'f':
                    phast_pos = int(
                        re.search('start=(\d+)', phast_line).groups()[0])

                    phast_line = next(phast_lines)
                else:
                    phast_pos += 1
            if phylo_pos == phast_pos:
                phylos.append(float(phylo_line.rstrip()))
                phasts.append(float(phast_line.rstrip()))
    except StopIteration:
        pass

print(np.corrcoef(phylos, phasts))
