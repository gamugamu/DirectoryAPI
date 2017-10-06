
import base64
import datetime
from Crypto import Random
from Crypto.Cipher import AES


class SecurityLevel(Enum):
    UNAUTH      = 0
    LOGGED      = 1
    SUPERUSER   = 2

AKEY    = 'd872eebd3967a9a00bdcb7235b491d87'
iv      = 'key-directoryAPI'


def encrypt(message):
    obj = AES.new(AKEY, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))

def decrypt(cipher):
    obj2 = AES.new(AKEY, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))

def check_if_token_allow_access(request, securityLevel):
    value = request.headers.get('Token-Request')
    print request.headers
    print value
    print decrypt(str(value))
