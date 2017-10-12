# coding: utf8

import base64
import json
import requests
import hashlib
from bunch import bunchify, unbunchify
from services.JSONValidator import validate_json

from CloudType import Group
from services import Dbb
from services.Security import generate_date_now
from services.TypeRedis import FileType
from services.Error import Error
from Model.File import FilePayload, FileHeader

class CloudService:
    id_and_key          = '191c9cd81236:00126b7b79d0d100c93ddc6b6e42f113090d8c8723'
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

                    if error == Error.SUCCESS:
                        return self.create_file_in_bucket(bunchify(bucket), owner_id, file_name, uri_path)
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
                    return self.delete_bucket(file_id, owner_id)
                else: # file or folder
                    pass
        else:
            return error

    # limité à 10
    def create_new_bucket(self, bucket_name, owner_id):
        print "Try to create a new bucket...", bucket_name
        params = {  'accountId': CloudService.account_id,
                    'bucketName': bucket_name,
                    'bucketType': "allPrivate" }

        e, r, response = self.simplified_post_request(uri_name="b2_create_bucket", post_data=params)

        if e == Error.SUCCESS and r.status_code == 200:
            print "let's do it"
            try:
                bucket_id           = response["bucketId"]
                bucket_name         = response["bucketName"]

                group = FilePayload(uid       = bucket_id,
                                    name      = bucket_name,
                                    type      = FileType.GROUP.value,
                                    date      = generate_date_now(),
                                    owner     = [owner_id])
                # store
                Dbb.store_collection(FileType.GROUP.name, bucket_id, group.__dict__)
                print "bucket created"
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
            print "try to delete bucket :", bucket_id
            bucket_redis_name   = bucket_id

            # store
            params = {  'accountId': CloudService.account_id,
                        'bucketId': bucket_id}

            e, r, response = self.simplified_post_request(uri_name="b2_delete_bucket", post_data=params)

            # fichier supprimée, clean de la bdd
            if e == Error.SUCCESS and r.status_code == 200:
                print "deleted bucket succeed", bucket_id
                Dbb.remove_value_for_key(FileType.GROUP.name, bucket.name)
                return Error.SUCCESS
            else:
                print "can't delete bucket"
                return Error.FAILED_DELETE_GROUP

        except Exception as e:
            print "ERROR_DELETE_BUCKET", e
            return Error.FAILED_DELETE_GROUP

    ##### private
    def retrieve_bucket_from_id(self):
        if self.main_bucket_id == "":
            ##TODO PAS encore fait
            r = requests.post(  '%s/b2api/v1/b2_list_buckets' % self.api_url,
                                data    = json.dumps({ 'accountId' : CloudService.account_id }),
                                headers = self.header_request())
            response             = json.loads(r.content)
            self.main_bucket_id  = response["buckets"][0]["bucketId"]

        ### TEST
        #self.getFilesFromBucketName(self.main_bucket_id)
        #self.create_file_in_bucket(self.main_bucket_id, "folder/jojo.txt")

    def retrieve_bucket_data_from_graph(self, parent_id, uri_path=""):
        key     = "*_" + parent_id
        value   = Dbb.value_for_key(key=key)

        try:
            parent_key = value.next()

            if FileType.GROUP.name in parent_key:
                # bucket trouvé. N'as pas de parent.
                bucket      = Dbb.collection_for_Key(key=parent_key)

                return Error.SUCCESS, Dbb.collection_for_Key(key=parent_key), uri_path
            else:
                print "*******found folder, reiterate"
                return Error.None, Dbb.collection_for_Key(key=parent_key), uri_path

        except Exception as e:
            print "EXCEPTION: ", e, "is not from graph"
            return Error.REDIS_KEY_UNKNOWN, None

    def create_file_in_bucket(self, bucket, owner_id, file_name, uri_path):
        # Vérifie qu'il a bien un parent (devrait toujours être a true)
        if bucket is not None:
            # Et vérifie qu'il n'y a pas de doublon
            #TODO faire le check
            print "create_file_in_bucket: ", uri_path
            uri_path      = self.append_path(uri_path, file_name)
            full_uri_path = self.append_path(bucket.name, uri_path)

            print "full_uri_path=== ", full_uri_path

            is_entry_already_exist = Dbb.is_key_exist_forPattern("*|" + full_uri_path + "|*")

            # Si il n'existe pas d'entrée, alors on peux créer le fichier
            if is_entry_already_exist == False:

                params = { 'bucketId' : bucket.uid}
                e, r, response = self.simplified_post_request(uri_name="b2_get_upload_url", post_data=params)

                if e == Error.SUCCESS and r.status_code == 200:
                    auth_token  = response["authorizationToken"]
                    uploadUrl   = response["uploadUrl"]

                    # now send data
                    print "url found ====== now uploading content"

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
                        print "response***** ", response
                        file_id = response["fileId"]
                        file_   = FilePayload(  uid       = file_id,
                                                name      = file_name,
                                                type      = FileType.FILE.value,
                                                date      = generate_date_now(),
                                                owner     = [owner_id],
                                                parentId  = bucket.uid)

                        redis_id            = "|" + full_uri_path + "|" + file_id
                        bucket.childsId     = Dbb.appendedValue(bucket.childsId, file_id)

                        #update data
                        Dbb.store_collection(FileType.FILE.name, redis_id, file_.__dict__)
                        Dbb.store_collection(FileType.GROUP.name, bucket.uid, unbunchify(bucket))
                        print "ADDED TO DB and backBlaze"

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
                print "key already exist***"
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
            else:
                print "HEADER FOUND ", header

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
            return path + "/" + new_value
