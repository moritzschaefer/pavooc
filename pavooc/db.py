import pymongo

from pavooc.config import MONGO_HOST

# deprecated
sgRNA_collection = pymongo.MongoClient(
    host=[MONGO_HOST], connect=False).db.sgRNA

guide_collection = pymongo.MongoClient(
    host=[MONGO_HOST], connect=False).db.gene_guides
