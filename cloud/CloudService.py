# coding: utf8

import base64
import json
import requests
import hashlib
from bunch import bunchify

from CloudType import Group
from services import Dbb
from services.TypeRedis import Type
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

        print data
        #self.create_new_bucket("jojoAdventure")
        self.delete_bucket("jojoAdventure")
        #self.retrieve_bucket_from_id()

    def retrieve_bucket_from_id(self):
        if self.main_bucket_id == "":
            ##TODO check fail
            header = { 'Authorization': self.auth_token }

            r = requests.post(  '%s/b2api/v1/b2_list_buckets' % self.api_url,
                                data    = json.dumps({ 'accountId' : CloudService.account_id }),
                                headers = header)
            response             = json.loads(r.content)
            self.main_bucket_id  = response["buckets"][0]["bucketId"]

        ### TEST
        #self.getFilesFromBucketName(self.main_bucket_id)
        #self.create_file_in_bucket(self.main_bucket_id, "folder/jojo.txt")

    # limité à 10
    def create_new_bucket(self, bucket_name):
        print "Try to create a new bucket..."
        params = {
            'accountId': CloudService.account_id,
            'bucketName': bucket_name,
            'bucketType': "allPrivate"
            }

        header = { 'Authorization': self.auth_token }
        r = requests.post(  '%s/b2api/v1/b2_create_bucket' % self.api_url,
                            data    = json.dumps(params),
                            headers = header)
        response = json.loads(r.content)
        print "done", response

        try:
            bucket = Group(id=response["bucketId"], name=response["bucketName"])
            # store
            Dbb.store_collection(Type.GROUP.name, bucket.name, bucket.__dict__)

            return Error.SUCCESS

        except Exception as e:
            print "ERROR", e
            return Error.FAILED_CREATE_GROUP


    def delete_bucket(self, bucket_name):
        try:
            print "try to delete bucket"
            bucket = bunchify(Dbb.collection_for_Key(Type.GROUP.name, bucket_name))

            # store
            params = {
                'accountId': CloudService.account_id,
                'bucketId': bucket.id,
                }

            header = { 'Authorization': self.auth_token }
            r = requests.post(  '%s/b2api/v1/b2_delete_bucket' % self.api_url,
                                data    = json.dumps(params),
                                headers = header)
            response = json.loads(r.content)
            print response
            # fichier supprimer, clean de la bdd
            if r.status_code == 200:
                print "succeed"
                Dbb.remove_value_for_key(Type.GROUP.name, bucket.name)
                return Error.SUCCESS
            else:
                print "failed"
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
