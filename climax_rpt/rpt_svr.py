#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server that manages the reported alarms and that dispatchs them to the right channel
'''
VERSION = '1.0'

import socket
#import time
import datetime
import re
import os
import sys
import argparse
import logging
from notifier import send_notification

from socket import error as SocketError
import errno


from GW_DB.Dj_Server_DB import DB_mngt, DB_gw
from HCsettings import HcDB, Rpt_svr, EventCode, ArmingRequest



# examle of contact Id received : [0730#74 181751000032CA2]
                
def translate(contactID, snsr_list, usr_list):
    
    alarmMsg=""
#[0730#74 18_1_751_00_003_2CA2]
#[0730#119 18 3 401 00 015 C0CF]
#          MT Q EEE GG ZZZ

    Q = contactID[-14:-13] # Q: Event qualifier 1: new event & disarm 3: restore & arm
    evt= contactID[-13:-10]  # EEE: event code
    GG = contactID[-10:-8] # GG: partition number (always 00 for non partitioned panels)
    sensor_id= contactID[-7:-5]  # ZZZ: representing zone number C 1 = 0 (fixed) , C 2 C 3 = Zone number
    
    sensor=""
    sensor_id = sensor_id.lstrip('0') or '0' # remove leading zeros in text string
    

    try:
        
        if evt == "401" or evt == "407" :
            
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
                if sensor_id == s[0]:
                    sensor_name=s[1]
                    sensor_type=s[2]
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
                
        else:          
                
            sensor_name=""
            for s in snsr_list:                     # search for sensor name based on sensor ID
                if sensor_id == s[0]:
                    sensor_name=s[1]
                    sensor_type=s[2]
                    break 
            
            if Q == '1':                            # new event
                alarmMsg += "Event: "
                alarmMsg += EventCode.value(evt)[0] # add event name on the message
                alarmMsg += " Sensor "
                alarmMsg += sensor_name

            else:      
                evt = '000'                         #  Q = 3 : Restore event : no need to process that message

    except:
        logging.info("Error ContactID: {}, evt:{}, GG:{}, sensorid:{}".format(contactID,evt, GG, sensor_id))
        return( "" )
        
    else:
        logging.debug("Event: {}".format(alarmMsg))
        return( evt, alarmMsg, EventCode.value(evt)[1] ) 

   
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
   

def get_logging_level(opts):
    '''
    Get the logging levels specified on the command line.
    The level can only be set once.
    '''
    if opts.level == 'notset':
        return logging.NOTSET
    elif opts.level == 'debug':
        return logging.DEBUG
    elif opts.level == 'info':
        return logging.INFO
    elif opts.level == 'warning':
        return logging.WARNING
    elif opts.level == 'error':
        return logging.ERROR
    elif opts.level == 'critical':
        return logging.CRITICAL

def err(msg):
    '''
    Report an error message and exit.
    '''
    logging.debug('ERROR: %s' % (msg))
    sys.exit(1)


def Main():
    
    opts = getopts()  
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=get_logging_level(opts))

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    
    server_ip = Rpt_svr.config("ip")
    server_port = Rpt_svr.config("port")
    server = (server_ip, int(server_port))
    
    logging.info('starting up on %s port %s' % server)
    sock.bind(server)
    # Listen for incoming connections
    sock.listen(1)

    Contact_ID_filter = re.compile(r'^\[[0-9A-Fa-f]{4}#[0-9A-Fa-f\s]{4}18[0-9A-Fa-f\s]{13}\]$') # contact ID
                      
    
    while True:
        # Wait for a connection
#        print ('waiting for a connection')
        
        try:
            connection, client_address = sock.accept()
#        print ('connection from {}'.format(client_address))
    
        # Receive the data in small chunks and retransmit it
            while True:
         
                try: 
                    data = connection.recv(32)
                    
                except SocketError as e:
                    errno, strerror = e.args
                    logging.info("Socket errorI/O error({0}): {1}".format(errno,strerror))

                else:
                    
                    if data:
                        
                        now=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
#                        now = time.strftime("%Y-%m-%d %H:%M:%S")                        
                        logging.info("Contact ID: {} {} ".format(now, data))
                      
                        try:                         
                            data = data.decode()                                
                                               
                            if Contact_ID_filter.match(data):
                                connection.sendall( b'\x06' )       # respond only if Contact ID is correct
                                
                                logging.debug("Contact ID format OK, acknowledge sent")
                                 
                                rptipid = data[1:5]
                                tmp = data[6:].split(' ')
                                acct2 = tmp[0]
                                
                                db_cur= DB_mngt( HcDB.config() ) 
    
                                if db_cur.echec:
                                    logging.info("Cannot open DB")
    
                                else :
                                    gw=DB_gw(db_cur)
                                    gw_id = gw.search_gw_from_acct( rptipid, acct2 ) # returns gateways_id
    
                                    if gw_id == []:    
                                        logging.info( " No Gw found with acct2= {}".format(acct2))
                                    else:
                                        logging.debug( " on Gw_id {}".format(gw_id[0][0]))
               
                                        

                                        snsr_list = gw.search_sensors_name_from_gwID( gw_id[0][0] ) # get sensors from gateways
                                        usr_list = gw.search_users_name_from_gwID( gw_id[0][0] ) # get users from gateways)
                                        
                                        event=[] # data          [0730#74 181751000032CA2] 
                                        event = translate(data, snsr_list, usr_list) # returns event code, formated alarm message, event action (send SMS, email , call) 
                                        
                                        if event[0] != '000':
                                            usr_profile = gw.search_usrprofile_from_gwID( gw_id[0][0] ) # get usr_profile from gateway = username, propertyaddr, SN_SMS, SN_Voice, prof.email, language
                                        
                                            req="INSERT INTO {} (timestamp, userWEB_id, type, gwID_id, event_code, event_description) VALUES ( %s, %s, %s, %s, %s, %s )".format("history_events")                                                                         
                                            value= (now, usr_profile[0][0], "GW", gw_id[0][0],event[0], event[1], )
                                            db_cur.executerReq(req, value)
                                            db_cur.commit() 
                                    
                                    db_cur.close()                               
                                    send_notification(usr_profile[0], event)


                                         
                            else:
                                logging.info("Error: bad contact id format")

                        except:

                            if db_cur in locals():
                                db_cur.close()  

                            logging.info("Error: bad Contact ID translation or user error in DB or issue sending notification")
                                 
                    else:
#                        print ('no more data from {}'.format(client_address))
                        break   
                                    
               
                    
    
        finally:
            # Clean up the connection
            connection.close()


    db_cur.close()       
            
            
            
           
            
        
if __name__ == '__main__':
    Main()
