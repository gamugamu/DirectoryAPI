# -*- coding: utf-8 -*-
# coding: utf8
import datetime
from StringIO import StringIO  # Python2
import sys

from services.Error import Error
from services.JSONValidator import iterate_through_graph
from datetime import datetime, timedelta
import base64
import uuid
import json
import uuid

from enum import Enum
from Crypto import Random
from Crypto.Cipher import AES
import requests

# Store the reference, in case you want to show things again in standard output

old_stdout = sys.stdout

# This variable will store everything that is sent to the standard output

result = StringIO()

sys.stdout = result

class color:
   PURPLE       = '\033[95m'
   CYAN         = '\033[96m'
   DARKCYAN     = '\033[36m'
   BLUE         = '\033[94m'
   GREEN        = '\033[92m'
   YELLOW       = '\033[93m'
   RED          = '\033[91m'
   BOLD         = '\033[1m'
   UNDERLINE    = '\033[4m'
   END          = '\033[0m'

AKEY    = 'd872eebd3967a9a00bdcb7235b491d87'
iv      = 'key-directoryAPI'
TOKEN_TIME_EXPIRATION_SEC   = 10000
Fa01_DATE_FORMAT            = "%Y-%m-%d_%H:%M:%S"
TOKEN_REQU_HEADER           = "token-request"
TOKEN_HEADER                = "token"

urlRoot     = "http://127.00.0.1:8000"
version_API = "0.0.2"

# graph
g_e = {"error" : {"code" : "", "description" : ""}};
g_u = {"user" : {"uid" : "", "email" : "", "name" : "", "group" : ""}};
g_t = {"token" : {"hash" : "", "dateLimit" : "", "right" : ""}};
g_p = {"filepayload" : {"type" : "", "name" : "", "parentId" : "", "uid" :"", "owner" : "",
"title" : "", "date" : "", "rules": "", "childsId": ""}};

def encrypt(message):
    obj = AES.new(AKEY, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))

def decrypt(cipher):
    obj2 = AES.new(AKEY, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))

