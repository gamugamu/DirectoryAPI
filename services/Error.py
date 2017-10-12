# coding: utf8
from enum import Enum

#@unique
class Error(Enum):
    NONE                        = "0"
    SUCCESS                     = "1"
    INVALID_APIKEY              = "2"
    INVALID_TOKEN               = "3"
    INVALID_USER_EMAIL          = "10"
    INVALID_USER_PASSWORD       = "11"
    INVALID_TOKEN_LOGGED        = "12"
    WRONG_USER_PASSWORD         = "13"
    NOT_PERMITTED               = "20"
    TOKEN_REQ_HEADER_MISSING    = "21"
    TOKEN_HEADER_MISSING        = "22"
    INVALID_JSON                = "23"
    INVALID_JSON_TYPE           = "24"
    USER_ALREADY_EXIST          = "30"
    USER_NOT_FOUND              = "31"
    USER_ALREADY_LOGOUT         = "32"
    USER_ALREADY_LOGGED         = "33"
    FAILED_CREATE_GROUP         = "70"
    FAILED_DELETE_GROUP         = "71"
    EXCEPTION                   = "100"
    REDIS_KEY_UNKNOWN           = "101"
    REDIS_KEY_ALREADY_EXIST     = "102"

    def asDescription(error):
        description = {
            "0" : "error unidentified",
            "1" : "request success",
            "2" : "wrong API key",
            "3" : "invalid token",
            "10" : "invalid email format",
            "11" : "invalid password format",
            "12" : "invalid token (logged)",
            "13" : "wrong password for this account",
            "20" : "unauthorised",
            "21" : "token key missing in header. Please read the documentation",
            "22" : "token-request key missing in header. Please read the documentation",
            "23" : "invalid json",
            "24" : "invalid json, missing required keys. Please read the documentation",
            "30" : "this account has already been taken. Please use another",
            "31" : "User not found",
            "32" : "You are already disconnected",
            "33" : "You are already logged",
            "70" : "Error : Cannot create group.",
            "71" : "Error : Cannot delete group",
            "100": "Exception while communicating with BackBlaze",
            "101": "Exception, data not found in database (Redis)",
            "102": "Exception, Key already exist in (Redis) database"
            }
        desc                = ErrorDescription()
        desc.code           = error.value
        desc.description    = description[error.value]

        return desc

class ErrorDescription:
    code        = 0
    description = ""
