# coding: utf8
from enum import Enum

#@unique
class Error(Enum):
    NONE                        = 0
    SUCCESS                     = 1
    INVALID_APIKEY              = 2
    INVALID_TOKEN               = 3
    INVALID_USER_EMAIL          = 4
    INVALID_USER_PASSWORD       = 5
    INVALID_TOKEN_LOGGED        = 6
    NOT_PERMITTED               = 7
    TOKEN_HEADER_MISSING        = 8
    TOKEN_REQ_HEADER_MISSING    = 9
    INVALID_JSON                = 10

    def asDescription(error):
        description = [
            "error unidentified",
            "request success",
            "wrong API key",
            "invalid token",
            "invalid email",
            "invalid password",
            "invalid token (logged)",
            "unauthorised",
            "token key missing in header. Please read the documentation",
            "token-request key missing in header. Please read the documentation",
            "invalid json"
            ]
        desc                = ErrorDescription()
        desc.code           = error.value
        desc.description    = description[error.value]

        return desc

class ErrorDescription:
    code        = 0
    description = ""
