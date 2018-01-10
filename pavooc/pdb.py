#!/usr/bin/env python3
import logging
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import re
from gzip import GzipFile

from pavooc.config import SIFTS_FILE


def pdb_mappings(pdb, chain, swissprot_id):
    intre = re.compile('-?\d+')
    ret = {}
    try:
        # read xml
        fi = GzipFile(SIFTS_FILE.format(
            '{}.xml.gz'.format(pdb.lower()), 'r'))
        # parse xml
        tree = ET.fromstring(fi.read())
    except (EOFError, ParseError) as e:
        logging.error(f'File {fi}.xml.gz corrupt: {e}')
        return {}
    except FileNotFoundError as e:
        logging.error(f'File {fi}.xml.gz not found: {e}')
        return {}
    for i in range(len(tree)):
        if tree[i].tag.split('}')[-1] != 'entity':
            continue
        for j in range(len(tree[i])):
            if tree[i][j].tag.split('}')[-1] != 'segment':
                continue
            for k in range(len(tree[i][j])):
                if tree[i][j][k].tag.split('}')[-1] != 'listResidue':
                    continue
                for resid in tree[i][j][k].getchildren():
                    pdb_id = None
                    pdb_rn = None  # residue number
                    pdb_aa = None
                    uniprot_id = None
                    uniprot_rn = None  # residue number
                    uniprot_aa = None
                    for ref in resid.getchildren():
                        if ref.tag.split('}')[-1] != "crossRefDb":
                            continue
                        if ref.attrib['dbSource'] == 'PDB':
                            if chain != ref.attrib['dbChainId']:
                                continue
                            pdb_id = ref.attrib['dbAccessionId']
                            pdb_chain = ref.attrib['dbChainId']
                            pdb_aa = ref.attrib['dbResName']
                            try:
                                pdb_rn = int(intre.findall(
                                    ref.attrib['dbResNum'])[0])
                            except IndexError:
                                pass

                        elif ref.attrib['dbSource'] == 'UniProt':
                            if swissprot_id != ref.attrib['dbAccessionId']:
                                continue
                            uniprot_id = ref.attrib['dbAccessionId']
                            uniprot_aa = ref.attrib['dbResName']
                            uniprot_rn = int(ref.attrib['dbResNum'])
                    if pdb_rn is not None and uniprot_rn is not None:
                        # should not happen; otherwise: redundant maps
                        if uniprot_rn in ret and ret[uniprot_rn] != pdb_rn:
                            print(pdb, chain,
                                  swissprot_id,
                                  ret[uniprot_rn], (pdb_rn, pdb_aa))
                            #raise Exception("Fix this! 1")
                        #ret[uniprot_rn] = (pdb_rn, pdb_aa)
                        ret[uniprot_rn] = pdb_rn
    return ret
