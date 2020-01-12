#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server that manages the reported alarms and that dispatchs them to the right channel
'''
VERSION = '2.0'


import socket
import socketserver
import datetime
import re
import os
import sys
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler

from notifier import send_notification

from socket import error as SocketError
import errno


from GW_DB.Dj_Server_DB import DB_mngt, DB_gw, DB_camera

from HCsettings import HcDB, Rpt_svr, EventCode, ArmingRequest, HcLog


# examle of contact Id received : [0730#74 181751000032CA2]
                
def translate(contactID, snsr_list, usr_list):

    hclog = logging.getLogger(__name__)
      
    alarmMsg=""
#[0730#74 18_1_751_00_003_2CA2]
#[0730#119 18 3 401 00 015 C0CF]
#          MT Q EEE GG ZZZ

    Q = contactID[-14:-13] # Q: Event qualifier 1: new event & disarm 3: restore & arm
    evt= contactID[-13:-10]  # EEE: event code
    GG = contactID[-10:-8] # GG: partition number (always 00 for non partitioned panels)
    sensor_id= contactID[-7:-5]  # ZZZ: representing zone number C 1 = 0 (fixed) , C 2 C 3 = Zone number
    
    sensor_id = sensor_id.lstrip('0') or '0' # remove leading zeros in text string
    sensor_ref_id=None

    try:
        
        if evt == "401" or evt == "407" :     # GW has been armed/disarmed via Keyfob or Keypad
            
            user_name="WEB"                   # if user is not found then user is type 14, meaning WEB but redundant with message type "401"
            for u in usr_list:                  # search for sensor name based on sensor ID
                if sensor_id == u[0]:
                    user_name=u[1]
                    break 
        
            if Q == '1':
                alarmMsg = "Disarmed with "
            else: 
                alarmMsg = "Armed with "

            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += " by user "                 
            alarmMsg += user_name      

        elif evt == "400" :
            
            sensor_name=""                          # keyfob searched based on device name
            for s in snsr_list:                     # search for sensor name based on sensor ID
                if sensor_id == s[1]:
                    sensor_name=s[2]
                    sensor_type=s[3]
                    sensor_ref_id=s[0]
                    break 
       
            if Q == '1':
                alarmMsg = "Disarmed with "
            else: 
                alarmMsg = "Armed with "

            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += ": "                 
            alarmMsg += sensor_name      

        
        elif evt == "602":     
            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += " = OK"
            sensor_id = None                        # the GW is not a sensor, will give a NULL in the history DB
                
        else:          
                
            sensor_name=""
            for s in snsr_list:                     # search for sensor name based on sensor ID
                if sensor_id == s[1]:
                    sensor_name=s[2]
                    sensor_type=s[3]
                    sensor_ref_id=s[0]
                    break 
            
            if Q == '1':                            # new event
                alarmMsg += "Event: "
                alarmMsg += EventCode.value(evt)[0] # add event name on the message
                alarmMsg += " Sensor "
                alarmMsg += sensor_name

            else:      
                evt = '000'                         #  Q = 3 : Restore event : no need to process that message
                alarmMsg = "Event: Restore"

    except:
        hclog.info("ERROR ContactID: {}, evt:{}, GG:{}, sensorid:{}".format(contactID,evt, GG, sensor_id))
        return( "" )
        
    else:
        hclog.debug("Event: {}".format(alarmMsg))
        return( evt, alarmMsg, EventCode.value(evt)[1], sensor_ref_id ) 

   

  
 
class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    allow_reuse_address = 1    # otherwise bind error when starting teh 2nd thread

    def handle(self):

        Contact_ID_filter = re.compile(r'^\[[0-9A-Fa-f]{4}#[0-9A-Fa-f\s]{4}18[0-9A-Fa-f\s]{13}\]$') # contact ID
                      
        self.data = self.request.recv(32)
                   
        now=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        hclog.info("Contact ID: UTC {} {} [client {}]".format(now, self.data, self.client_address[0]) )

        try:
            data = self.data.decode()                                
                                   
            if Contact_ID_filter.match(data):
                self.request.sendall( b'\x06' )       # respond only if Contact ID is correct
                 
                hclog.debug("Contact ID format OK, acknowledge sent")
                  
                rptipid = data[1:5]
                tmp = data[6:].split(' ')
                acct2 = tmp[0]
                 
                db_cur= DB_mngt( HcDB.config() ) 

                if db_cur.echec:
                    hclog.info("Cannot open DB")

                else :
                    gw=DB_gw(db_cur)
                     
                    # returns the_id of the gateway                              
                    gw_id = gw.search_gw_from_acct( rptipid, acct2 ) 

                    if gw_id == []:    
                        hclog.info( " No Gw found with acct2= {}".format(acct2))
                    else:
                        hclog.debug( " on Gw_id {}".format(gw_id[0][0]))

                        snsr_list = gw.search_sensors_name_from_gwID( gw_id[0][0] ) # get sensors from gateways
                        usr_list = gw.search_users_name_from_gwID( gw_id[0][0] ) # get users from gateways)
                         
                        event=[] # data          [0730#74 181751000032CA2] 
                        event = translate(data, snsr_list, usr_list) # returns event code, formated alarm message, event action (send SMS, email , call) 
                         
                        if event[0] != '000':
                             
                            #get info about user
                            #user_id, propertyaddr, SN_SMS, SN_Voice, prof.email, language "
                             
                            usr_profile = gw.search_usrprofile_from_gwID( gw_id[0][0] ) # get usr_profile from gateway = username, propertyaddr, SN_SMS, SN_Voice, prof.email, language
                         
                            req="INSERT INTO {}"\
                                 "(timestamp, userWEB_id, type, gwID_id, sensorID_id, event_code, event_description)"\
                                 " VALUES ( %s, %s, %s, %s, %s, %s, %s )".format("history_events")                                                                         
                            value= (now, usr_profile[0][0], "GW", gw_id[0][0], event[3], event[0], event[1])
                            db_cur.executerReq(req, value)
                            db_cur.commit()
                             
                            send_notification(usr_profile[0], event)
                             

                            if event[0] == "400" or event[0] == "407" :            # check if Horus has been armed via keyfob / keypad, then arm camera if relevant
                                 
                                if event[1][:5] == "Armed":                     # dirty implementation ;-) , should pass the alarm status instead
                                    securityStatus = 1
                                elif event[1][:8] == "Disarmed":                     # dirty implementation ;-) , should pass the alarm status instead
                                    securityStatus = 0
                                else:
                                    securityStatus = 9
                                  
                                if securityStatus == 0 or securityStatus == 1:
                                     
                                    cam_cursor=DB_camera(db_cur)                                        
                                    cam_list = cam_cursor.search_cam_list_from_user(usr_profile[0][0])
                                    # returns : id, securityStatus (char), activateWithAlarm (Bolean)
                                    for cam in cam_list:
                                         
                                        if cam[2]== 1:
                                 
                                            #send "Arm/Disarm command to the camera"
                                            #add_camera_cmd( self, cam_id, cmd):
                                            cam_cursor.add_camera_cmd(cam[0], 'GET /adm/set_group.cgi?group=SYSTEM&pir_mode={} HTTP/1.1\r\n'.format(securityStatus) )
                                            cam_cursor.add_camera_cmd(cam[0], 'GET /adm/set_group.cgi?group=EVENT&event_trigger=1&event_interval=0&event_pir=ftpu:1&event_attach=avi,1,10,20 HTTP/1.1\r\n')

                                            #change the camera security status 
                                            #update_camera_status(self, cam_id, status)
                                            cam_cursor.update_camera_security_flag(cam[0], securityStatus)

                                            db_cur.commit()
                                            hclog.info("Camera {} Armed/disarmed ( {} ) on Gw {} request".format(cam[0], securityStatus, gw_id[0][0] ) )
        
                    # "if..." close the opened DB                                            
                    db_cur.close()                               


            # data not matching the Contact ID format              
            else:
                hclog.info("ERROR: Bad Contact ID: UTC {} {} [client {}]".format(now, self.data, self.client_address[0]) )

        except:

            if 'db_cur' in locals():
                db_cur.close()  

            hclog.info("ERROR: bad Contact ID translation or user error in DB or issue sending notification: UTC {} {} [client {}]".format(now, self.data, self.client_address[0]))

        finally:
            self.request.close()

def getopts():
    '''
    Get the command line options.
    '''

    # Get the help from the module documentation.
    this = os.path.basename(sys.argv[0])
    description = ('description:%s' % '\n  '.join(__doc__.split('\n')))
    epilog = ' '
    rawd = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=rawd,
                                     description=description,
                                     epilog=epilog)

    parser.add_argument('-l', '--level',
                        action='store',
                        type=str,
                        default='info',
                        choices=['notset', 'debug', 'info', 'warning', 'error', 'critical',],
                        help='define the logging level, the default is %(default)s')

  
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s - v' + VERSION)

    opts = parser.parse_args()
    return opts


        
if __name__ == '__main__':
    
    opts = getopts() 
     
    logPath= HcLog.config("logPath")
    retentionTime = int(HcLog.config("retentionTime"))
    moduleName = "reporting_svr"
    
    hclog = logging.getLogger()   # must be the rootlogger, otherwise sub-modules will not benefit from the config.
     
    handler = TimedRotatingFileHandler(logPath + moduleName + '.log',
                                  when='midnight',
                                  backupCount=retentionTime)   
    if opts.level == 'debug':
        hclog.setLevel(logging.DEBUG) 
        handler.setLevel(logging.DEBUG) 
    else:
        hclog.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)      
        
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',datefmt='%b %d %H:%M:%S')
    handler.setFormatter(formatter)

    hclog.addHandler(handler)
    
    """
   
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port    
    sock.bind(server)
    
    # Listen for incoming connections
    sock.listen(1)
    """    
    server_ip = Rpt_svr.config("ip")
    server_port = Rpt_svr.config("port")
    server = (server_ip, int(server_port))
    
    hclog.info('starting up on %s port %s' % server)
    print("Starting up on %s port %s" % server)

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer(server, MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()  


