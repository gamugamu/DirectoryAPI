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

def is_key_exist_forPattern(key):
    return len(list(r.scan_iter(match=key))) != 0

def store_collection(typeKey, key, storeDict):
    key             = generated_key(typeKey, key)
    already_exist   = r.exists(key)

    r.hmset(key, storeDict)

def collection_for_Key(typeKey="", key=""):
    if key == None:
        return None

    if typeKey == "":
        g_key = key
    else:
        g_key = generated_key(typeKey, key)
    already_exist = r.exists(g_key)

    if already_exist == False:
        return None
    else:
        return r.hgetall(g_key)


def value_for_key(typeKey="", key=""):
    if key == None:
        return None
    elif typeKey == "":
        return r.scan_iter(match=key)
    else:
        return r.get(generated_key(typeKey, key))

def purify_key(key=""):
    split =  key.split("_")
    if len(split) >= 1:
        return split[1]
    else:
        return key

def remove_value_for_key(typeKey="", key=""):
    if key == None:
        return False
    elif typeKey == "":
        return r.delete(key)
    else:
        return r.delete(generated_key(typeKey, key))

def remove_with_key_pattern(p_key=""):
    did_deleted = False
    for key in r.scan_iter(p_key):
        r.delete(key)
        did_deleted = True

    return did_deleted

def appendedValue(data, value):
    return data + "|" + value
