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

AKEY        = 'd872eebd3967a9a00bdcb7235b491d87'
BLOCK_SIZE  = 16

TOKEN_UNAUTH_TIME_EXPIRATION_SEC    = 100 # secondes
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
        self.owner          = ""

    def description(self):
        if self.secret_uuid == "":
            #token invalide
            return ""
        else:
            return str(self.secret_uuid) + "|" + str(self.right) + "|" + self.date_limit + '|' + self.owner

    def as_dict(self):
        return {
            "hash" : self.secret_description(),
            "dateLimit" :  self.date_limit,
            "right" : str(self.right)}

    def secret_description(self):
        #TODO Sha256
        return self.description()

    @staticmethod
    def decrypt_secret_description(token_value):
        #TODO Sha256
        return token_value

def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length)*length

def unpad(data):
    return data[:-ord(data[-1])]

def encrypt(message, passphrase):
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV, segment_size=128)
    return base64.b64encode(IV + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV, segment_size=128)
    return unpad(aes.decrypt(encrypted[BLOCK_SIZE:]))

def check_if_token_allow_access(request, securityLvl):
    # demande de token
    if securityLvl == SecurityLevel.NONE:
        if TOKEN_REQU_HEADER in request.headers:
            crypted_token_request = request.headers.get(TOKEN_REQU_HEADER)
            try:
                token_request = decrypt(crypted_token_request, AKEY)
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
                try:

                    decrypted_token = Token.decrypt_secret_description(str(token_key))
                    token_data  = decrypted_token.split("|")
                    right       = int(token_data[1])
                    #print("Right***", token_data)
                    type_key    = Type.TOKEN.name if right <= SecurityLevel.UNAUTH.value else Type.SESSION.name
                    token       = Dbb.value_for_key(typeKey=type_key, key=token_key)

                    if token == None:
                        # ne devrait pas arriver. Sauf si une personne est capable de générer de faux
                        # ticket.
                        return Error.INVALID_TOKEN
                    else:
                        return Error.SUCCESS
                except Exception as e:
                    print(e)
                    return Error.INVALID_APIKEY
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

    token.secret_uuid   = uuid.uuid4().hex
    token.date_limit    = (datetime.now() + timedelta(seconds=TOKEN_UNAUTH_TIME_EXPIRATION_SEC)).strftime(Fa01_DATE_FORMAT)
    token.right         = SecurityLevel.LOGGED.value
    token.owner         = secret_keys[2] # account

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
    try:
        #TODO sha256
        crypt_token     = token_from_header(request)
        data_token      = crypt_token.split("|")
        #decrypt_token   = decrypt(crypt_token, AKEY)
        #data_token      = decrypt_token.split("|")
        return data_token[3] #account
    except Exception as e:
        print(e)
        return Error.INVALID_APIKEY

def token_from_header(request):
    return request.headers[TOKEN_HEADER]

def generate_date_now():
    return datetime.now().strftime(Fa01_DATE_FORMAT)
