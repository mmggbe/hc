#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Server that manages the care rules alarms and that dispatchs them to the right channel
'''
VERSION = '1.0'


from datetime import date, time, datetime, timezone

import os
import sys
import argparse
import pytz

import logging
from logging.handlers import TimedRotatingFileHandler

from notifier import send_notification
from GW_DB.Dj_Server_DB import DB_mngt, DB_gw


from HCsettings import HcDB, EventCode,  HcLog

   
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
                        help='define the hclog level, the default is %(default)s')

  
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s - v' + VERSION)

    opts = parser.parse_args()
    return opts
   

def Main():
    
    opts = getopts() 
     
    logPath= HcLog.config("logPath")
    retentionTime = int(HcLog.config("retentionTime"))
    moduleName = "care_svr"
    
    hclog = logging.getLogger()   # must be the rotlogger, otherwise sub-modules will not benefit from the config.
     
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
  
    print('Care Server starting up')
    hclog.info('Care Server starting up' )

    db_cur= DB_mngt( HcDB.config() ) 

    if db_cur.echec:
        hclog.info("Cannot open DB")
        exit()

    else :
        
        
        # get naive date
        current_tz = pytz.timezone('Europe/Brussels')
        date = datetime.now().date()
        
      
        gwDB=DB_gw(db_cur)
        gw_list = gwDB.search_gw_with_Care_flag( "1" )
       
        for gw in gw_list:
            hclog.info("Scan rules of Gw= {}, current time= {}".format(gw[0], datetime.today().strftime("%Y-%m-%d %H:%M:%S") ) )
            
            rules= gwDB.search_rules_from_gwID( gw[0] )
    
            for rule in rules:
                hclog.info("Rule: sensor_id {}, start_time {}, end_time {}".format(rule[1],rule[2],rule[3]) )
                
                dt= datetime.combine(date, time(0, 0) ) + rule[2]
                start = current_tz.localize(dt).astimezone(pytz.utc)                             # convert to UTC time
 
                
                dt = datetime.combine(date, time(0, 0) ) + rule[3]
                end  = current_tz.localize(dt).astimezone(pytz.utc)                                # convert to UTC time

                
                if start <= datetime.now(timezone.utc) <= end:   # we are between the start and the end of the rule               
                    if rule[4] != "1":          # rule was not valid during the last script run
                        gwDB.upd_in_rule_flag(rule[0], "1")      # update flag of rule id
                        hclog.debug("Rule is applicable")
 
                        break
                
                
                else:
                    if rule[4] == "1":          # the rule was valid during the last script run
                        gwDB.upd_in_rule_flag(rule[0], "0")      # deactivate flag of rule id
                        
                        evt_list = gwDB.apply_rule(rule[1], start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"))   # check if there was sensor messages between start and end time
                        hclog.debug( "Event List= {}".format(evt_list) )
                        if len(evt_list) == 0:
                            hclog.debug( "No event found during rule validity period" )
                            
                            snsr_list = gwDB.search_sensors_name_from_gwID( gw[0]) # get sensors from gateways
                            sensor_name=""
                            for s in snsr_list:                     # search for sensor name based on sensor ID
                                if rule[1] == s[0]:
                                    sensor_name=s[2]
                                    break 
                           
                            no_event= ("900", "Event: No motion detected on sensor {}".format(sensor_name), EventCode.value("900")[1], None)
                            usr_profile = gwDB.search_usrprofile_from_gwID( gw[0] ) # get usr_profile from gateway = username, propertyaddr, SN_SMS, SN_Voice, prof.email, language
                            now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        
                            req="INSERT INTO {} (timestamp, userWEB_id, type, gwID_id, sensorID_id, event_code, event_description) VALUES ( %s, %s, %s, %s, %s, %s, %s )".format("history_events")                                                                         
                            value= (now, usr_profile[0][0], "CR", gw[0],no_event[3], no_event[0], no_event[1])
            
                            db_cur.executerReq(req, value)
                            db_cur.commit() 

                            send_notification(usr_profile[0], no_event)
 
        db_cur.close()       
    
    hclog.info('Finished' )

        
if __name__ == '__main__':
    Main()
