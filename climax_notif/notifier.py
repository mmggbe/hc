#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json 
import logging

import shutil
import subprocess

import smtplib
from email.mime.text import MIMEText

from HCsettings import Notifier, HcDB, Email_svr





def send_notification(usr, event):
# list usr [username, propertyaddr, SN_SMS, SN_Voice, email, language]
# list event eg: '100', "Medical", [ "1", "0", "0"] # code : "description, email to be sent, sms to be sent, voice call to be issued


    if event[2][0] and usr[4] and usr[4].strip:            # check if email to send and email field

    #https://stackoverflow.com/questions/24077314/how-to-send-an-email-with-style-in-python3
        logging.info(" Sending email to email {} of user ID {}".format(usr[4], usr[0]) )
                
 #       title = 'Horus supervisor:'
 #       msg_content = '<h2>{title} > <font color="green">OK</font></h2>\n'.format(title=event)
 
        EMAIL_CONTENT = """
<html>
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type">
  </head>
  <body>Hi,
    <br>
    <br>
    The following event has been detected:
    <br>
    <br>
    [property] <font color="green">
      <br>
      {0}
    </font>
    <br><br>
    [event] <font color="green">
      <br>
      {1}
    </font>
    <br>
    <br>
    Please take the appropriate actions
    <br>
    <br>
    Best regards
    <br>
    Your Horus Monitoring System
  </body>
</html>

"""
        
        message = MIMEText(EMAIL_CONTENT.format(usr[1],event[1]), 'html')
        
        message['From'] = Email_svr.config("from")
        message['To'] = usr[4]
        #message['Cc'] = 'Receiver2 Name <receiver2@server>'
        message['Subject'] = 'Horus supervisor : your property: {}'.format(usr[1])
        
        msg_full = message.as_string()
        
        try:
            server = smtplib.SMTP(Email_svr.config("server"),587)
            server.starttls()
            server.ehlo()
            server.login(Email_svr.config("login"), Email_svr.config("password"))
            server.sendmail(Email_svr.config("from"),usr[4], msg_full)

        except smtplib.SMTPException as error :
            logging.info("Email to user ID {} failed, error:{}".format(usr[0],str(error)) )

        finally:
            server.quit()  
        
        
    if event[2][1] and usr[2] and usr[2].strip :                # check if SMS to send and MSISDN field
        logging.info(" Sending SMS to MSISDN {} from user ID {}".format(usr[2], usr[0]) )
        
        try:
            logging.debug("EnCo SMS API: Acquiring token\n")
              
            payload = {'grant_type': 'client_credentials', 'scope': 'openid'}         
            r = requests.post("https://api.enco.io/token", data=payload, auth=( Notifier.config("client_id"), Notifier.config("client_secret")))
            logging.debug("Get token {}\n".format(r.text))
            
            authInfo = r.json()
            tokenBearer = authInfo['access_token']
    
            logging.debug("Using token to retrieve user information\n")
            
            auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Accept':'application/json'}
            r = requests.get("https://api.enco.io/userinfo?schema=openid", headers=auth_header)
            logging.debug("Get user info {}\n".format(r.text))
            userInfo = r.json()
            
            logging.debug("Name: {}, Given name: {}, Familly name: {}, Email: {}\n".format(userInfo['name'],userInfo['given_name'], userInfo['family_name'],userInfo['email']) )   
            
            """
            curl -i -X POST 'https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false' 
            -H 'Authorization: Bearer 674f4fc8db0000000083e887306cd8' 
            -H 'Content-Type: application/json' 
            -H 'Accept: application/json'  
            -d '{"message":"Hello World Test Message","destinations":["+32000000000"]}'
            """
            
            if False:            # to avoid to waste SMS credit during testing
                
#                payload = json.dumps( {'message':'Hello Marc 2','destinations':['+32475618115']} )
                msg=("Horus: "+usr[0]+": "+event[1])        # still to limit to 140 char.
                dest=[(usr[2]),]
                 
                payload = json.dumps( {'message':msg,'destinations':dest} )

                auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Content-Type':'application/json', 'Accept':'application/json'}
                r = requests.post("https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false", data=payload, headers=auth_header)
                
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as error:
            logging.info("SMS to user ID {} failed, error:{}".format(usr[0],str(error)) )

        finally:
            logging.info("Sent SMS {}\n".format(r.text))  

            
            
    if event[2][2] and usr[3] and usr[3].strip :                # check if Voice to call and MSISDN field
        logging.info(" Calling MSISDN {} from user ID {}".format(usr[3], usr[0]) )
        
        VOICE_MSG_CONTENT = """
Hello\n
This is you Horus monitoring system calling you.\n
An event happened to your propoerty : {}\n
Please take the appropriate actions\n
Bye

"""
        msg= VOICE_MSG_CONTENT.format(event[1])
        
        ESPEAK_BIN= ['/usr/bin/espeak', '-a', '100', '-p', '50', '-s', '170', '-g', '10', '-v', 'en', msg, '--stdout']
        SOX_BIN= ['/usr/bin/sox', '-', '-b', '16','-r','8000', '/tmp/text.wav' ]
      
                #ficher .wav doivent être codé 8 bits Khz      
        ps = subprocess.Popen(ESPEAK_BIN, stdout=subprocess.PIPE)
        output = subprocess.check_output(SOX_BIN, stdin=ps.stdout)
        ps.wait()
 
        fichier = open("evt.call", "w")       
                # don't put the ".wav" extension in teh enveloppe
        fichier.write(
"Channel: SIP/6001\n\
Application: Playback\n\
Data: {}\n\
SetVar: CHANNEL(language)=en\n".format("/tmp/text") )
        
        fichier.close()

        try:
            shutil.move("evt.call", "/var/spool/asterisk/outgoing")
            
        except IOError as e:
            logging.info("I/O error({0}): {1}, cannot move ".format(e.errno, e.strerror))

        finally:
            logging.info('Test Call')



