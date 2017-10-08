# coding: utf8
from Error import Error
import re

import json
from bunch import bunchify
import Dbb
import Security

from JSONValidator import validate_json

class User:
    def __init__(self, id="", email="", name="", group=[]):
        self.id     = id
        self.email  = email
        self.name   = name
        self.group  = group

def add_new_user(email, loginData):
    newUser         = User(email=email)
    exist           = Dbb.is_key_exist("USER", email)

    if exist:
        return (Error.USER_ALREADY_EXIST, User().__dict__)
    else:
        newUser.id = Dbb.generated_key("USER", email)
        Dbb.store_collection("USER", email, newUser.__dict__)

        return (Error.SUCCESS, User().__dict__)

def retrieve_user(email, loginData):
    user = Dbb.collection_for_Key("USER", email)

    if user != None:
        #Note: redis ne sauvegarde que des dictionnaires. Le type est perdu.
        return (Error.SUCCESS, bunchify(user))
    else:
        return (Error.USER_NOT_FOUND, User().__dict__)


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
                    return (Error.INVALID_USER_EMAIL, User().__dict__)

                #Validation password format. Note: vérifie d'abord que l'email n'existe pas.
                if not re.match(r"^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{10,}$", decry_passw):
                    return (Error.INVALID_USER_PASSWORD, User().__dict__)

                #Validation uniquness
                return callBack(email, loginData)

        return (error, User().__dict__)
    else:
        return (from_error, User().__dict__)
