# coding: utf8
from Error import Error
from bunch import bunchify

import re
import json
import Dbb

import Security
from Security import SecurityLevel
from TypeRedis import Type, Login_Req as LR

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
        newUser.id                  = Dbb.generated_key(Type.USER.name, email)
        #0 password, 1 email_token, 2 date, 3 email_user
        newUser._secret_password    = Security.encrypt_with_security_level(loginData[0], SecurityLevel.LOGGED)
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
    error, decrpt_passw = login_request_from_data(request, SecurityLevel.UNAUTH)
    return perform_check_validity(error, request, add_new_user, decrpt_passw)[0]

def login(from_error, request):
    error, token_decrpt_passw = login_request_from_data(request, SecurityLevel.UNAUTH)
    error, user = perform_check_validity(error, request, retrieve_user, token_decrpt_passw)

    if error.value == Error.SUCCESS.value:
        #check password
        user_decrpt_passw = Security.decrypt_with_security_level(user._secret_password, SecurityLevel.LOGGED)
        #print "COMPARE: ", token_decrpt_passw, "XXX", user._secret_password, "XXX", user_decrpt_passw

        #0 password, 1 email_token, 2 date, 3 email_user
        #print token_decrpt_passw[0], user_decrpt_passw, token_decrpt_passw[0] == user_decrpt_passw
        if token_decrpt_passw[0] == user_decrpt_passw:
            #new_token = Security.generate_Session_token(user_decrpt_passw, request)
            session_token = Security.generate_Session_token(token_decrpt_passw, request)
            return (Error.SUCCESS, user, session_token)
        else:
            # Le mot-de-passe n'est pas celui du compte.
            return (Error.WRONG_USER_PASSWORD, User(), Security.generate_blank_token())
    else:
        return (error, user, Security.generate_blank_token())

def logout(from_error, request):
    if from_error.value == Error.SUCCESS.value:
        did_succed = Security.remove_Session_token(request)
         # Note USER_ALREADY_LOGOUT n'arrivera jamais car Security fait un check en amont.
        return Error.SUCCESS if did_succed else Error.USER_ALREADY_LOGOUT
    else:
        return from_error

def perform_check_validity(from_error, request, callBack, login_request):
    if from_error == Error.SUCCESS:
        #0 password, 1 email_token, 2 date, 3 email_user
        password    = login_request[0]
        token_email = login_request[1]
        user_email  = login_request[3]

        if token_email == user_email:
            #Validation email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
                return (Error.INVALID_USER_EMAIL, User().__dict__)

            #Validation password format. Note: vérifie d'abord que l'email n'existe pas.
            if not re.match(r"^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{10,}$", password):
                return (Error.INVALID_USER_PASSWORD, User().__dict__)

            #Validation uniquness
            return callBack(user_email, login_request)
        else:
            #token invalid. Email n'est pas retrouvé.
            return (Error.INVALID_TOKEN, User().__dict__)
    else:
        # erreur déjà présente. Pas de check
        return (from_error, User().__dict__)

def login_request_from_data(request, SecurityLevel):
    error, data = validate_json(request)

    if error == Error.SUCCESS:
        #Vérification clès API
        login_request = data[LR.loginrequest.name]

        if set((LR.cryptpassword.name, LR.email.name)) <= set(login_request):
            crypt_passw         = login_request[LR.cryptpassword.name]
            email               = login_request[LR.email.name]
            decry_passw         = Security.decrypt_with_security_level(crypt_passw, lvSecurity=SecurityLevel)
            decrpt_passw        = decry_passw.rsplit('|')
            decrpt_passw.append(email)

            return (Error.SUCCESS, decrpt_passw)
        else:
            # clès du json mauvaises
            return (Error.INVALID_JSON_TYPE, None)
    # mauvais json
    return (error, None)
