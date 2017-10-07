# coding: utf8
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def volatil_store(typeKey, key, storeDict, time):
    key = typeKey + "_" + key
    r.set(key, storeDict, ex=time)
    return key

def valueForKey(typeKey="", key=""):
    if key == None:
        return None
    elif typeKey == "":
        return r.get(key)
    else:
        return r.get(typeKey + "_" + key)
