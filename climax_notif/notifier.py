#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json 
import logging

import smtplib
from email.mime.text import MIMEText

from HCsettings import Notifier, HcDB, Email_svr





def send_notification(usr, event):


    logging.info("Acquiring token\n")

    
    payload = {'grant_type': 'client_credentials', 'scope': 'openid'} 
    
    r = requests.post("https://api.enco.io/token", data=payload, auth=( Notifier.config("client_id"), Notifier.config("client_secret")))
    print(r.text)
    authInfo = r.json()
    tokenBearer = authInfo['access_token']
    
    print()
    print( "Using token to retrieve user information\n")
    
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
    
    if 1==0:
        payload = json.dumps( {'message':'Hello Marc 2','destinations':['+32475618115']} )
        
        auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Content-Type':'application/json', 'Accept':'application/json'}
        r = requests.post("https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false", data=payload, headers=auth_header)
        print(r.text)
    
    #https://stackoverflow.com/questions/24077314/how-to-send-an-email-with-style-in-python3
    logging.info(" Sending email to user ID {}".format(usr) )
    
    
    title = 'Horus monitoring service notification'
    msg_content = '<h2>{title} > <font color="green">OK</font></h2>\n'.format(title=title)
    message = MIMEText(msg_content, 'html')
    
    message['From'] = Email_svr.config("from")
    message['To'] = '<mage.gerin@gmail.com>'
    #message['To'] = 'Receiver Name <receiver@server>'
    #message['Cc'] = 'Receiver2 Name <receiver2@server>'
    message['Subject'] = 'Any subject2'
    
    msg_full = message.as_string()
    
    server = smtplib.SMTP(Email_svr.config("server"),587)
    server.starttls()
    server.ehlo()
    server.login(Email_svr.config("login"), Email_svr.config("password"))
    server.sendmail(Email_svr.config("from"),'mage.gerin@gmail.com', msg_full)
    
    server.quit()
