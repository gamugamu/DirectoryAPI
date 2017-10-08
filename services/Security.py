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

s_AKEY    = 'W8$04K5D98WA6WIIGRMPREOC3GTAYCV2'
s_iv      = 'black_cerberus|*'

TOKEN_UNAUTH_TIME_EXPIRATION_SEC    = 10 # secondes
Fa01_DATE_FORMAT                    = "%Y-%m-%d_%H:%M:%S"
TOKEN_REQU_HEADER                   = "token-request"
TOKEN_HEADER                        = "token"

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
        return {"hash" : self.secret_description(), "dateLimit" :  self.date_limit, "right" : str(self.right)}

    def secret_description(self):
        return encrypt(self.description(), akey=s_AKEY, _iv=s_iv)

    @staticmethod
    def decrypt_secret_description(token_value):
        return decrypt(token_value, akey=s_AKEY, _iv=s_iv)

def encrypt(message, akey=AKEY, _iv=iv):
    obj = AES.new(akey, AES.MODE_CFB, _iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))

def decrypt(cipher, akey=AKEY, _iv=iv):
    obj2 = AES.new(akey, AES.MODE_CFB, _iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))

def decrypt_user_password(crypted_password):
    try:
        decrypt_pass = decrypt(str(crypted_password))
            # security level
        if AKEY in decrypt_pass:
            return Error.SUCCESS, decrypt_pass.replace(AKEY + "|", "")
        else:
            return Error.INVALID_APIKEY, ""
    except Exception as e:
        print(e)
        return Error.INVALID_APIKEY

def check_if_token_allow_access(request, securityLvl):
    # demande de token
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
            decrypted_token = Token.decrypt_secret_description(str(token_key))
            ip_request      = request.environ['REMOTE_ADDR']

            if ip_request in decrypted_token:
                # l'ip du token correspond au clien de la requete.
                # Est-t'il repertoirié?
                token = Dbb.value_for_key(typeKey=Type.TOKEN.name, key=token_key)
                if token == None:
                    # ne devrait pas arriver. Sauf si une personne est capable de générer de faux
                    # ticket.
                    return Error.INVALID_TOKEN
                else:
                    return Error.SUCCESS
            else:
                # l'ip de la requete de correspond pas à celle du token.
                return Error.INVALID_TOKEN
        else:
            return Error.TOKEN_HEADER_MISSING
    # n'arrive jamais
    return Error.none

def generateToken(isValid, securityLvl, from_request):
    token = Token()

    if isValid == True:
        token.secret_uuid   = uuid.uuid4().hex + "|" + from_request.environ["REMOTE_ADDR"]
        token.date_limit    = (datetime.now() + timedelta(seconds=TOKEN_UNAUTH_TIME_EXPIRATION_SEC)).strftime(Fa01_DATE_FORMAT)
        token.right         = securityLvl.value

        Dbb.volatil_store(typeKey=Type.TOKEN.name, key=token.secret_description(), storeDict=token.date_limit, time=TOKEN_UNAUTH_TIME_EXPIRATION_SEC)

    return token