def performtest(urlRoot=urlRoot, version_API=urlRoot):
    print "WILL performtest ", urlRoot, urlRoot

    url = urlRoot + "/rest/" + version_API + "/"
    apirequestkey           = encrypt(AKEY + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    headers_requestToken    = {'content-type': 'application/json', 'token-request' : apirequestkey}

    print "\n\n\n========== launching test on " + url + " API. ==========="
    print  color.BOLD + color.PURPLE + "[#Pa01] [#Pa02] [#Pa03]" + color.END
    r = requests.get(url)
    print "[#Pa01] statuscode: ", r.status_code, "== 200", r.status_code == 200
    print "[#Pa02] uri version: ", url, r.status_code == 200
    print "[#Pa03] header version: ", r.headers["Version"], r.headers["Version"] == version_API

    print "\n========== " +url + "asktoken ==========="
    print  color.BOLD + color.PURPLE + "[#SaP01] [#SaD01]" + color.END

    r       = requests.get(url + "asktoken", headers=headers_requestToken)
    data    = json.loads(r.content)
    token   = data["token"]["hash"]

    print "[#SaP01] url: ", r.status_code, "== 200", r.status_code == 200

    e = iterate_through_graph(data, {"error" : {"code" : "", "description" : ""}, "token" : {"hash" : "", "right" : "", "dateLimit" : ""}})
    print "[#SaD01] datastructure: ", e.value == Error.SUCCESS.value, e
    headers_requestToken    = {'content-type': 'application/json', 'token-request' : "invalid_key"}
    r       = requests.get(url + "asktoken", headers=headers_requestToken)
    data    = json.loads(r.content)
    e       = iterate_through_graph(data, {"error" : {"code" : "", "description" : ""}, "token" : {"hash" : "", "right" : "", "dateLimit" : ""}})
    print "[#SaD01] with bad apiKey", int(data["error"]["code"]) == 2 # code invalid_apikey
    print "[#SaD01] get blank datastructure", e.value == Error.SUCCESS.value


    headers_token    = {'content-type': 'application/json', 'token' : token}

    print "\n========== " + url + "createaccount ==========="
    print  color.BOLD + color.PURPLE + "[#SbP01] [#SbD01] [#SbR01] [#SbR02]" + color.END

    email               = str(uuid.uuid4())[0:6] + "fd.com"
    password            = "superpassE0"
    crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r       = requests.post(url + "createaccount", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email, "cryptpassword" : crypted_password}}))
    data    = json.loads(r.content)

    print "[#SbR02] bad email ", int(data["error"]["code"]) == 10 # invalid_user_email

    email               = str(uuid.uuid4())[0:6] + "@fddfs.com"
    password            = "superp___0"
    crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r                   = requests.post(url + "createaccount", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email, "cryptpassword" : crypted_password}}))
    data                = json.loads(r.content)
    print "[#SbR02] bad password ", int(data["error"]["code"]) == 11 #invalid_user_password

    email               = str(uuid.uuid4())[0:6] + "@gmail.com"
    password            = "superpassE0"
    crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r = requests.post(url + "createaccount", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email, "cryptpassword" : crypted_password}}))
    data                = json.loads(r.content)

    print "[#SbPO1] url", r.status_code == 200
    e = iterate_through_graph(data, g_e)

    print "[#SbDO1] datastructure", e.value == Error.SUCCESS.value
    r = requests.post(url + "createaccount", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email, "cryptpassword" : crypted_password}}))
    data                = json.loads(r.content)
    print "[#SbRO1] compte already exist", int(data["error"]["code"]) == 30 #user_already_exist


    print "\n==========" + url + "login ==========="
    print  color.BOLD + color.PURPLE + "[#SdP01] [#SdD01] [#SdR01]" + color.END

    crypted_password    = encrypt(AKEY + "|" + "superpassE2" + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email , "cryptpassword" : crypted_password}}))
    print "[#SdP01] uri ", r.status_code, "== 200", r.status_code == 200
    data    = json.loads(r.content)
    e       = iterate_through_graph(data, dict(dict(g_e, **g_u), **g_t))

    print "[#SdD01] datastructure ", e.value == Error.SUCCESS.value
    print "[#SdR01] wrong-password ", int(data["error"]["code"]) == 33 # wring password code

    false_account = "chewi@gmail.ocm"
    crypted_password    = encrypt(AKEY + "|" + password + "|" + false_account + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r       = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : false_account , "cryptpassword" : crypted_password}}))
    data    = json.loads(r.content)
    print "[#SdR01] user not found ", int(data["error"]["code"]) == 31 # user not found

    crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r       = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email , "cryptpassword" : crypted_password}}))
    data    = json.loads(r.content)
    print "[#SdR01] login OK", int(data["error"]["code"]) == 1 # success
    token_session = data["token"]["hash"]


    print "\n==========" + url + "logout ==========="
    print  color.BOLD + color.PURPLE + "[#SeP01] [#SeD01] [#SeR01]" + color.END
    headers_token    = {'content-type': 'application/json', 'token' : token_session}
    r = requests.get(url + "logout", headers=headers_token)

    print "[#SeP01] uri ", r.status_code, "== 200", r.status_code == 200
    e = iterate_through_graph(data, dict(g_e, **g_t))

    print "[#SeD01] datastructure", e.value == Error.SUCCESS.value
    headers_token    = {'content-type': 'application/json', 'token' : token_session}
    r = requests.get(url + "logout", headers=headers_token)
    data    = json.loads(r.content)
    print "[#SeR01] re-logout", int(data["error"]["code"]) == 3 # false token

    print "\n==========" + url + "re-login attempt ==========="
    crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email , "cryptpassword" : crypted_password}}))
    token_session = json.loads(r.content)["token"]["hash"]
    headers_token    = {'content-type': 'application/json', 'token' : token_session}
    data    = json.loads(r.content)
    print "[#SdR01] re-login", int(data["error"]["code"]) == 1 # success


    print "\n==========" + url + "create FILE " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    print  color.BOLD + color.PURPLE + "[#SfP01] [#SfD01] [#SfR01]" + color.END

    data = {"filetype" : {"type" : 1, "name" : "yellow5", "parentId" : ""}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    data = json.loads(r.content)
    group_id = data["filepayload"]["uid"]
    print "[#SfP01] uri ", r.status_code, "== 200", r.status_code == 200
    e       = iterate_through_graph(data, dict(g_e, **g_p))

    print "[#SfD01] datastructure ", e.value == Error.SUCCESS.value
    data = {"filetype" : {"type" : 6, "name" : "yellow5", "parentId" : ""}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    data = json.loads(r.content)
    print "[#SfR01] datastructure ", e.value == Error.SUCCESS.value
    print "[#SfR01] error wrong type ", int(data["error"]["code"]) == 50 #wrong type code


    print "\n==========" + url + "create File in Group " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 3, "name" : "subYellow", "parentId" : group_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    data = json.loads(r.content)
    file1       = data
    file1_id    = data["filepayload"]["uid"]

    print "\n==========" + url + "modify File ==========="
    print  color.BOLD + color.PURPLE + "[#SgP01] [#SgD01] [#SgR01]" + color.END

    file1["filepayload"]["payload"] = "This is a content from yellow"
    r = requests.post(url + "modifyfile", headers=headers_token, data=json.dumps(file1))
    print "[#SgP01] uri ", r.status_code, "== 200", r.status_code == 200
    e       = iterate_through_graph(data, dict(g_e, **g_p))

    print "[#SgD01] datastructure ", e.value == Error.SUCCESS.value
    print "[#SgR01] right (not tested)", False


    print "\n============= TEST GRAPH  ==============="
    print "========================================="

    print "==========" + url + "create File in Group (2)" + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 3, "name" : "subGreen", "parentId" : group_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)
    file2_id = data["filepayload"]["uid"]

    print "==========" + url + "create File in Group (3)" + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 3, "name" : "subRed", "parentId" : group_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data    = json.loads(r.content)
    file_id = data["filepayload"]["uid"]

    print "==========" + url + "delete File in Group (3)" + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"fileid" : {"type" : 3, "name" : data["filepayload"]["name"], "uid" : file_id}}
    r = requests.post(url + "deletefile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)

    print "==========" + url + "get headers " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"fileids" : [group_id, file2_id, file1_id]}
    r = requests.post(url + "filesheader", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)

    print "==========" + url + "create Folder in Group " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 2, "name" : "fruits", "parentId" : group_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)
    folder_id = data["filepayload"]["uid"]

    print "==========" + url + "create file in Folder " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 3, "name" : "pomme", "parentId" : folder_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)

    print "==========" + url + "create Folder in Folder " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 2, "name" : "legumes", "parentId" : folder_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)
    folder2_id = data["filepayload"]["uid"]

    print "==========" + url + "create file in Folder/Folder " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 3, "name" : "celeri", "parentId" : folder2_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)

    print "==========" + url + "create file in Folder/Folder " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 3, "name" : "oignon", "parentId" : folder2_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)

    print "==========" + url + "create folder to Folder/Folder/Folder " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 2, "name" : "dessert", "parentId" : folder2_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)
    folder3_id = data["filepayload"]["uid"]

    print "==========" + url + "create file in Folder/Folder/Folder " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"filetype" : {"type" : 2, "name" : "foretNoire", "parentId" : folder3_id}}
    r = requests.post(url + "createfile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"
    data = json.loads(r.content)
    folder3_id = data["filepayload"]["uid"]


    print "==========" + url + "delete GROUP " + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    data = {"fileid" : {"type" : 1, "name" : "yellow2", "uid" : group_id}}
    r = requests.post(url + "deletefile", headers=headers_token, data=json.dumps(data))
    print r.content + "\n"


    print "==========" + url + "deleteaccount" + color.BOLD + color.PURPLE + "(must succeed)" + color.END + "==========="
    r = requests.get(url + "deleteaccount", headers=headers_token)
    print r.content + "\n"

    print "==========" + url + "login again with same deleted account " + color.BOLD + color.CYAN + "(must fail)" + color.END + "==========="
    crypted_password    = encrypt(AKEY + "|" + password + "|" + email + "|" + datetime.now().strftime(Fa01_DATE_FORMAT))
    r = requests.post(url + "login", headers=headers_token, data=json.dumps({"loginrequest" : {"email" : email , "cryptpassword" : crypted_password}}))
    print r.content + "\n"

    sys.stdout = old_stdout
    result_string = result.getvalue()

    return result_string
