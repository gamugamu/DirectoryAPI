# coding: utf8
from enum import Enum
import enum

class Login_Req(Enum):
    loginrequest    = 0,
    cryptpassword   = 1,
    email           = 2

#@unique
class Type(Enum):
    TOKEN       = 0,
    SESSION     = 1,
    USER        = 2,


class FileType(enum.IntEnum):
    UNKNOW      = 0,
    GROUP       = 1,
    FOLDER      = 2,
    FILE        = 3 # bucket
