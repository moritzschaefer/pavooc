import pymongo

from pavooc.config import MONGO_HOST, MONGO_PORT, CRISPR_MODE

# deprecated
sgRNA_collection = pymongo.MongoClient(
    host=MONGO_HOST, port=MONGO_PORT, connect=False).db.sgRNA

if CRISPR_MODE == 'knockout':
    guide_collection = pymongo.MongoClient(
        host=MONGO_HOST, port=MONGO_PORT, connect=False).db.gene_guides
else:
    guide_collection = pymongo.MongoClient(
        host=MONGO_HOST, port=MONGO_PORT, connect=False).db['gene_guides_activation']
