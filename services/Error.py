# coding: utf8
from enum import Enum

#@unique
class Error(Enum):
    UNKNOW                      = "0"
    SUCCESS                     = "1"
    INVALID_APIKEY              = "2"
    INVALID_TOKEN               = "3"
    INVALID_TOKEN_BLANK         = "4"
    INVALID_TOKEN_IP            = "5"
    INVALID_USER_EMAIL          = "10"
    INVALID_USER_PASSWORD       = "11"
    INVALID_TOKEN_LOGGED        = "12"
    NOT_PERMITTED               = "20"
    TOKEN_REQ_HEADER_MISSING    = "21"
    TOKEN_HEADER_MISSING        = "22"
    INVALID_JSON                = "23"
    INVALID_JSON_TYPE           = "24"
    USER_ALREADY_EXIST          = "30"
    USER_NOT_FOUND              = "31"
    USER_ALREADY_LOGGED         = "32"
    USER_PASSW_MISTMATCH        = "33"
    FILE_UNKNOW_TYPE            = "50"
    FILE_NO_PARENT_ID           = "51"
    FAILED_CREATE_GROUP         = "70"
    FAILED_DELETE_GROUP         = "71"
    FAILED_DELETE_FILE          = "73"

    EXCEPTION                   = "100"
    REDIS_KEY_UNKNOWN           = "101"
    REDIS_KEY_ALREADY_EXIST     = "102"

    def asDescription(error):
        description = {
            "0" : "error unidentified",
            "1" : "request success",
            "2" : "wrong API key",
            "3" : "invalid token",
            "4" : "token is empty",
            "5" : "token seems to taken be from another source.",
            "10" : "invalid email format",
            "11" : "invalid password format",
            "12" : "invalid token (logged)",
            "20" : "unauthorised",
            "21" : "token key missing in header. Please read the documentation",
            "22" : "token-request key missing in header. Please read the documentation",
            "23" : "invalid json",
            "24" : "invalid json, missing required keys. Please read the documentation",
            "30" : "this account has already been taken. Please use another",
            "31" : "User not found",
            "32" : "You are already disconnected",
            "33" : "wrong password for this account",
            "50" : "file type is unknow or wrong, please read the documentation and provide a known type",
            "51" : "parent uid is empty",
            "70" : "Error : Cannot create group.",
            "71" : "Error : Cannot delete group",
            "73" : "Error : Cannot delete file",
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
