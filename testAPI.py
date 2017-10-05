# -*- coding: utf-8 -*-

import requests
import json

urlRoot = "https://directory-api.herokuapp.com/"
version = "0.0.1"

print "========== launching test on " + urlRoot + " API. ==========="
r = requests.get(urlRoot)

# #Ia01, #Ia02
print "[#Ia01, #Ia02] status code == 200", r.status_code, r.status_code == 200

# #Ia03
print "[#Ia03] version == ", r.headers["version"], version == r.headers["version"]
