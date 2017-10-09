# coding: utf8
from enum import Enum

class Login_Req(Enum):
    loginrequest    = 0,
    cryptpassword   = 1,
    email           = 2

#@unique
class Type(Enum):
    TOKEN       = 0,
    SESSION     = 1,
    USER        = 2
