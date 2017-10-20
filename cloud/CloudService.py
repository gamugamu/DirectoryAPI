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

class CloudService:

    def __init__(self):
        pass

    def connect_to_cloud(self):
        pass

################# SERVICE ######################

    def create_file(self, from_error, request, owner_id):
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"filetype": {"name" : "", "type" : "", "parentId" : ""}})

            if error == Error.SUCCESS:
                file_name = data["filetype"]["name"]
                file_type = data["filetype"]["type"]
                parent_id = data["filetype"]["parentId"]

                if file_type == int(FileType.GROUP):
                    return self.create_new_bucket(file_name, owner_id)

                elif file_type in (FileType.FILE, FileType.FOLDER): # file or folder
                    error, bucket, uri_path = self.retrieve_bucket_data_from_graph(parent_id)

                    if error == Error.SUCCESS:
                        # Si c'est un dossier, le nom doit être formaté avec un .bzEmpty
                        if file_type == int(FileType.FOLDER):
                            file_name = self.append_as_folder(file_name)
                        return self.create_file_in_bucket(bunchify(bucket), owner_id, file_name, uri_path, parent_id)
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
            return from_error

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
            error, data = validate_json(request, {"fileids": []});
            list_uid = [];

            if error == Error.SUCCESS:
                for uid in data["fileids"]:
                    value = Dbb.collection_for_Pattern("*" + uid)

                    if value is not None:
                        value = unbunchify(FileHeader.dictionnary_to_fileHeader(value))
                        list_uid.append(value)

                if len(list_uid) == 0:
                    return Error.REDIS_KEY_UNKNOWN, FilePayload().__dict__
                else:
                    return Error.SUCCESS, list_uid
            else:
                return error, FilePayload().__dict__
        else:
            return error, FilePayload().__dict__

################# LOGIC ######################

    def create_new_bucket(self, bucket_name, owner_id):
        bucket_id   = uuid.uuid4().hex
        group       = FilePayload(  uid    = bucket_id,
                                    name   = bucket_name,
                                    type   = FileType.GROUP.value,
                                    date   = generate_date_now(),
                                    owner  = [owner_id])
        # store
        Dbb.store_collection(FileType.GROUP.name, bucket_id, group.__dict__)
        self.add_user_ownership(owner_id, bucket_id)

        return Error.SUCCESS, group

    #supprime le bucket
    def delete_bucket(self, bucket_id, owner_id):
        bucket_redis_name = bucket_id
        e = self.recursively_delete_all_files_in_bucket(bucket_id)

        if e == Error.SUCCESS:
            Dbb.remove_value_for_key(FileType.GROUP.name, bucket_id)
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
        Dbb.store_collection(FileType.GROUP.name, bucket["uid"], bucket)

        #les suppressions ont réussies
        return Error.SUCCESS

    def create_file_in_bucket(self, bucket, owner_id, file_name, uri_path, parentId):
        if bucket is not None:
            uri_path      = self.append_path(uri_path, file_name)
            full_uri_path = self.append_path(bucket.name, uri_path)

            is_entry_already_exist = Dbb.is_key_exist_forPattern("*|" + full_uri_path + "|*")

            # Si il n'existe pas d'entrée, alors on peux créer le fichier
            if is_entry_already_exist == False:
                # creation du fichier redis
                if parentId == "":
                    parentId = bucket.uid

                file_id = uuid.uuid4().hex
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
                # l'entrée existe déjà pour ce fichier
                return Error.REDIS_KEY_ALREADY_EXIST, FilePayload()

    def remove_file_from_parent(self, file_id):
        file_pattern    = "*" + file_id
        file_           = bunchify(Dbb.collection_for_Pattern(file_pattern))

        parent_pattern   = "*" + file_.parentId
        parent           = Dbb.collection_for_Pattern(parent_pattern)
        parent           = FileHeader.dictionnary_to_fileHeader(parent)

        #remove childs from parent
        parent.childsId.remove(file_id)

        # remove
        type_file = FileType.GROUP.name if int(parent.type) == int(FileType.GROUP.value) else FileType.FOLDER.name

        #update
        Dbb.remove_with_key_pattern(file_pattern)
        parent = FileHeader.fileHeader_to_dictionnary(parent)
        Dbb.store_collection(type_file, parent["uid"], parent)

################# GRAPH ######################

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

################# USER OWNERSHIP ######################

    def add_user_ownership(self, user_id, group_id):
        user            = Dbb.collection_for_Key(typeKey=Type.USER.name, key=user_id)
        print "user++ ", user, user_id
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
        return path.replace("/.bzEmpty", "")

    def append_as_folder(self, path):
        return path + "/.bzEmpty"

################# GRAPH ######################
    def graph(self, from_error, request, owner_id):
        print "graph GRAPH"
        if from_error == Error.SUCCESS:
            error, data = validate_json(request, {"file_id": ""})
            print "++++++++++++"
            if error == Error.SUCCESS:
                print "xxxxxxxxxxxxx"

                print self.retrieve_bucket_data_from_graph(data["file_id"])

            else:
                return error
        else:
            return from_error

        return from_error, "graph"
