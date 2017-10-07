# coding: utf8
from enum import Enum

#@unique
class Error(Enum):
    NONE                    = 0
    SUCCESS                 = 1
    INVALID_APIKEY          = 2
    INVALID_TOKEN           = 3
    INVALID_USER_EMAIL      = 4
    INVALID_USER_PASSWORD   = 5
    INVALID_TOKEN           = 6
    NOT_PERMITTED           = 7

    def asDescription(error):
        description = [
            "error unidentified",
            "request success",
            "wrong API key",
            "invalid token",
            "invalid email",
            "invalid password",
            "invalid token (logged)",
            "unauthorised"
            ]
        desc                = ErrorDescription()
        desc.code           = error.value
        desc.description    = description[error.value]

        return desc

class ErrorDescription:
    code        = 0
    description = ""
