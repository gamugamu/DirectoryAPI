# coding: utf8
from flask import request
from Error import Error

import json

def validate_json(request):
    try:
        data = request.get_json()
        print data
        print(data['loginrequest'])
        return (Error.SUCCESS, "data")

    except Exception as e:
        print(e)
        return (Error.INVALID_JSON, "")


    return (Error.NONE, "")
