# coding: utf8
from Error import Error
from bunch import bunchify

import re
import json
import Dbb

import Security
from Security import SecurityLevel
from TypeRedis import Type

from JSONValidator import validate_json

class User:
    def __init__(self, id="", email="", name="", group=[]):
        self.id                 = id
        self.email              = email
        self.name               = name
        self.group              = group
        self._secret_password   = ""

def add_new_user(email, loginData):
    newUser         = User(email=email)
    exist           = Dbb.is_key_exist(Type.USER.name, email)

    if exist:
        return (Error.USER_ALREADY_EXIST, User().__dict__)
    else:
        newUser.id                  = Dbb.generated_key(Type.USER, email)
        newUser._secret_password    = loginData["cryptpassword"]
        Dbb.store_collection(Type.USER.name, email, newUser.__dict__)

        return (Error.SUCCESS, User().__dict__)

def retrieve_user(email, loginData):
    user = Dbb.collection_for_Key(Type.USER.name, email)

    if user != None:
        #Note: redis ne sauvegarde que des dictionnaires. Le type est perdu.
        return (Error.SUCCESS, bunchify(user))
    else:
        return (Error.USER_NOT_FOUND, User().__dict__)


def create_account(from_error, request):
    return perform_check_validity(from_error, request, add_new_user)[0]

def login(from_error, request):
    error, user = perform_check_validity(from_error, request, retrieve_user)

    if error.value == Error.INVALID_USER_PASSWORD.value:
        print "WRONG_USER_PASSWORD 1"
        return (Error.WRONG_USER_PASSWORD, user, Security.generate_black_token())
    else:
        #check password

        print "pass " + user._secret_password
        print request
        data_from_request = validate_json(request)[1]["loginrequest"]["cryptpassword"]
        print "data ****"
        print data_from_request
        error, decrpt_passw = Security.decrypt_user_password(user._secret_password)
        decrpt_passw        = decrpt_passw.rsplit('|')
        print "decrpt_passw ****"
        print decrpt_passw
        error, check = Security.decrypt_user_password(data_from_request)
        check        = check.rsplit('|')
        print "check"
        print check

        if decrpt_passw[0] != check[0]:
            return (Error.WRONG_USER_PASSWORD, User(), new_token)

        new_token = Security.generate_Session_token(decrpt_passw, request)

        return (error, user, new_token)

def perform_check_validity(from_error, request, callBack):
    if from_error == Error.SUCCESS:
        error, data = validate_json(request)

        if error == Error.SUCCESS:
            #Vérification clès API
            login_request       = data["loginrequest"]

            if set(("cryptpassword", "email")) <= set(login_request):
                crypt_passw      = login_request["cryptpassword"]
                email            =  data["loginrequest"]["email"]

                error, decry_passw  = Security.decrypt_user_password(crypt_passw)
                decrpt_passw = decry_passw.rsplit('|')

                #0 password, 1 email, 2 date
                if len(decrpt_passw) == 3 and decrpt_passw[1] == email:
                    if error == Error.SUCCESS:
                        #TODO validation type

                        #Validation email format
                        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                            return (Error.INVALID_USER_EMAIL, User().__dict__)

                        #Validation password format. Note: vérifie d'abord que l'email n'existe pas.
                        if not re.match(r"^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{10,}$", decrpt_passw[0]):
                            return (Error.INVALID_USER_PASSWORD, User().__dict__)

                        #Validation uniquness
                        return callBack(email, login_request)
                    #token invalid. Email n'est pas retrouvé.
                else:
                    return (Error.INVALID_TOKEN, User().__dict__)

            else:
                # clès du json mauvaises
                return (Error.INVALID_JSON_TYPE, User().__dict__)
        # mauvais json
        return (error, User().__dict__)
    else:
        # erreur déjà présente. Pas de check
        return (from_error, User().__dict__)
