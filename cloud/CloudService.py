# coding: utf8

import base64
import json
import requests
import hashlib
from bunch import bunchify, unbunchify
from services.JSONValidator import validate_json
import uuid
import pdb

from services.TypeRedis import Type
from CloudType import Group
from services import Dbb
from services.Security import generate_date_now
from services.TypeRedis import FileType
from services.Error import Error
from Model.File import FilePayload, FileHeader

#graph
import operator
import dpath.util

HISTORY_TAG     = "H_"
GROUP_PATTERN   = "*_|*"

class CloudService:

    def __init__(self):
        pass

    def connect_to_cloud(self):
        pass

################# SERVICE ######################

    def create_file(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"payload": {
                "name" : "",
                "type" : "",
                "parentId" : "",
                "title" : "",
                "payload" : ""}})

            if error == Error.SUCCESS:
                data        = data["payload"]
                file_name   = data["name"]
                file_type   = data["type"]
                parent_id   = data["parentId"]
                payload     = data["payload"]

                if file_type == int(FileType.GROUP):
                    return self.create_new_bucket(file_name, owner_id)

                elif file_type in (FileType.FILE, FileType.FOLDER): # file or folder

                    error, bucket, uri_path = self.retrieve_bucket_data_from_graph(parent_id)

                    if error == Error.SUCCESS:
                        if file_type == int(FileType.FOLDER):
                            file_name = self.append_as_folder(file_name)

                        return self.create_file_in_folder(bunchify(bucket), owner_id, file_name, uri_path, parent_id, file_type, payload)
                    else:
                        # graph error
                        return error, FilePayload()
                else:
                    # type error
                    return Error.FILE_UNKNOW_TYPE, FilePayload()
            else:
                # json validation error
                return error, FilePayload()
        else:
            # external error
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
                    self.remove_file_from_parent(file_id)
                    return Error.SUCCESS
            else:
                return error
        else:
            return from_error

    def modify_file(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:

            error, data = validate_json(request, {"filepayload": {
            "type" : "", "name" : "", "uid" : "", "parentId" : "", "owner" : "",
            "title" : "", "date" : "", "rules" : "", "payload" : ""}})

            if error == Error.SUCCESS:
                data        = data["filepayload"]
                if len(data["uid"]) != 32: #uuid lenght
                    return Error.REDIS_KEY_UNKNOWN
                else:
                    pattern_key = GROUP_PATTERN + data["uid"]
                    key         = Dbb.value_for_key(key=pattern_key)

                    if key is not None:
                        key = key.next()

                        #update content in redis
                        Dbb.store_collection(key=key, storeDict=data)
                        return Error.SUCCESS

            else:
                #graph error
                return error
        else:
            # exrternal error
            return from_error

    def get_files_header(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"fileids": []});
            list_uid = [];

            for uid in data["fileids"]:
                value = Dbb.collection_for_Pattern("*" + uid)

                if value is not None:
                    value = unbunchify(FileHeader.dictionnary_to_fileHeader(value))
                    value.pop('payload', None) # seul les headers nous interressent
                    list_uid.append(value)

            if len(list_uid) == 0:
                return Error.REDIS_KEY_UNKNOWN, FileHeader().__dict__
            else:
                return Error.SUCCESS, list_uid
        else:
            return from_error, FileHeader().__dict__

    def get_files_payload(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:

            error, data = validate_json(request, {"filesid": []});
            list_uid = [];

            if error == Error.SUCCESS:
                for uid in data["filesid"]:
                    value = Dbb.collection_for_Pattern("*" + uid)

                    if value is not None:
                        value = unbunchify(FileHeader.dictionnary_to_fileHeader(value))
                        list_uid.append(value)

                if len(list_uid) == 0:
                    return Error.REDIS_KEY_UNKNOWN, FilePayload().__dict__
                else:
                    return Error.SUCCESS, list_uid
            else:
                print "bad json", error
                return error, FilePayload().__dict__
        else:
            return error, FilePayload().__dict__

################# LOGIC ######################

    def create_new_bucket(self, bucket_name, owner_id):
        is_entry_already_exist = Dbb.is_key_exist_forPattern("*|" + bucket_name + "|*")

        if is_entry_already_exist is False:
            bucket_id               = uuid.uuid4().hex
            creation_date, tstamp   = generate_date_now()
            group       = FilePayload(  uid    = bucket_id,
                                        name   = bucket_name,
                                        type   = FileType.GROUP.value,
                                        date   = creation_date,
                                        owner  = [owner_id])
            bucket_id_key = bucket_name + "|" + bucket_id

            # store
            Dbb.store_collection(FileType.GROUP.name, "|" + bucket_id_key, group.__dict__)
            self.sort_for_history(bucket_id_key, tstamp)
            self.add_user_ownership(owner_id, bucket_id)

            return Error.SUCCESS, group
        else:
            print "Error.REDIS_KEY_ALREADY_EXIST"
            return Error.REDIS_KEY_ALREADY_EXIST, FilePayload()

    #supprime le bucket
    def delete_bucket(self, bucket_id, owner_id):
        bucket_redis_name = bucket_id
        e = self.recursively_delete_all_files_in_bucket(bucket_id)

        if e == Error.SUCCESS:
            key = Dbb.remove_value_for_key(FileType.GROUP.name, bucket_id)
            self.remove_from_history(key)
            self.remove_user_ownership(owner_id, bucket_id)
            return Error.SUCCESS
        else:
            print "can't delete bucket ", response
            return Error.FAILED_DELETE_GROUP

    def recursively_delete_all_files_in_bucket(self, bucket_id):
        # store
        bucket      = Dbb.collection_for_Key(typeKey=FileType.GROUP.name, key=bucket_id)
        bucket      = FileHeader.dictionnary_to_fileHeader(bucket)

        #R2cupérations de la listes des fichiers + suppresion
        for child_id in bucket.childsId:
            Dbb.remove_with_key_pattern(p_key= "*|" + child_id)

        bucket = FileHeader.fileHeader_to_dictionnary(bucket)
        # TODO, uid path à refaire
        Dbb.store_collection(FileType.GROUP.name, "****" + bucket["uid"], bucket)

        #les suppressions ont réussies
        return Error.SUCCESS

    def create_file_in_folder(self, bucket, owner_id, file_name, uri_path, parentId, file_type, payload):
        if bucket is not None:
            uri_path      = self.append_path(uri_path, file_name)
            is_entry_already_exist = Dbb.is_key_exist_forPattern("*|" + uri_path + "|*")

            # Si il n'existe pas d'entrée, alors on peux créer le fichier
            if is_entry_already_exist == False:
                # creation du fichier redis

                if parentId == "":
                    parentId = bucket.uid

                creation_date, tstamp = generate_date_now()
                file_id = uuid.uuid4().hex
                file_   = FilePayload(  uid       = file_id,
                                        name      = self.sanityse_path(file_name),
                                        type      = file_type,
                                        date      = creation_date,
                                        owner     = [owner_id],
                                        parentId  = parentId,
                                        payload   = payload)

                redis_id            = uri_path + "|" + file_id
                parent_path_key     = Dbb.keys(pattern = GROUP_PATTERN + parentId + "*")
                parent              = bunchify(Dbb.collection_for_Key(key=parent_path_key[0]))

                # store_file
                Dbb.store_collection(FileType(int(file_type)).name, "|" + redis_id, file_.__dict__)
                self.sort_for_history(redis_id, tstamp)

                #update data
                bucket.childsId = Dbb.appendedValue(bucket.childsId, file_id)
                Dbb.store_collection(key=parent_path_key[0], storeDict=unbunchify(bucket))

                return Error.SUCCESS, file_
            else:
                # l'entrée existe déjà pour ce fichier
                print "BUCKET NOT FOUND"
                return Error.REDIS_KEY_ALREADY_EXIST, FilePayload()


    def remove_file_from_parent(self, file_id):
        file_pattern    = "*" + file_id
        file_           = bunchify(Dbb.collection_for_Pattern(file_pattern))

        if file_ is not None:
            try:
                parent_pattern   = "*" + file_.parentId
                parent           = Dbb.collection_for_Pattern(parent_pattern)
                parent           = FileHeader.dictionnary_to_fileHeader(parent)

                #remove childs from parent
                parent.childsId.remove(file_id)

                # remove
                type_file               = FileType.GROUP.name if int(parent.type) == int(FileType.GROUP.value) else FileType.FOLDER.name
                e, data, file_graph     = self.retrieve_bucket_data_from_graph(parent.uid)

                if file_graph == "":
                    file_graph = parent['name']

                #update
                key = Dbb.keys(file_pattern)

                Dbb.remove_with_key_pattern(file_pattern)
                self.remove_from_history(key[0])

                parent = FileHeader.fileHeader_to_dictionnary(parent)

                Dbb.store_collection(type_file, "|" + file_graph + "|" + parent["uid"], parent)

            except Exception as e:
                #TODO gérer erreur si delete file inexistante
                print "EXCEPTION: ", e, "didn't removed"

    def get_file_by_name(self, file_name):
        file_       = {}
        group_key   = Dbb.keys(pattern="*|" + file_name + "|*")

        if len(group_key) > 0:
            file_ = Dbb.collection_for_Key(key=group_key[0])
            return Error.SUCCESS, file_
        else:
            return Error.FILE_NOT_FOUND, file_

################# USER OWNERSHIP ######################

    def add_user_ownership(self, user_id, group_id):
        user            = Dbb.collection_for_Key(typeKey=Type.USER.name, key=user_id)
        user["group"]   = Dbb.appendedValue(user["group"], group_id)

        Dbb.store_collection(Type.USER.name, user_id, user)

    def remove_user_ownership(self, user_id, group_id):
        user            = Dbb.collection_for_Key(typeKey=Type.USER.name, key=user_id)
        user["group"]   = Dbb.removedValue(user["group"], group_id)

        Dbb.store_collection(Type.USER.name, user_id, user)

################# PATH ######################

    def append_path(self, path, new_value):
        if path == "":
            return new_value
        else:
            new_path = path + "/" + new_value
            return new_path.replace("//", "/")

    def sanityse_path(self, path):
        return path

    def append_as_folder(self, path):
        return path

################# GRAPH ######################
    def retrieve_bucket_data_from_graph(self, parent_id, uri_path=""):
        if parent_id == "":
            return Error.FILE_NO_PARENT_ID, None, "";
        else:
            #
            try:
                # retrouve le bon bucket et renvoie l'uri.
                # Note: *_|* permet de séparer les group et folder des clès de
                # SORT par date.
                t_key                = Dbb.keys(pattern= GROUP_PATTERN + parent_id);

                bucket_key_name      = t_key[0].split("|")[1].split("/")[0]
                bucket_full_key_name = Dbb.keys(pattern= "*|" + bucket_key_name + "|*")[0];

                bucket               = Dbb.collection_for_Key(key=bucket_full_key_name)
                uri_path             = t_key[0].split("|")[1]

                return Error.SUCCESS, bucket, uri_path

            except Exception as e:
                print "EXCEPTION: ", e, "buck is not from graph"
                return Error.REDIS_KEY_UNKNOWN, None, ""

    def graph(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"file_id": ""})

            if error == Error.SUCCESS:
                #print data

                file_id = data["file_id"]
                if file_id == "":
                    return  Error.FILE_NO_PARENT_ID, ""
                else:
                    return self.recurse_graph(file_id, 3, 0)

            else:
                return error, ""
        else:
            return from_error, ""

        return from_error, ""

    def recurse_graph(self, file_id, max_depht, incr_deph):
        file_full_key_name = Dbb.keys(pattern=GROUP_PATTERN + file_id)

        try:
            # retrouve le bon bucket et renvoie l'uri.
            file_base_key_name  = file_full_key_name[0].split("|")[1]
            graph_keys          = Dbb.keys(pattern= GROUP_PATTERN + file_base_key_name + "*");

            full_graph  = {}
            for x in graph_keys:
                # rappel 0: type de fichier, 1:path, 2:uid
                splits = x.split("|")
                path   = splits[1]

                dpath.util.new(full_graph , path + "/uid", splits[2])

            return Error.SUCCESS, full_graph

        except Exception as e:
            print "EXCEPTION: ", e, "data is not from graph"
            return Error.REDIS_KEY_UNKNOWN, ""

