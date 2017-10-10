# coding: utf8

import base64
import json
import requests
import hashlib
from bunch import bunchify
from services.JSONValidator import validate_json

from CloudType import Group
from services import Dbb
from services.TypeRedis import FileType
from services.Error import Error

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

        #self.create_new_bucket("jojoAdventure")
        #self.delete_bucket("jojoAdventure")
        #self.retrieve_bucket_from_id()

    def validate_create_file_json_request(self, create_request):
        try:
            error, create_request   = validate_json(create_request)
            create_info             = create_request["filetype"]

            if set(("name", "type")) <= set(create_info):
                return error, create_info
            else:
                return Error.INVALID_JSON_TYPE, None

        except Exception as e:
            return Error.INVALID_JSON_TYPE, None

    def validate_delete_file_json_request(self, create_request):
        try:
            error, create_request   = validate_json(create_request)
            create_info             = create_request["fileid"]

            if set(("id")) <= set(create_info):
                return error, create_info
            else:
                return Error.INVALID_JSON_TYPE, None

        except Exception as e:
            return Error.INVALID_JSON_TYPE, None

    def create_file(self, from_error, data, owner_id):
        return  self.c_or_d_file(from_error, data, owner_id,
                self.create_new_bucket, data["name"])

    def delete_file(self, from_error, data, owner_id):
        return  self.c_or_d_file(from_error, data, owner_id,
                self.delete_bucket, data["id"])

    ##### private
    def retrieve_bucket_from_id(self):
        if self.main_bucket_id == "":
            ##TODO check fail
            r = requests.post(  '%s/b2api/v1/b2_list_buckets' % self.api_url,
                                data    = json.dumps({ 'accountId' : CloudService.account_id }),
                                headers = self.header_request())
            response             = json.loads(r.content)
            self.main_bucket_id  = response["buckets"][0]["bucketId"]

        ### TEST
        #self.getFilesFromBucketName(self.main_bucket_id)
        #self.create_file_in_bucket(self.main_bucket_id, "folder/jojo.txt")

    # limité à 10
    def create_new_bucket(self, bucket_name, owner_id):
        print "Try to create a new bucket..."
        params = {  'accountId': CloudService.account_id,
                    'bucketName': bucket_name,
                    'bucketType': "allPrivate" }

        e, r, response = self.simplified_post_request(uri_name="b2_create_bucket", post_data=params)

        if e == Error.SUCCESS and r.status_code == 200:
            print "****** "
            try:
                bucket = Group(id=response["bucketId"], name=response["bucketName"])
                bucket.users_id.append(owner_id)
                # store
                Dbb.store_collection(FileType.GROUP.name, bucket.name, bucket.__dict__)

                return Error.SUCCESS

            except Exception as e:
                print "ERROR", e
                return Error.FAILED_CREATE_GROUP

            return Error.SUCCESS
        else:
            return Error.FAILED_CREATE_GROUP

    #supprime le bucket
    def delete_bucket(self, bucket_name):
        try:
            print "try to delete bucket"
            bucket = bunchify(Dbb.collection_for_Key(FileType.GROUP.name, bucket_name))

            # store
            params = {  'accountId': CloudService.account_id,
                        'bucketId': bucket.id}

            e, r, response = self.simplified_post_request(uri_name="b2_delete_bucket", post_data=params)
            print response

            # fichier supprimée, clean de la bdd
            if e == Error.SUCCESS and r.status_code == 200:
                Dbb.remove_value_for_key(FileType.GROUP.name, bucket.name)
                return Error.SUCCESS
            else:
                return Error.FAILED_DELETE_GROUP

        except Exception as e:
            print "ERROR", e
            return Error.FAILED_DELETE_GROUP


    def get_files_from_bucket_id(self, bucket_id):
        print "try to get files from bucket_id"
        header = { 'Authorization': self.auth_token }

        r = requests.post(  '%s/b2api/v1/b2_list_file_names' % self.api_url,
                            data    = json.dumps({ 'bucketId' : bucket_id}),
                            headers = header)

        response = json.loads(r.content)
        print "found: ", response
        return response

    def create_file_in_bucket(self, bucket_id, uri_path):
        # get bucket upload url and auth
        header = { 'Authorization': self.auth_token }
        print "try to create file into bucket: ", uri_path

        r = requests.post(  '%s/b2api/v1/b2_get_upload_url' % self.api_url,
                            data    = json.dumps({ 'bucketId' : bucket_id}),
                            headers = header)

        response    = json.loads(r.content)
        auth_token  = response["authorizationToken"]
        uploadUrl   = response["uploadUrl"]
        #TODO check error

        # now send data
        print "url found ====== now uploading content"
        file_data           = ""
        file_name           = uri_path
        content_type        = "text/plain"
        sha1_of_file_data   = hashlib.sha1(file_data).hexdigest()

        headers = {
            'Authorization'     : auth_token,
            'X-Bz-File-Name'    : file_name,
            'Content-Type'      : content_type,
            'X-Bz-Content-Sha1' : sha1_of_file_data
        }

        r = requests.post(  uploadUrl,
                            data    = file_data,
                            headers = headers)

        response = json.loads(r.content)
        print response

    def delete_file(self, file_id, owner_id):
        header      = { 'Authorization': self.auth_token }
        print "try to create file into bucket: ", uri_path
        file_data   = bunchify(Dbb.collection_for_Key(FileType.GROUP.name, bucket_name))
        pass

    def simplified_post_request(self, uri_name, post_data):
        try:
            print "simplified request***", json.dumps(post_data)
            r = requests.post(  '%s/b2api/v1/%s' % (self.api_url, uri_name),
                                data    = json.dumps(post_data),
                                headers = { 'Authorization': self.auth_token })
            print "DONE ?"
            return Error.SUCCESS, r, json.loads(r.content)

        except Exception as e:
            print "__ERROR", e
            return Error.EXCEPTION, None, None


    def c_or_d_file(self, from_error, data, owner_id, callback, params):
        print callback
        if from_error.value == Error.SUCCESS.value:
            if data["type"] == int(FileType.GROUP):
                return callback(params, owner_id)
            else: # file or folder
                return Error.NONE
        else:
            return from_error
