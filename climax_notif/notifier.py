#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json 
import logging

import os, sys, stat
import shutil
import subprocess
import tempfile
from datetime import datetime

import smtplib
from email.mime.text import MIMEText

from HCsettings import SMS_Notif, HcDB, Email_svr



def send_notification(usr, event):
# list usr [username, propertyaddr, SN_SMS, SN_Voice, email, language]
# list event eg: '100', "Medical", [ "1", "0", "0"] # code : "description, email to be sent, sms to be sent, voice call to be issued

    hclog=logging.getLogger(__name__)
    
    hclog.info("Notification to user id:{}, content : {}".format(usr[0],event[1]))
    hclog.debug("Notification to user:{}, content : {}".format(usr,event))

    if event[2][0] == '1' and usr[4].strip() != "":            # check if email to send and email field

    #https://stackoverflow.com/questions/24077314/how-to-send-an-email-with-style-in-python3
        hclog.info(" Sending email to email : {}".format(usr[4]) )
                
#       title = 'Horus supervisor:'
#       msg_content = '<h2>{title} > <font color="green">OK</font></h2>\n'.format(title=event)
 
        EMAIL_CONTENT = """
<html>
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type">
  </head>
  <body>Hi, <br>
    <br>
    The following event has been detected at {2} on: <br>
    [property] <font color="green"> <br>
      {0} </font> <br>
    [event] <font color="green"> <br>
      {1} </font> <br>
    Please take the appropriate actions <br>
    <br>
    Best regards <br>
    Your Horus Monitoring System
    
  </body>
</html>

"""
        
        message = MIMEText(EMAIL_CONTENT.format(usr[1],event[1], datetime.today().strftime("%Y-%m-%d %H:%M:%S")) , 'html')
        hclog.info("MIME text : usr {} event {}".format(usr[1],event[1]) )
        
        message['From'] = Email_svr.config("from")
        message['To'] = usr[4]
        #message['Cc'] = 'Receiver2 Name <receiver2@server>'
        message['Subject'] = 'Horus supervisor : your property: {}'.format(usr[1].split("\r")[0])
        
        msg_full = message.as_string()

        try:
            server = smtplib.SMTP(Email_svr.config("server"),587)
            server.starttls()
            server.ehlo()
            server.login(Email_svr.config("login"), Email_svr.config("password"))
            server.sendmail(Email_svr.config("from"),usr[4], msg_full)

        except smtplib.SMTPException as error :
            hclog.info("Email to user ID {} failed, error:{}".format(usr[0],str(error)) )

        else:
            server.quit()  
            hclog.debug("email sent ")         
        
    if event[2][1] =='1' and usr[2].strip() != "" :                # check if SMS to send and MSISDN field
        hclog.info(" Sending SMS to MSISDN {}".format(usr[2]) )
        
        try:
            hclog.debug("EnCo SMS API: Acquiring token")
              
            payload = {'grant_type': 'client_credentials', 'scope': 'openid'}  
            
            enco_perm_token = SMS_Notif.config("enco_secret" )
            if enco_perm_token and enco_perm_token.strip():             # there is a EnCO SMS permanent token in the HCsettings.py file
                tokenBearer = enco_perm_token
                hclog.debug("Using Enco permanent token for SMS sending" )   

                
            else:                                                       # use Marc account and accquire tmp token
              
                r = requests.post("https://api.enco.io/token", data=payload, auth=(SMS_Notif.config("client_id"), SMS_Notif.config("client_secret")))
                hclog.debug("Get token {}\n".format(r.text))
                
                authInfo = r.json()
                tokenBearer = authInfo['access_token']
        
                hclog.debug("Using token to retrieve user information")
                
                auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Accept':'application/json'}
                r = requests.get("https://api.enco.io/userinfo?schema=openid", headers=auth_header)
                hclog.debug("Get user info {}\n".format(r.text))
                userInfo = r.json()
                
                hclog.debug("Name: {}, Given name: {}, Familly name: {}, Email: {}\n".format(userInfo['name'],userInfo['given_name'], userInfo['family_name'],userInfo['email']) )   
                
            """
            curl -i -X POST 'https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false' 
            -H 'Authorization: Bearer 674f4fc8db0000000083e887306cd8' 
            -H 'Content-Type: application/json' 
            -H 'Accept: application/json'  
            -d '{"message":"Hello World Test Message","destinations":["+32000000000"]}'
            """
            msg="Horus Monitoring: " + event[1]        # still to limit to 140 char.
            dest=[(usr[2]),]
             
            payload = json.dumps( {'message':msg,'destinations':dest} )

            auth_header = {'Authorization':'Bearer {}'.format(tokenBearer), 'Content-Type':'application/json', 'Accept':'application/json'}
            r = requests.post("https://api.enco.io/sms/1.0.0/sms/outboundmessages?forceCharacterLimit=false", data=payload, headers=auth_header)
            
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as error:
            hclog.info("SMS to user ID {} failed, error:{}".format(usr[0],str(error)) )

        finally:
            hclog.info("Sent SMS {}\n".format(r.text))  
     
            
    if event[2][2] =='1' and usr[3].strip() != "" :                # check if Voice to call and MSISDN field
        hclog.info(" Calling MSISDN {}".format(usr[3]) )
        
        VOICE_MSG_CONTENT = """
Hello\n
This is you Horus monitoring system calling you.\n
An event happened to your property : {}\n
Please take the appropriate actions\n
Bye

"""
        msg= VOICE_MSG_CONTENT.format(event[1])
