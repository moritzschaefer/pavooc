import pymongo

from pavooc.config import MONGO_HOST

sgRNA_collection = pymongo.MongoClient(host=[MONGO_HOST]).db.sgRNA