################# HISTORY ######################
    def sort_for_history(self, key, creation_date):
        Dbb.add_for_sorting(self.generate_history_key(key), HISTORY_TAG + key, "date", creation_date)

    def remove_from_history(self, key):
        Dbb.remove_from_sorting(self.generate_history_key(key), HISTORY_TAG + key)

    def key_without_history_tag(self, key):
        return key.replace(HISTORY_TAG, "")

    def history(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:

            error, data = validate_json(request, {})

            if data is not None:
                option_filter   = data.get("option-filter")
                group_name      = option_filter.get("group_name")
                want_payload    = option_filter.get("file_payload")
                list_by_date    = Dbb.sort(member= self.generate_history_key(group_name), by="*->date", desc=False)

                result = []

                for document in list_by_date:
                    uri_key = self.key_without_history_tag(document)
                    payload = Dbb.collection_for_Pattern(GROUP_PATTERN + uri_key)

                    if not want_payload:
                        payload["payload"] = ""

                    result.append(payload)

                return  Error.FILE_NO_PARENT_ID, result
            else:
                print "NOT IMPLEMENTED"
                # recherche de base, ce que l'utilisateur a créé

                return from_error, ""

        else:
            return from_error, ""

    def generate_history_key(self, key):
        key         = key.split("|")[0]
        root_bucket = key.split("/")[0]

        return "history_" +  root_bucket
