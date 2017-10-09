# coding: utf8

import base64
import json
import requests
import hashlib

class CloudService:
    id_and_key          = '191c9cd81236:00126b7b79d0d100c93ddc6b6e42f113090d8c8723'
    account_id          = "191c9cd81236" # Obtained from your B2 account page
    basic_auth_string   = 'Basic ' + base64.b64encode(id_and_key)

    def __init__(self):
        # renseigné via le cloud
        self.auth_token     = ""
        self.api_url        = ""
        self.download_url   = ""

    def connect_to_cloud(self):
        header = { 'Authorization': CloudService.basic_auth_string }
        r = requests.get(   'https://api.backblazeb2.com/b2api/v1/b2_authorize_account',
                            headers = header)
        data = json.loads(r.content)

        self.auth_token      = data['authorizationToken']
        self.api_url         = data['apiUrl']
        self.download_url    = data['downloadUrl']

        print data
        print "connected-----", self.api_url

    def getBucketFile(self):
        print "getBucketFile***", self.api_url

        header = { 'Authorization': self.auth_token }

        r = requests.post(  '%s/b2api/v1/b2_list_buckets' % self.api_url,
                        data    = json.dumps({ 'accountId' : CloudService.account_id }),
                        headers = header)
        response        = json.loads(r.content)

        print response
        bucket_test_id = response["buckets"][0]["bucketId"]
        self.getFilesFromBucketName(bucket_test_id)
        self.test_create_file(bucket_test_id)

    def getFilesFromBucketName(self, bucket_id):
        print "****** getFilesFromBucketName"
        header = { 'Authorization': self.auth_token }

        r = requests.post(  '%s/b2api/v1/b2_list_file_names' % self.api_url,
                            data    = json.dumps({ 'bucketId' : bucket_id}),
                            headers = header)

        response = json.loads(r.content)
        print response
        print "\n\n"

    def test_create_file(self, bucket_id):
        print "find Bucket url and auth"
        # get bucket upload url and auth
        header = { 'Authorization': self.auth_token }

        r = requests.post(  '%s/b2api/v1/b2_get_upload_url' % self.api_url,
                            data    = json.dumps({ 'bucketId' : bucket_id}),
                            headers = header)

        response = json.loads(r.content)
        print response
        # check error
        auth_token  = response["authorizationToken"]
        uploadUrl   = response["uploadUrl"]

        # now send data
        print "url found ====== now uploading content"
        file_data           = ""
        file_name           = "anotherFolder/.bzEmpty"
        content_type        = "text/plain"
        sha1_of_file_data   = hashlib.sha1(file_data).hexdigest()

        headers = {
            'Authorization'     : auth_token,
            'X-Bz-File-Name'    :  file_name,
            'Content-Type'      : content_type,
            'X-Bz-Content-Sha1' : sha1_of_file_data
        }

        r = requests.post(  uploadUrl,
                            data    = file_data,
                            headers = headers)

        response = json.loads(r.content)
        print response

    def create_file(type):
        print "create: ", type
        if type == 1: # bucket / group
            pass
        else:
            pass
