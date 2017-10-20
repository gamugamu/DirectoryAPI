# -*- coding: utf-8 -*-
# coding: utf8

from CloudService import *

def graph(from_error, request, owner_id):
    if from_error == Error.SUCCESS:
        error, data = validate_json(request, {"fileid": ""});

        if from_error == Error.SUCCESS:
            print "data ", data
            file_id = data["fileid"]
            #file    = CloudService.get_raw_files_header(file_id)
            #print "file ", file
            #error, bucket, uri_path = CloudService.retrieve_bucket_data_from_graph(file_id)

    return from_error, "result"
