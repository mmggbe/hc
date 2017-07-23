#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from HCsettings import Notifier


payload = {'grant_type': 'client_credentials', 'scope': 'openid'}

print( "Acquiring token" )
print()

r = requests.post("https://api.enco.io/token", data=payload, auth=( Notifier.config("CLIENT_ID"), Notifier.config("CLIENT_SECRET")))
print(r.text)
authInfo = r.json()
tokenBearer = authInfo['access_token']

print()
print( "Using token to retrieve user information")
print
auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Accept':'application/json'}
r = requests.get("https://api.enco.io/userinfo?schema=openid", headers=auth_header)
print(r.text)
userInfo = r.json()

print()
print( "Hello %s" % userInfo['name'])
print( "\t%s, %s" % (userInfo['given_name'], userInfo['family_name']) )
print( "\teMail: %s" % userInfo['email'] )


"""
curl -i -X POST 'https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false' 
-H 'Authorization: Bearer 674f4fc8db0000000083e887306cd8' 
-H 'Content-Type: application/json' 
-H 'Accept: application/json'  
-d '{"message":"Hello World Test Message","destinations":["+32000000000"]}'
"""

payload = {'message':'Hello Marc','destinations':['+32475618115',]}
auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Content-Type':'application/json', 'Accept':'application/json'}
r = requests.post("https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false", data=payload, headers=auth_header)
print(r.text)

