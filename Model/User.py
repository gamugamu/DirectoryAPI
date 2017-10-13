# coding: utf8
class User:
    def __init__(self, uid="", email="", name="", group=""):
        self.uid                = uid
        self.email              = email
        self.name               = name
        self.group              = group
        self._secret_password   = ""
