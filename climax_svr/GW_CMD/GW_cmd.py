#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on 2 nov. 2016

@author: marc
'''
import time
import sys
import logging
from random import randrange


from lxml import etree
from GW_DB.Dj_Server_DB import DB_mngt, DB_gw
from HCsettings import HcDB,GW_Pol_svr, Rpt_svr, HcLog



CLIMAX_CMD_HDR  = """
<?xml version="1.0" encoding="ISO-8859-1"?>"""
 
CLIMAX_CMD_SUB_HDR = """
<polling>
    <mac value={} />
    <rptipid value="{}" />
    <commands>"""

CLIMAX_CMD_TAIL ="""
    </commands>
</polling>"""


class cmdTo_climax():
    '''
    Command sent to the CLimax GW
    '''


    def __init__(self,db_cur, MAC, user_ID, GW_ID, rptip_ID):
        '''
        Constructor
        '''
       
        self.db_cur = db_cur 
        self.MAC = MAC
        self.user_ID = user_ID
        self.GW_ID = GW_ID
        self.rptip_ID = rptip_ID
        self.queue = cmd_queue(db_cur)
        self.hclog=logging.getLogger(__name__)

# regular polling answer (no command to be sent     
    def polling(self, rptipid):
        
        CLIMAX_CMD_BODY = """
<polling>
    <mac value="{}"/>
    <rptipid value="{}"/>
    <date value="{}" />
</polling>"""      
        response = CLIMAX_CMD_HDR+CLIMAX_CMD_BODY.format( self.MAC, rptipid, time.strftime("%Y-%m-%d %H:%M:%S"))
        self.hclog.debug("Polling response to GW= {0}\n".format(response) )

        return response
    
    # rptipid has to remains empty for the GW registration
    # it seems command id doesn't matter


    
    def autoRegister(self, rptipid, acct2):

        CLIMAX_CMD_BODY= """
<polling>
    <mac value="{0}"/>
    <rptipid value=""/>
    <commands>
        <command id="105" action="setPolling">
            <url1 value="polln://{1}:{2}" />
            <interval value="20" />
            <errnotify value="20" />
        </command>
        <command id="106" action="setRpt">
            <url1 value="rptn://{3}@{4}:{5}" />
            <acct2 value="{6}" />
        </command>
    </commands>
</polling>"""
        response = CLIMAX_CMD_HDR+CLIMAX_CMD_BODY.format( self.MAC, \
            GW_Pol_svr.config("ip"), GW_Pol_svr.config("port") , \
            rptipid, Rpt_svr.config("ip"), Rpt_svr.config("port"), \
            acct2 )
        self.hclog.debug("XML command to be send = {0}".format(response) )
        
        return response
    
     
    
    def server_cmd( self ):
        # check if there is a command to be sent
        
        CLIMAX_CMD_BODY= """
<polling>
    <mac value="{}" />
    <rptipid value="{}" />
    <commands> """
        
        CLIMAX_TAIL_BODY = """
    </commands>
</polling>"""
            
        queue=cmd_queue(self.db_cur)      
        queue_content = queue.get(self.GW_ID)
        
        if queue_content is None:
            return None
        
        else:
            cmd = CLIMAX_CMD_HDR + CLIMAX_CMD_BODY.format(self.MAC, self.rptip_ID)
            cmd = cmd + queue_content + CLIMAX_TAIL_BODY
        
        return cmd
        
        
    
class cmd_queue():
    '''
    Management of the command queue to be sent to the CLimax GW
    '''
    def __init__(self,db_cur):
        '''
        Constructor
        '''
       
        self.db = db_cur
        self.table ="alarm_commands"
        self.hclog=logging.getLogger(__name__)
   
    
    def add ( self, gw_id, cmd_xml, cmd_id ):
        ''' add a command to the queue
        '''    
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        req="INSERT INTO {} (cmdID,action,sent,result, submissiontime, gwID_id) VALUES (%s,%s,%s,%s,%s,%s);".format(self.table)
        value= ( cmd_id, cmd_xml, "N", "N", now, gw_id)
        self.db.executerReq(req, value)
        self.db.commit() 
    
    def ack ( self, gw_id, cmd_id ):
        ''' acknowledge a command has been processed by the GW
        '''
        req="UPDATE {} SET result = %s WHERE gwID_id = %s AND cmdID = %s;".format(self.table)
        value= ( "Y", gw_id, cmd_id )
        self.db.executerReq(req, value)
        self.db.commit()     
        
    def get( self,  gw_id ):
        ''' return the commands available for that GW
        '''
        req="SELECT action, cmdID FROM {} WHERE gwID_id = %s AND sent = %s;".format(self.table)
        value= ( gw_id, "N")
        if self.db.executerReq(req, value):
            action_list=""
            cmd_id_list=[]
            cnt=4

            rows = self.db.resultatReq() # returns a tuple
            if len( rows ) > 0 :
                for row in rows:
                
                    if cnt > 0: # process max 4 commands at the time
                        cnt=cnt-1
                        action_list=action_list+str(row[0])+"\n"
                        cmd_id_list.append(row[1])
                        row = self.db.resultatReqOneRec()                 
                    
                for cmd_id in cmd_id_list:                            
                    # update sent flag to indicate request has been sent to GW
                    req="UPDATE {} SET sent = %s WHERE gwID_id = %s AND cmdID = %s;".format(self.table)
                    value= ( "Y", gw_id, cmd_id )
                    self.db.executerReq(req, value)
                
                self.db.commit()                 

                return action_list
            
            else:
                return None
        
        return None
    

    
        ###### Main Program #########
def main(argv):
    
    oldcmd=1    # status of the GW
    
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

    # DB object creation
    db = DB_mngt(HcDB.config())
    if db.echec:
        sys.exit()
    
    #__init__(self,db_cur, MAC, user_ID, GW_ID, rptip_ID):
    cmd = cmdTo_climax(db, "00:1D:94:03:0F:16", "usr1", "1","0730")
    queue=cmd_queue(db)    
    
    while 1:
        print("\nCommand to test:\n"\
              "1) Set Polling\n"\
              "2) Set Reporting\n"\
              "3) Set Config All\n"\
              "4) Add command (setMode, getUsers, getSensors) to queue\n"\
              "5) Ack command ok\n"\
              "6) Get command list\n"\
              "7) Arm/Unarm GW command\n"\
              
              

              "10) Terminate ?                         Votre choix :" , end=' ')
        try:
            ch = int(input())
        except:
            print("Wrong command entered")
        else:
            
            print()
            if ch ==1:
                # blabla:
                print("Set Polling\n{}".format(cmd.setPolling("0730" )))
             
            elif ch ==2:
                print("Set Reporting\n{}".format(cmd.setReporting( "0730", "99")))
    
            elif ch ==3:
                print("Set Config\n{}".format(cmd.configAll("0730")))
                
            elif ch ==4:         
                     
                cmd.setMode( str(randrange(1000)), str(randrange(1,3)))
                cmd.getUsers( str(randrange(1000)))
                cmd.getSensors( str(randrange(1000)))
    
                print("Pls check result in mySQL")
                
            elif ch ==5:
                queue.ack ( "1", "99" )
                print("Pls check result in mySQL")
                
            elif ch ==6:
                list = cmd.server_cmd( )
                print("Cmd list\n{}".format(list))
                
            elif ch ==7:
                # = disarm
                if oldcmd==3:
                    print("Unarm GW")
                    cmd.setMode( str(randrange(1000)), "1")
                    oldcmd=1
                else:
                    print("Arm GW")
                    cmd.setMode( str(randrange(1000)), "3")
                    oldcmd=3
                    
                
            else:
                db.commit()
                db.close()
                break
    print("End")

if __name__ == "__main__":
    main(sys.argv)