# coding: utf8
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def volatil_store(typeKey, key, storeDict, time):
    r.set(typeKey + "_" + key, storeDict, ex=100)
