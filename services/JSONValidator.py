# coding: utf8
from flask import request
from Error import Error

import json

def validate_json(request, graph):
    try:
        data  = request.get_json()
        error = iterate_through_graph(data, graph)

        return error, data

    except Exception as e:
        print(e)
        return Error.INVALID_JSON, None

def iterate_through_graph(data, graph):
    for key, value in graph.items():
        if (key in data) == False:
            print "KEY NOT FOUND ", key
            return Error.INVALID_JSON_TYPE
        else:
            if type(value) == dict:
                return iterate_through_graph(data[key], graph[key])

    return Error.SUCCESS
