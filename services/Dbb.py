# coding: utf8
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def volatil_store(typeKey, key, storeDict, time):
    key = typeKey + "_" + key
    r.set(key, storeDict, ex=time)
    return key

def generated_key(typeKey, key):
    return typeKey + "_" + key

def is_key_exist(typeKey, key):
    return r.exists(generated_key(typeKey, key))

def store_collection(typeKey, key, storeDict):
    key             = generated_key(typeKey, key)
    already_exist   = r.exists(key)

    r.hmset(key, storeDict)

def collection_for_Key(typeKey="", key=""):
    if key == None:
        return None

    already_exist = r.exists(generated_key(typeKey, key))

    if already_exist == False:
        return None
    else:
        return r.hgetall(generated_key(typeKey, key))


def value_for_key(typeKey="", key=""):
    if key == None:
        return None
    elif typeKey == "":
        return r.get(key)
    else:
        return r.get(generated_key(typeKey, key))

def remove_value_for_key(typeKey="", key=""):
    if key == None:
        return False
    elif typeKey == "":
        return r.delete(key)
    else:
        return r.delete(generated_key(typeKey, key))
