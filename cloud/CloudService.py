# coding: utf8

import base64
import json
import requests
import hashlib
from bunch import bunchify, unbunchify
from services.JSONValidator import validate_json

from services.TypeRedis import Type
from CloudType import Group
from services import Dbb
from services.Security import generate_date_now
from services.TypeRedis import FileType
from services.Error import Error
from Model.File import FilePayload, FileHeader

class CloudService:
    id_and_key          = '191c9cd81236:001a7ee30eaf15bbda5fa0b1d7fb06210f5bcadd3e'
    account_id          = "191c9cd81236" # Obtained from your B2 account page
    basic_auth_string   = 'Basic ' + base64.b64encode(id_and_key)

    def __init__(self):
        # renseigné via le cloud
        self.auth_token     = ""
        self.api_url        = ""
        self.download_url   = ""
        self.main_bucket_id = ""

    def connect_to_cloud(self):
        header = { 'Authorization': CloudService.basic_auth_string }
        r = requests.get(   'https://api.backblazeb2.com/b2api/v1/b2_authorize_account',
                            headers = header)
        data = json.loads(r.content)

        self.auth_token      = data['authorizationToken']
        self.api_url         = data['apiUrl']
        self.download_url    = data['downloadUrl']

    def create_file(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"filetype": {"name" : "", "type" : "", "parentId" : ""}})

            if error == Error.SUCCESS:
                file_name = data["filetype"]["name"]
                file_type = data["filetype"]["type"]
                parent_id = data["filetype"]["parentId"]

                if file_type == int(FileType.GROUP):
                    return self.create_new_bucket(file_name, owner_id)
                else: # file or folder
                    error, bucket, uri_path = self.retrieve_bucket_data_from_graph(parent_id)

                      # Si c'est un dossier, le nom doit être formaté avec un .bzEmpty
                    if file_type == int(FileType.FOLDER):
                        file_name = self.append_as_folder(file_name)

                    if error == Error.SUCCESS:
                        return self.create_file_in_bucket(bunchify(bucket), owner_id, file_name, uri_path, parent_id)
                    else:
                        return error, FilePayload()
            else:
                return error, FilePayload()
        else:
            return from_error, FilePayload()

    def delete_file(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"fileid": {"type" : "", "uid" : ""}})

            if error == Error.SUCCESS:
                file_id     = data["fileid"]["uid"]
                file_type   = data["fileid"]["type"]

                if file_type == int(FileType.GROUP):
                    # le bucket doit être vide afin d'effacer son contenu
                    # (oui, c'est complétement débile!)
                    return self.delete_bucket(file_id, owner_id)
                else: # file or folder
                    file_name = data["fileid"]["name"]

                    e, r = self.delete_file_from_server(file_id, file_name)

                    if e == Error.SUCCESS and r.status_code == 200:
                        # child
                        self.remove_file_from_parent(file_id)
                        return Error.SUCCESS
                    else:
                        return Error.FAILED_DELETE_FILE
        else:
            return error

    def modify_file(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:

            error, data = validate_json(request, {"filepayload": {
            "type" : "", "name" : "", "uid" : "", "parentId" : "", "owner" : "",
            "title" : "", "date" : "", "rules" : "", "payload" : ""}})

            if error == Error.SUCCESS:
                data        = data["filepayload"]
                pattern_key = "*" + data["uid"]
                key         = Dbb.value_for_key(key=pattern_key)

                if key is not None:
                    key = key.next()

                Dbb.store_collection(key=key, storeDict=data)

            return error
        else:
            return error

    def get_files_header(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"fileids": []});
            list_uid = [];

            for uid in data["fileids"]:
                value = Dbb.collection_for_Pattern("*" + uid)

                if value is not None:
                    value = unbunchify(FileHeader.dictionnary_to_fileHeader(value))
                    list_uid.append(value)

            if len(list_uid) == 0:
                return Error.REDIS_KEY_UNKNOWN, FileHeader().__dict__
            else:
                return Error.SUCCESS, list_uid
        else:
            return error, FileHeader().__dict__

    def delete_file_from_server(self, file_id, file_name):
        params = {  'fileName': file_name,
                    'fileId': file_id }

        e, r, response = self.simplified_post_request(uri_name="b2_delete_file_version", post_data=params)
        return e, r

    # limité à 10
    def create_new_bucket(self, bucket_name, owner_id):
        print "Try to create a new bucket...", bucket_name
        params = {  'accountId': CloudService.account_id,
                    'bucketName': bucket_name,
                    'bucketType': "allPrivate" }

        e, r, response = self.simplified_post_request(uri_name="b2_create_bucket", post_data=params)

        if e == Error.SUCCESS and r.status_code == 200:
            try:
                bucket_id           = response["bucketId"]
                bucket_name         = response["bucketName"]

                group = FilePayload(uid       = bucket_id,
                                    name      = bucket_name,
                                    type      = FileType.GROUP.value,
                                    date      = generate_date_now(),
                                    owner     = [owner_id])
                # store
                self.add_user_ownership(owner_id, bucket_id)
                Dbb.store_collection(FileType.GROUP.name, bucket_id, group.__dict__)
                return Error.SUCCESS, group

            except Exception as e:
                print "ERROR", e
                print "could'nt create bucket"
                return Error.FAILED_CREATE_GROUP, FilePayload()

        else:
            print "error from BackBlaze ", response
            return Error.FAILED_CREATE_GROUP, FilePayload()

    #supprime le bucket
    def delete_bucket(self, bucket_id, owner_id):
        try:
            bucket_redis_name = bucket_id
            e = self.recursively_delete_all_files_in_bucket(bucket_id)

            if e == Error.SUCCESS:
                # store
                params = {  'accountId': CloudService.account_id,
                            'bucketId': bucket_id}

                e, r, response = self.simplified_post_request(uri_name="b2_delete_bucket", post_data=params)

                # fichier supprimée, clean de la bdd
                if e == Error.SUCCESS and r.status_code == 200:
                    Dbb.remove_value_for_key(FileType.GROUP.name, bucket_id)
                    self.remove_user_ownership(owner_id, bucket_id)
                    return Error.SUCCESS
                else:
                    print "can't delete bucket ", response
                    return Error.FAILED_DELETE_GROUP
            else:
                print "can't delete files in bucket ", response
                return Error.FAILED_DELETE_GROUP

        except Exception as e:
            print "ERROR_DELETE_BUCKET", e
            return Error.FAILED_DELETE_GROUP

    def recursively_delete_all_files_in_bucket(self, bucket_id):
        # store
        params          = {'bucketId': bucket_id}
        e, r, response  = self.simplified_post_request(uri_name="b2_list_file_names", post_data=params)

        #R2cupérations de la listes des fichiers + suppresion
        if e == Error.SUCCESS and r.status_code == 200:
            for file_list in response["files"]:
                file_id = file_list["fileId"]
                e, r    = self.delete_file_from_server(file_id, file_list["fileName"])

                if e == Error.SUCCESS and r.status_code == 200:
                    Dbb.remove_with_key_pattern(p_key= "*|" + file_id)
                else:
                    return Error.FAILED_DELETE_FILE
            #les suppressions ont réussies
            return Error.SUCCESS
        else:
            return e

    def retrieve_bucket_data_from_graph(self, parent_id, uri_path=""):
        b_key   = "*_" + parent_id
        f_key   = "*|" + parent_id
        key     = ""

        # le patterne est différent pour retrouver un folder ou un bucket
        # il y a plus de chance de tomber sur un folder que sur un bucket.
        if Dbb.is_key_exist_forPattern(f_key):
            key = f_key

        elif Dbb.is_key_exist_forPattern(b_key):
            key = b_key

        value = Dbb.value_for_key(key=key)

        try:
            parent_key = value.next()

            if FileType.GROUP.name in parent_key:
                # bucket trouvé. N'as pas de parent.
                bucket = Dbb.collection_for_Key(key=parent_key)
                return Error.SUCCESS, Dbb.collection_for_Key(key=parent_key), uri_path
            else:
                # note, un fichier ne peut pas contenir un autre fichier,
                # donc forcement un folder
                folder      = Dbb.collection_for_Key(key=parent_key)
                folder      = bunchify(folder)
                uri_path    = self.append_path(folder.name, uri_path)

                return self.retrieve_bucket_data_from_graph(folder.parentId, uri_path)

        except Exception as e:
            print "EXCEPTION: ", e, key, "is not from graph"
            return Error.REDIS_KEY_UNKNOWN, None, ""

    def create_file_in_bucket(self, bucket, owner_id, file_name, uri_path, parentId):
        # Vérifie qu'il a bien un parent (devrait toujours être a true)
        if bucket is not None:
            # Et vérifie qu'il n'y a pas de doublon
            #TODO faire le check

            uri_path      = self.append_path(uri_path, file_name)
            full_uri_path = self.append_path(bucket.name, uri_path)

            is_entry_already_exist = Dbb.is_key_exist_forPattern("*|" + full_uri_path + "|*")

            # Si il n'existe pas d'entrée, alors on peux créer le fichier
            if is_entry_already_exist == False:

                params = { 'bucketId' : bucket.uid}
                e, r, response = self.simplified_post_request(uri_name="b2_get_upload_url", post_data=params)

                if e == Error.SUCCESS and r.status_code == 200:
                    auth_token  = response["authorizationToken"]
                    uploadUrl   = response["uploadUrl"]

                    # now send data
                    file_data           = ""
                    file_name           = file_name
                    content_type        = "text/plain"
                    sha1_of_file_data   = hashlib.sha1(file_data).hexdigest()

                    header = {
                        'Authorization'     : auth_token,
                        'X-Bz-File-Name'    : uri_path,
                        'Content-Type'      : content_type,
                        'X-Bz-Content-Sha1' : sha1_of_file_data }

                    e, r, response = self.simplified_post_request(  full_url        = uploadUrl,
                                                                    post_data       = file_data,
                                                                    header          = header,
                                                                    need_dumping    = False)

                    if e == Error.SUCCESS and r.status_code == 200:
                        # creation du fichier redis
                        if parentId == "":
                            parentId = bucket.uid

                        file_id = response["fileId"]
                        file_   = FilePayload(  uid       = file_id,
                                                name      = self.sanityse_path(file_name),
                                                type      = FileType.FILE.value,
                                                date      = generate_date_now(),
                                                owner     = [owner_id],
                                                parentId  = parentId)

                        full_uri_path       = self.sanityse_path(full_uri_path)
                        redis_id            = "|" + full_uri_path + "|" + file_id
                        bucket.childsId     = Dbb.appendedValue(bucket.childsId, file_id)

                        #update data
                        Dbb.store_collection(FileType.FILE.name, redis_id, file_.__dict__)
                        Dbb.store_collection(FileType.GROUP.name, bucket.uid, unbunchify(bucket))

                        return Error.SUCCESS, file_
                    else:
                        # le bucket a été retrouvé mais le fichier n'a pas pu être crée.
                        return Error.EXCEPTION, FilePayload()
                else:
                    # le bucket n'est pas connu par backblaze
                    print "bucket not found ***"
                    return Error.NONE, FilePayload()
            else:
                # l'entrée existe déjà pour ce fichier
                return Error.REDIS_KEY_ALREADY_EXIST, FilePayload()


    #helper
    def simplified_post_request(self, uri_name=None, post_data=None, full_url=None, header=None, need_dumping=True):
        try:
            if full_url is not None:
                url = full_url
            else:
                url = '%s/b2api/v1/%s' % (self.api_url, uri_name)

            if header is None:
                header = { 'Authorization': self.auth_token }

            if need_dumping == True:
                post_data = json.dumps(post_data)

            r = requests.post(  url,
                                data    = post_data,
                                headers = header)

            return Error.SUCCESS, r, json.loads(r.content)

        except Exception as e:
            return Error.EXCEPTION, None, None

    def append_path(self, path, new_value):
        if path == "":
            return new_value
        else:
            new_path = path + "/" + new_value
            return new_path.replace("//", "/")

    def sanityse_path(self, path):
        return path.replace("/.bzEmpty", "")

    def append_as_folder(self, path):
        return path + "/.bzEmpty"

    def add_user_ownership(self, user_id, group_id):
        user            = Dbb.collection_for_Key(typeKey=Type.USER.name, key=user_id)
        user["group"]   = Dbb.appendedValue(user["group"], group_id)

        Dbb.store_collection(Type.USER.name, user_id, user)

    def remove_user_ownership(self, user_id, group_id):
        user            = Dbb.collection_for_Key(typeKey=Type.USER.name, key=user_id)
        user["group"]   = Dbb.removedValue(user["group"], group_id)

        Dbb.store_collection(Type.USER.name, user_id, user)

    def remove_file_from_parent(self, file_id):
        file_pattern    = "*" + file_id
        file_           = bunchify(Dbb.collection_for_Pattern(file_pattern))

        parent_pattern   = "*" + file_.parentId
        parent           = bunchify(Dbb.collection_for_Pattern(parent_pattern))
        parent           = FileHeader.dictionnary_to_fileHeader(parent)

        #remove childs from parent
        parent.childsId.remove(file_id)

        # remove
        type_file = FileType.GROUP.name if int(parent.type) == int(FileType.GROUP.value) else FileType.FOLDER.name
        #update
        Dbb.remove_with_key_pattern(file_pattern)
        parent = FileHeader.fileHeader_to_dictionnary(parent)
        Dbb.store_collection(type_file, parent["uid"], parent)
