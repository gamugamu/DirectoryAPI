# coding: utf8
from bunch import unbunchify
from bunch import Bunch

def sanityse(type_data):
    if type(type_data) is Bunch:
        _dict = unbunchify(type_data)
    elif type(type_data) is dict:
        _dict = type_data
    else:
        _dict = type_data.__dict__

    for key in _dict.keys():
        if key[0] == "_":
            del _dict[key]

    return _dict
