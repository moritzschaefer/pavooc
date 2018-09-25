import pymongo

from pavooc.config import MONGO_HOST, MONGO_PORT

# deprecated
sgRNA_collection = pymongo.MongoClient(
    host=MONGO_HOST, port=MONGO_PORT, connect=False).db.sgRNA

guide_collection = pymongo.MongoClient(
    host=MONGO_HOST, port=MONGO_PORT, connect=False).db.gene_guides
