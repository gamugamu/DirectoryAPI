# coding: utf8
from Error import Error
import re

import json
import Dbb
import Security

from JSONValidator import validate_json


def add_new_user(email, loginData):
    if Dbb.store_collection_if_unique("USER", email, loginData) != True:
        return (Error.USER_ALREADY_EXIST, None)
    else:
        return (Error.SUCCESS, None)

def retrieve_user(email, loginData):
    user = Dbb.collection_for_Key("USER", email)
    if user != None:
        return (Error.SUCCESS, user)
    else:
        return (Error.USER_NOT_FOUND, None)


def create_account(from_error, request):
    return perform_check_validity(from_error, request, add_new_user)[0]

def login(from_error, request):
    return perform_check_validity(from_error, request, retrieve_user)

def perform_check_validity(from_error, request, callBack):
    if from_error == Error.SUCCESS:
        error, data = validate_json(request)

        if error == Error.SUCCESS:
            #Vérification clès API
            crypt_passw         = data["loginrequest"]["cryptpassword"]
            error, decry_passw  = Security.decrypt_user_password(crypt_passw)

            if error == Error.SUCCESS:
                #TODO validation type

                #Validation password:
                email       =  data["loginrequest"]["email"]
                loginData   = data["loginrequest"]

                #Validation email format
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return (Error.INVALID_USER_EMAIL, None)

                #Validation password format. Note: vérifie d'abord que l'email n'existe pas.
                if not re.match(r"^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{10,}$", decry_passw):
                    return (Error.INVALID_USER_PASSWORD, None)

                #Validation uniquness
                return callBack(email, loginData)

        return (error, None)
    else:
        return (from_error, None)
