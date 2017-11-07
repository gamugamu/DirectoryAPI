# coding: utf8


import re
import json
import Dbb
import Security

from Security import SecurityLevel
from Error import Error
from bunch import bunchify
from Model.User import User
from TypeRedis import Type, Login_Req as LR
from JSONValidator import validate_json


def add_new_user(email, loginData):
    newUser         = User(email=email)
    exist           = Dbb.is_key_exist(Type.USER.name, email)

    if exist:
        return (Error.USER_ALREADY_EXIST, User().__dict__)
    else:
        newUser.id                  = Dbb.generated_key(Type.USER.name, email)
        #0 password, 1 email_token, 2 date, 3 email_user
        # TODO: SHA256
        newUser._secret_password    = Security.encrypt(loginData[0], Security.AKEY)
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
    # check avant, si l'utilisateur est déjà loggé:
    token = Security.token_from_header(request)

    if Dbb.is_key_exist(Type.SESSION.name, token):
        #il est déjà loggé
        return (Error.USER_ALREADY_LOGGED, User(), Security.generate_blank_token())

    # sinon test de loggin
    error, token_decrpt_passw = login_request_from_data(request, SecurityLevel.UNAUTH)
    error, user = perform_check_validity(error, request, retrieve_user, token_decrpt_passw)

    if error.value == Error.SUCCESS.value:
        #check password
        #TODO sha256
        user_decrpt_passw = Security.decrypt(user._secret_password, Security.AKEY)

        #0 password, 1 email_token, 2 date, 3 email_user
        if token_decrpt_passw[0] == user_decrpt_passw:
            session_token = Security.generate_Session_token(token_decrpt_passw, request)
            return (Error.SUCCESS, user, session_token)
        else:
            # Le mot-de-passe n'est pas celui du compte.
            return (Error.USER_PASSW_MISTMATCH, User(), Security.generate_blank_token())
    else:
        # le token ne doit pas être bon
        return (error, User(), Security.generate_blank_token())

def logout(from_error, request):
    if from_error.value == Error.SUCCESS.value:
        # devrait toujours être à true
        did_succed = Security.remove_Session_token(request)
         # Note USER_ALREADY_LOGOUT n'arrivera jamais car Security fait un check en amont.
        return Error.SUCCESS if did_succed else Error.USER_ALREADY_LOGOUT
    else:
        # autre erreur
        return from_error

def delete_account(from_error, request):
    if from_error.value == Error.SUCCESS.value:
        email       = Security.user_id_from_request(request)
        did_remove  = Dbb.remove_value_for_key(Type.USER.name, email)
        #clean session
        Security.remove_Session_token(request)

        return Error.SUCCESS if did_remove else Error.USER_NOT_FOUND
    else:
        return from_error

def perform_check_validity(from_error, request, callBack, login_request):
    try:
        if from_error == Error.SUCCESS:
            #0 secretKEY, 1 password, 2 email_token, 3 date, 4 email_user
            password    = login_request[1]
            token_email = login_request[2]
            user_email  = login_request[4]

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
    except Exception as e:
        print(e)
        return (Error.INVALID_TOKEN, User().__dict__)

def login_request_from_data(request, SecurityLevel):
    error, data = validate_json(request, {LR.loginrequest.name : {LR.cryptpassword.name : "", LR.email.name : ""}})

    if error == Error.SUCCESS:
        #Vérification clès API
        login_request = data[LR.loginrequest.name]
        #TODO refacto
        if set((LR.cryptpassword.name, LR.email.name)) <= set(login_request):
            crypt_passw         = login_request[LR.cryptpassword.name]
            email               = login_request[LR.email.name]
            decry_passw         = Security.decrypt(crypt_passw, Security.AKEY)
            decrpt_passw        = decry_passw.rsplit('|')
            decrpt_passw.append(email)

            return (Error.SUCCESS, decrpt_passw)
        else:
            # clès du json mauvaises
            return (Error.INVALID_JSON_TYPE, None)
    # mauvais json
    return (error, None)
