# coding: utf8
from bunch import unbunchify

def sanityse(type):
    dict = unbunchify(type)
    for key in dict.keys():
        if key[0] == "_":
            del dict[key]

    return dict
