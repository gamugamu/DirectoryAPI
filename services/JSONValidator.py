# coding: utf8
from flask import request
from Error import Error, ErrorDescription
import json

def validate_json(request, graph):
    ErrorDescription.EXTRA_DESCRIPTION_ERROR = ""
    
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
            ErrorDescription.EXTRA_DESCRIPTION_ERROR = " | Key missing: " + key
            return Error.INVALID_JSON_TYPE
        else:
            if type(value) == dict:
                return iterate_through_graph(data[key], graph[key])

    return Error.SUCCESS
