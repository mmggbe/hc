#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server that manages the reported alarms and that dispatchs them to the right channel
'''
VERSION = '1.0'

import socket
import time
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
                
def translate(contactID):
    
    alarmMsg=""
#[0730#74 18_1_751_00_003_2CA2]
#         MT Q XYZ GG CCC
    Q = contactID[-14:-13]
    evt= contactID[-13:-10]
    GG = contactID[-10:-8] 
    sensor= contactID[-7:-5]
    
#    print("Event={}".format(evt))
    try:

        alarmMsg += ArmingRequest.value(GG)
        alarmMsg += ": "
        
        if Q== '1':
            if sensor == '14' or sensor == '15' :
                alarmMsg += "Disarm: "
            else:
                alarmMsg += "New event: "
                
        elif Q == '3':
            if sensor == '14' or sensor == '15' :
                alarmMsg += "Armed: "
            else:
                alarmMsg += "Restore: "
        else:
            alarmMsg += ""
        
        
        # arm vie RC
        if evt == '400':
            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += "User "
            alarmMsg += sensor
            
        # arm via WEB
        elif evt =='401' and (sensor == '14' or sensor == '15'):
            alarmMsg += EventCode.value(evt)[0]

        # arm via Keypad
        elif evt == '407':
            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += "User "
            alarmMsg += sensor

        
        else:
            alarmMsg += EventCode.value(evt)[0] # add event name on the message
            alarmMsg += " Sensor "
            alarmMsg += sensor
            
        
    except:
        logging.info("Error ContactID: {}".format(contactID))
        return( "" )
        
    else:
#        print("Event= {}".format(alarmMsg), end='')
        logging.info("Event: {}".format(alarmMsg))
        return( evt, alarmMsg ) 

   
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
                        
                        
                        now = time.strftime("%Y-%m-%d %H:%M:%S")                        
                        logging.info("Contact ID: {} {} ".format(now, data))
                      
                        try:                         
                            data = data.decode()                                
                                               
                            if Contact_ID_filter.match(data):
                                connection.sendall( b'\x06' )       # respond only if Contact ID is correct
                                
                                logging.debug("Contact ID OK, acknowledge sent")
                                
                                event = translate(data)
        #                        [0730#74 181751000032CA2]   
                                rptipid = data[1:5]
                                tmp = data[6:].split(' ')
                                acct2 = tmp[0]
                                
                                db_cur= DB_mngt( HcDB.config() ) 
    
                                if db_cur.echec:
                                    logging.info("Cannot open DB")
    
                                else :
                                    gw=DB_gw(db_cur)
                                    gw_id = gw.search_gw_from_acct( rptipid, acct2 )
    
                                    if gw_id == []:    
                                        logging.info( " No Gw found with acct2= {}".format(acct2))
                                    else:
                                        logging.info( " on Gw_id {}".format(gw_id[0][0]))
               
                                        req="INSERT INTO {} (event, eventtime, gwID_id) VALUES ( %s, %s, %s )".format("alarm_events")
                                        value= (data, now, gw_id[0][0],)
                                        db_cur.executerReq(req, value)
                                        db_cur.commit() 
                                        usr=gw_id.userWEB
                                        
                                    db_cur.close()                               
                                    send_notification(usr, event)


                                         
                            else:
                                logging.info("Error: bad contact id format")

                        except:
                            logging.info("Error: bad Contact ID translation or user not found in DB or during writing DB")
                                 
                    else:
#                        print ('no more data from {}'.format(client_address))
                        break   
                                    
               
                    
    
        finally:
            # Clean up the connection
            connection.close()


    db_cur.close()       
            
            
            
           
            
        
if __name__ == '__main__':
    Main()