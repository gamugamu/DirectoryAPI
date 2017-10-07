# coding: utf8
import datetime
import base64
import uuid

from enum import Enum
from Crypto import Random
from Crypto.Cipher import AES

import Dbb
from Error import Error

class SecurityLevel(Enum):
    NONE        = 0
    UNAUTH      = 1
    LOGGED      = 2
    SUPERUSER   = 3

class Token():

    def __init__(self):
        self.secret_uuid    = uuid.uuid4().hex
        self.date_limit     = ""
        self.right          = SecurityLevel.NONE

    def description(self):
        return str(self.secret_uuid) + "|" + str(self.right) + "|" + self.date_limit

AKEY    = 'd872eebd3967a9a00bdcb7235b491d87'
iv      = 'key-directoryAPI'

#private
def encrypt(message):
    obj = AES.new(AKEY, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))
#private
def decrypt(cipher):
    obj2 = AES.new(AKEY, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))

#public
def check_if_token_allow_access(request, securityLvl):
    crypted_token_request   = request.headers.get('Token-Request')
    try:
        print crypted_token_request
        token_request           = decrypt(str(crypted_token_request))
    except Exception as e:
        print(e)
        return Error.INVALID_APIKEY

    if securityLvl == SecurityLevel.UNAUTH:
        # security level
        if AKEY in token_request:
            return Error.SUCCESS
        else:
            return Error.INVALID_APIKEY
    #n'arrive jamais
    return Error.none

def generateToken(isValid, securityLvl):
    token = Token()
    print "generate token"
    if isValid == True:
        token.secretKey = ""
        token.dateLimit = ""
        token.right     = securityLvl.value
        Dbb.volatil_store(typeKey="TOKEN", key=token.description(), storeDict=token.dateLimit, time=100)
        print "true"

    print "stored"
    return token
