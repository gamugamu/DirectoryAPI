# coding: utf8

import base64
import datetime
from Error import Error
from enum import Enum
from Crypto import Random
from Crypto.Cipher import AES


class SecurityLevel(Enum):
    NONE        = 0
    UNAUTH      = 1
    LOGGED      = 2
    SUPERUSER   = 3

class Token():
    secretKey   = ""
    dateLimit   = ""
    right       = ""

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
        token_request           = decrypt(str(crypted_token_request))
    except:
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

    if isValid == True:
        token.secretKey = ""
        token.dateLimit = ""
        token.right     = securityLvl.value

    return token
