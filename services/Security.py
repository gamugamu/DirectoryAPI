# coding: utf8
import datetime
from datetime import datetime, timedelta
import base64
import uuid

from enum import Enum
from Crypto import Random
from Crypto.Cipher import AES

import Dbb
from TypeRedis import Type
from Error import Error

AKEY    = 'd872eebd3967a9a00bdcb7235b491d87'
iv      = 'key-directoryAPI'
TOKEN_TIME_EXPIRATION_SEC   = 4800 # 30 minutes
Fa01_DATE_FORMAT            = "%Y-%m-%d_%H:%M:%S"
TOKEN_REQU_HEADER           = "token-request"
TOKEN_HEADER                = "token"

class SecurityLevel(Enum):
    NONE        = 0
    UNAUTH      = 1
    LOGGED      = 2
    SUPERUSER   = 3

class Token():

    def __init__(self):
        self.secret_uuid    = ""
        self.date_limit     = ""
        self.right          = SecurityLevel.NONE

    def description(self):
        return str(self.secret_uuid) + "|" + str(self.right) + "|" + self.date_limit

    def as_dict(self):
        return {"hash" : self.description(), "dateLimit" :  self.date_limit, "right" : str(self.right)}

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
    # demande de token
    print request.headers
    if securityLvl == SecurityLevel.NONE:
        if TOKEN_REQU_HEADER in request.headers:
            crypted_token_request = request.headers.get(TOKEN_REQU_HEADER)

            try:
                token_request = decrypt(str(crypted_token_request))
                # security level
                if AKEY in token_request:
                    return Error.SUCCESS
                else:
                    return Error.INVALID_APIKEY

            except Exception as e:
                print(e)
                return Error.INVALID_APIKEY
        else:
            return Error.TOKEN_REQ_HEADER_MISSING
    else:
        ## securityLvl <= SecurityLevel.UNAUTH:
        if TOKEN_HEADER in request.headers:
            token_key  = request.headers.get(TOKEN_HEADER)
            token      = Dbb.valueForKey(typeKey=Type.TOKEN.name, key=token_key)
            if token == None:
                return Error.INVALID_TOKEN
            else:
                return Error.SUCCESS
        else:
            return Error.TOKEN_HEADER_MISSING
    # n'arrive jamais
    return Error.none

def generateToken(isValid, securityLvl):
    token = Token()

    if isValid == True:
        token.secret_uuid   = uuid.uuid4().hex
        token.date_limit    = (datetime.now() + timedelta(seconds=TOKEN_TIME_EXPIRATION_SEC)).strftime(Fa01_DATE_FORMAT)
        token.right         = securityLvl.value
        Dbb.volatil_store(typeKey=Type.TOKEN.name, key=token.description(), storeDict=token.date_limit, time=TOKEN_TIME_EXPIRATION_SEC)

    return token