#create a temporary file name        
        tf = tempfile.NamedTemporaryFile(delete=False)
        wavFile = tf.name + ".wav"
        
        try:
#        ESPEAK_BIN= ['/usr/bin/espeak', '-a', '100', '-p', '50', '-s', '170', '-g', '10', '-v', 'en', msg, '--stdout']
            ESPEAK_BIN= ['/usr/bin/espeak', '-a', '100', '-p', '50', '-s', '140', '-g', '6', '-v', 'en+12', msg, '--stdout']           
            SOX_BIN= ['/usr/bin/sox', '-', '-b', '16','-r','8000', wavFile ]
          
                    #ficher .wav doivent être codé 8 bits Khz      
            ps = subprocess.Popen(ESPEAK_BIN, stdout=subprocess.PIPE)
            output = subprocess.check_output(SOX_BIN, stdin=ps.stdout)
            ps.wait()

        except Exception as e:
            errno, strerror = e.args
            hclog.info("Error voice synthese, error({0}): {1}".format(errno,strerror))

        VOICE_ENV = """
Channel: SIP/belgacom/{}\n\
CallerID: "Horus" <+3222196052>\n\
Application: Playback\n\
Data: {}\n\
SetVar: CHANNEL(language)=en\n
"""
        env=VOICE_ENV.format( usr[3].strip(),tf.name )     
  
        try:
             
            eventFile = tempfile.NamedTemporaryFile(delete=False,suffix=".call")
            fd = os.open(eventFile.name,  os.O_RDWR|os.O_CREAT)    
            
            # Horus needs to be in the same group as Asterisk
            os.fchmod(fd, stat.S_IRGRP | stat.S_IWGRP | stat.S_IWUSR | stat.S_IRUSR | stat.S_IROTH)       
               
            # don't put the ".wav" extension in the enveloppe
            os.write(fd, str.encode(env))
        
#SetVar: CHANNEL(language)=en\n".format("/tmp/text") )
            os.close(fd)

            shutil.move(eventFile.name, "/var/spool/asterisk/outgoing")
            
        except IOError as e:
            hclog.info("I/O error({0}): {1}, cannot move ".format(e.errno, e.strerror))
            
        except OSError as err:
            hclog.info("OS error: {0}".format(err))
            
        except:
            hclog.info("Unexpected error:{}".format(sys.exc_info()[0]))

        finally:
            hclog.debug('Asterisk envelop file {}'.format(eventFile.name))
            hclog.debug("Voice call submitted")  

