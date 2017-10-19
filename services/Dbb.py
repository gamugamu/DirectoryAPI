# coding: utf8
import redis
import os

if "REDISCLOUD_URL" in os.environ:
    print "REDISCLOUD_URL found ", os.environ['REDISCLOUD_URL']
    r = redis.from_url(os.environ['REDISCLOUD_URL'])
else:
    print "LOCALHOST"
    r  = redis.StrictRedis(host='localhost', port=6379, db=0)

def volatil_store(typeKey, key, storeDict, time):
    key = typeKey + "_" + key
    r.set(key, storeDict, ex=time)
    return key

def generated_key(typeKey, key):
    return typeKey + "_" + key

def is_key_exist(typeKey, key):
    return r.exists(generated_key(typeKey, key))

def is_key_exist_forPattern(key):
    try:
        has_key = len(list(r.scan_iter(match=key))) != 0
        # true 100%
        return has_key

    except Exception as e:
        return False

def store_collection(typeKey="", key="", storeDict=""):
    if typeKey != "" :
        key = generated_key(typeKey, key)

    r.hmset(key, storeDict)

def collection_for_Pattern(pattern=""):
    value = value_for_key(key=pattern)
    try:
        key = value.next()
        return r.hgetall(key)

    except Exception as e:
        return None

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
    if data == "":
        return value
    else:
        return data + "|" + value

def removedValue(data, value):
    data = data.replace(value, "")

    if data[-1:] == "|":
        data = data[:-1]

    return data
