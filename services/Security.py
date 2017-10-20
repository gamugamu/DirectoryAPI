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
TOKEN_AUTH_TIME_EXPIRATION_SEC      = 10000 # secondes

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
        self.right          = SecurityLevel.NONE.value

    def description(self):
        if self.secret_uuid == "":
            #token invalide
            return ""
        else:
            return str(self.secret_uuid) + "|" + str(self.right) + "|" + self.date_limit

    def as_dict(self):
        return {
            "hash" : self.secret_description(),
            "dateLimit" :  self.date_limit,
            "right" : str(self.right)}

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

def encrypt_with_security_level(data_to_encrypt, lvSecurity):
    _akey = AKEY if lvSecurity.value == SecurityLevel.UNAUTH.value else s_AKEY
    _iv   = iv if lvSecurity.value == SecurityLevel.UNAUTH.value else s_iv

    return encrypt(str(data_to_encrypt), _akey, _iv)

def decrypt_with_security_level(data_to_decrypt, lvSecurity):
    try:
        _akey = AKEY if lvSecurity.value == SecurityLevel.UNAUTH.value else s_AKEY
        _iv   = iv if lvSecurity.value == SecurityLevel.UNAUTH.value else s_iv

        decrypt_pass = decrypt(str(data_to_decrypt), _akey, _iv)
            # security level
        return decrypt_pass.replace(_akey + "|", "")

    except Exception as e:
        print(e)
        return ""

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
            token_key       = request.headers.get(TOKEN_HEADER)

            if token_key == None:
                return Error.INVALID_TOKEN_BLANK
            else:
                decrypted_token = Token.decrypt_secret_description(str(token_key))

                token_data  = decrypted_token.split("|")
                right       = token_data[2]
                type_key    = Type.TOKEN.name if right <= SecurityLevel.UNAUTH.value else Type.SESSION.name
                token       = Dbb.value_for_key(typeKey=type_key, key=token_key)

                if token == None:
                    # ne devrait pas arriver. Sauf si une personne est capable de générer de faux
                    # ticket.
                    return Error.INVALID_TOKEN
                else:
                    return Error.SUCCESS

        else:
            return Error.TOKEN_HEADER_MISSING
    # n'arrive jamais
    return Error.UNKNOW

def generateToken(isValid, securityLvl, from_request):
    token = Token()

    if isValid == True:
        token.secret_uuid   = uuid.uuid4().hex
        token.date_limit    = (datetime.now() + timedelta(seconds=TOKEN_UNAUTH_TIME_EXPIRATION_SEC)).strftime(Fa01_DATE_FORMAT)
        token.right         = securityLvl.value

        Dbb.volatil_store(
            typeKey     = Type.TOKEN.name,
            key         = token.secret_description(),
            storeDict   = token.date_limit,
            time        = TOKEN_UNAUTH_TIME_EXPIRATION_SEC)

    return token

def generate_Session_token(secret_keys, from_request):
    token = Token()
    print "secret_keys", secret_keys
    token.secret_uuid   = uuid.uuid4().hex + "|" + secret_keys[3] # account
    token.date_limit    = (datetime.now() + timedelta(seconds=TOKEN_UNAUTH_TIME_EXPIRATION_SEC)).strftime(Fa01_DATE_FORMAT)
    token.right         = SecurityLevel.LOGGED.value

    Dbb.volatil_store(
        typeKey     = Type.SESSION.name,
        key         = token.secret_description(),
        storeDict   = token.date_limit,
        time        = TOKEN_AUTH_TIME_EXPIRATION_SEC)

    return token

def remove_Session_token(from_request):
    token = token_from_header(from_request)
    return Dbb.remove_value_for_key(Type.SESSION.name, token)

def generate_blank_token():
    return Token()

# >= .UNAUTH
def user_id_from_request(request):
    crypt_token     = token_from_header(request)
    decrypt_token   = decrypt_with_security_level(crypt_token, SecurityLevel.LOGGED)
    data_token      = decrypt_token.split("|")

    return data_token[1] #account

def token_from_header(request):
    return request.headers[TOKEN_HEADER]

def generate_date_now():
    return datetime.now().strftime(Fa01_DATE_FORMAT)
