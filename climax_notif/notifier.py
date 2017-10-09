#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json 
import logging

import smtplib
from email.mime.text import MIMEText

from HCsettings import Notifier, HcDB, Email_svr





def send_notification(usr, event):
# list usr [User,Property, email, SN_SMS, SN_Voice]
# list event eg: '100', "Medical", [ "1", "0", "0"] # code : "description, email to be sent, sms to be sent, voice call to be issued


    if event[2][0] :
         
    #https://stackoverflow.com/questions/24077314/how-to-send-an-email-with-style-in-python3
        logging.info(" Sending email to user ID {}".format(usr[0]) )
                
 #       title = 'Horus supervisor:'
 #       msg_content = '<h2>{title} > <font color="green">OK</font></h2>\n'.format(title=event)
 
        EMAIL_CONTENT = """
Hi,

The following event has been detected:\n\n

[property]\n
 <font color="green">
{0}
</font>
\n\n
[event]
 <font color="green">
{1}
</font>
\n\n

Please take the appropriate actions
\n\n

Best regards\n
Your Horus Monitoring System

"""
        
        message = MIMEText(EMAIL_CONTENT.format(usr[1],event[1]), 'html')
        
        message['From'] = Email_svr.config("from")
        message['To'] = usr[4]
        #message['To'] = 'Receiver Name <receiver@server>'
        #message['Cc'] = 'Receiver2 Name <receiver2@server>'
        message['Subject'] = 'Horus supervisor : you property: {}'.format(usr[1])
        
        msg_full = message.as_string()
        
        server = smtplib.SMTP(Email_svr.config("server"),587)
        server.starttls()
        server.ehlo()
        server.login(Email_svr.config("login"), Email_svr.config("password"))
        server.sendmail(Email_svr.config("from"),usr[4], msg_full)
        
        server.quit()        
        
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
    
  
