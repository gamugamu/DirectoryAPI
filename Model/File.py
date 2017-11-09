# coding: utf8
from bunch import bunchify, unbunchify

class FileType(object):
    def __init__(self, type=0, name=""):
        self.type  = type
        self.name  = name

class FileID(FileType):
    def __init__(self, uid="", *args, **kwargs):
        super(FileID, self).__init__(*args, **kwargs)
        self.uid = uid

class FileHeader(FileID):
    def __init__(self, owner="", title="", date="", parentId="", rules="", childsId="", *args, **kwargs):
        super(FileHeader, self).__init__(*args, **kwargs)
        self.owner      = owner
        self.title      = title
        self.date       = date
        self.parentId   = parentId
        self.rules      = rules
        self.childsId   = childsId

    @staticmethod
    def dictionnary_to_fileHeader(dict):
        try:
            print "DICT***", dict
            file            = bunchify(dict)
            print "FILE***", file
            file.childsId   = file.childsId.split("|")
            return file
        except Exception as e:
            print "exception", e
            return None

    @staticmethod
    def fileHeader_to_dictionnary(file_header):
        file_header.childsId   = '|'.join(file_header.childsId)
        #file_header.parentId   = '|'.join(file_header.parentId)
        return unbunchify(file_header)

class FilePayload(FileHeader):
    def __init__(self, payload="", *args, **kwargs):
        super(FilePayload, self).__init__(*args, **kwargs)
        self.payload  = payload
