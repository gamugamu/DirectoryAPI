# coding: utf8
from Error import Error

import json
from JSONValidator import validate_json

def create_account(from_error, request):
    if from_error == Error.SUCCESS:
        print "REQUEST DATA"
        error, data = validate_json(request)
        return error
    else:
        return from_error
