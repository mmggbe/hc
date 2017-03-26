#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on 2 fev 2017

@author: marc
'''
import time

from .models import gateways, commands

class Glob:
    current_GW = None               # current gateway record 

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


    def __init__(self):
        '''
        Constructor
        '''
        
        self.gtw=Glob.current_GW
    
    def getUsers(self):
        
        CLIMAX_CMD_BODY= """
        <command id= "{}" action="getUsers"/>""" 
        
        cmd_id= self.inc_last_cmd_id()
        self.add_queue ( CLIMAX_CMD_BODY.format(cmd_id), cmd_id )    
        
    def setUsers(self, index_usr, code, name, latch):
        
        CLIMAX_CMD_BODY= """
        <command id="{}" action="setUser" >
            <index value="{}"/>
            <code value="{}"/>
            <name value="{}"/>
            <latch value="{}"/>
        </command >"""
        
        cmd_id= self.inc_last_cmd_id()
        self.add_queue ( CLIMAX_CMD_BODY.format(cmd_id, index_usr, code, name, latch), cmd_id )
    
    def getSensors(self):
        
        CLIMAX_CMD_BODY= """
        <command id= "{}" action="getSensors"/>""" 
        cmd_id = self.inc_last_cmd_id()
        self.add_queue (CLIMAX_CMD_BODY.format(cmd_id), cmd_id )
        
    def delSensors(self, sensor):
        
        CLIMAX_CMD_BODY= """
        <command id="{}" action="delSensor" >
            <zone value="{}"/>
        </command >"""
        cmd_id = self.inc_last_cmd_id()
        self.add_queue (CLIMAX_CMD_BODY.format(cmd_id, sensor), cmd_id )
        
        
    def editSensors(self, zone, name, attr, latch ):
        
        CLIMAX_CMD_BODY= """
        <command id="{}" action="setSensor" >
            <zone value="{}"/>
            <name value="{}"/>
            <attr value="{}" />
            <latch value="{}" />
        </command >"""

        
        cmd_id = self.inc_last_cmd_id()
        self.add_queue (CLIMAX_CMD_BODY.format(cmd_id, zone, name, attr, latch), cmd_id )
        
    def setMode(self, mode):

        CLIMAX_CMD_BODY= """
		<command id= "{0}" action="setMode">
			<mode value = "{1}"/>
		</command>"""

        cmd_id = self.inc_last_cmd_id()
        self.add_queue( CLIMAX_CMD_BODY.format(cmd_id,mode), cmd_id )   
      
        self.gtw.mode = mode
        self.gtw.save(update_fields=['mode'])



    def inc_last_cmd_id(self):
        ''' increase the command_id each time a command is sent.
        The command_id can be modified by the polling server 
        '''
#        gtw=gateways.objects.get(id=self.gtw.id)
     

        self.gtw.last_cmd_id= self.gtw.last_cmd_id+1
        self.gtw.save()
        
        return(self.gtw.last_cmd_id)
    
    def add_queue ( self, cmd_xml, cmd_id ):
        ''' add a command to the queue
        '''    
        now = time.strftime("%Y-%m-%d %H:%M:%S")
#        req="INSERT INTO {} (cmdID,action,sent,result, submissiontime, gwID_id) VALUES (%s,%s,%s,%s,%s,%s);".format(self.table)
#        value= ( cmd_id, cmd_xml, "N", "N", now, gw_id)
#        self.db.executerReq(req, value)
#        self.db.commit() 
        cmd= commands(    
            id=None,
            referer = "",
            cmdID = cmd_id,
            action = cmd_xml,
            result = "N",
            sent = "N",              
            submissiontime = now,
            gwID = self.gtw
        ) 

        cmd.save()

    
 