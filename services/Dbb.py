# coding: utf8
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def volatil_store(typeKey, key, storeDict, time):
    key = typeKey + "_" + key
    r.set(key, storeDict, ex=time)
    return key

def store_collection_if_unique(typeKey, key, storeDict):
    key             = typeKey + "_" + key
    already_exist   = r.hgetall(key)

    if already_exist != None:
        return 0
    else:
        r.hmset(key, storeDict)
        return 1

def collection_for_Key(typeKey="", key=""):
    if key == None:
        return None
    elif typeKey == "":
        return r.hgetall(key)
    else:
        return r.hgetall(typeKey + "_" + key)


def value_for_key(typeKey="", key=""):
    if key == None:
        return None
    elif typeKey == "":
        return r.get(key)
    else:
        return r.get(typeKey + "_" + key)
