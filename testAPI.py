# -*- coding: utf-8 -*-
# coding: utf8
import datetime
from datetime import datetime, timedelta
import base64
import uuid
import json
import uuid

from enum import Enum
from Crypto import Random
from Crypto.Cipher import AES
import requests

AKEY    = 'd872eebd3967a9a00bdcb7235b491d87'
iv      = 'key-directoryAPI'
TOKEN_TIME_EXPIRATION_SEC   = 10000
Fa01_DATE_FORMAT            = "%Y-%m-%d_%H:%M:%S"
TOKEN_REQU_HEADER           = "token-request"
TOKEN_HEADER                = "token"

urlRoot = "http://127.00.0.1:8000/rest/"
version = ""
url     = urlRoot + version


def encrypt(message):
    obj = AES.new(AKEY, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))

def decrypt(cipher):
    obj2 = AES.new(AKEY, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))

print url

apirequestkey           = encrypt(AKEY + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
headers_requestToken    = {'content-type': 'application/json', 'token-request' : apirequestkey}

print "========== launching test on " + urlRoot + " API. ==========="
print "==========" +url + "asktoken" + "==========="

r = requests.get(url + "asktoken", headers=headers_requestToken)
print r.content + "\n"
data    = json.loads(r.content)
token   = data["token"]["hash"]

headers_token    = {'content-type': 'application/json', 'token' : token}

print "========== launching test on " + urlRoot + " API. ==========="
print "==========" + url + "createaccount" + "==========="
email               = "jojo@hotmail.fr" #str(uuid.uuid4())[0:6] + "@gmail.com"
password            = "superpassE0"
crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
r = requests.post(url + "createaccount", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email, "cryptpassword" : crypted_password}}))
print r.content + "\n"

print "==========" + url + "login (fail)" + "==========="
crypted_password    = encrypt(AKEY + "|" + "fdklfdp" + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
r = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email , "cryptpassword" : crypted_password}}))
print r.content + "\n"

print "==========" + url + "login (success)" + "==========="
crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
r = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email , "cryptpassword" : crypted_password}}))
print r.content + "\n"

#data=json.dumps(payload),

#r = requests.get(urlRoot)

# #Ia01, #Ia02
#print "[#Ia01, #Ia02] status code == 200", r.status_code, r.status_code == 200

# #Ia03
#print "[#Ia03] version == ", r.headers["version"], version == r.headers["version"]
