# coding: utf8
class User:
    def __init__(self, id="", email="", name="", group=[]):
        self.id                 = id
        self.email              = email
        self.name               = name
        self.group              = group
        self._secret_password   = ""
