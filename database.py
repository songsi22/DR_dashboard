from pymongo import MongoClient

def collectioncon(svr):
    client=MongoClient('localhost', 27017)
    db = client.ap
    cl = db.get_collection(svr)
    return cl