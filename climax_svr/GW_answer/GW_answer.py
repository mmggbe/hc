#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import time
import logging

from lxml import etree
from GW_DB.Dj_Server_DB import DB_mngt, DB_gw
from GW_CMD.GW_cmd import cmd_queue


CLIMAX_CMD_HDR  = r'<?xml version="1.0" encoding="ISO-8859-1"?>'

"""
CLIMAX_CMD_BDY = r'<polling>' \
    '<mac value="00:1D:94:03:0F:16"/>' \
    '<rptipid value=""/>' \
    '< value="28/07/2016 14:27:11" />' \
    '</polling>'

"""
"""
CLIMAX_CMD_BDY = r'<polling>' \
    '<mac value="00:1D:94:03:0A:5A" />' \
    '<rptipid value="" />' \
    '<commands>' \
    '<command id="101" action="getUsers" />' \
    '<command id="102" action="getSpecParams" />' \
    '<command id="104" action="setPolling">' \
    '<url1 value="polln://v03.hub.belgacomhome.be/service.aspx" />' \
    '<url2 value="pollg://v03.hub.belgacomhome.be/service.aspx" />' \
    '<interval value="20" />' \
    '<errnotify value="20" />' \
    '</command>' \
    '<command id="105" action="setRpt">' \
    '<url1 value="rptn://0701@bcom.1815.rpt.intamac.com:52016" />' \
    '<url2 value="rptg://0701@bcom.1815.rpt.intamac.com:52016" />' \
    '<acct2 value="330260" />' \
    '</command>'\
    '<command id="106" action="setPanel">' \
    '<doorchime value="0" />' \
    '<offtimer value="1" />' \
    '</command>' \
    '<command id="107" action="setUpload">' \
    '<url1 value="ftp://:@bcom.ftp.intamac.com" />' \
    '<prefix value="001D94030A5A" />'\
    '</command>' \
    '</commands>' \
    '</polling>'
"""
"""
CLIMAX_CMD_BDY = r'<polling>
  <mac value="00:1D:94:03:0A:5A"/><rptipid value=""/>
  <ver value="CTC-1815 1.0.34 I1815W36A "/>
  <sensor_mod value="0"/>
  <commands>
<referer value="panel/up"/>
<command id="1" action="getSensors">
  <result>1</result>
  <message>OK</message>
  <xmldata>
<size value="7"/>
<zone>
  <no value="1"/>
  <rf value="49"/>
  <address value="6E0401"/>
  <type value="1"/>
  <attr value="4"/>
  <latch value="0"/>
  <name value=""/>
  <status1 value="80"/>
  <status2 value="00"/>
  <rssi value="00"/>
</zone>
<zone>
  <no value="2"/>
  <rf value="49"/>
  <address value="6F0201"/>
  <type value="1"/>
  <attr value="4"/>
  <latch value="0"/>
  <name value=""/>
  <status1 value="80"/>
  <status2 value="00"/>
  <rssi value="00"/>
</zone>
<zone>
  <no value="3"/>
  <rf value="49"/>
  <address value="CA0A02"/>
  <type value="0"/>
  <attr value="13"/>
  <latch value="1"/>
  <name value="Keyfob"/>
  <status1 value="00"/>
  <status2 value="00"/>
  <rssi value="00"/>
</zone>
<zone>
  <no value="4"/>
  <rf value="49"/>
  <address value="3C1F02"/>
  <type value="0"/>
  <attr value="13"/>
  <latch value="1"/>
  <name value="Keyfob"/>
  <status1 value="00"/>
  <status2 value="00"/>
  <rssi value="00"/>
</zone>
<zone>
  <no value="5"/>
  <rf value="49"/>
  <address value="183D00"/>
  <type value="4"/>
  <attr value="0"/>
  <latch value="0"/>
  <name value=""/>
  <status1 value="80"/>
  <status2 value="00"/>
  <rssi value="00"/>
</zone>
<zone>
  <no value="6"/>
  <rf value="49"/>
  <address value="001D94"/>
  <type value="29"/>
  <attr value="0"/>
  <latch value="0"/>
  <name value=""/>
  <status1 value="80"/>
  <status2 value="00"/>
  <rssi value="00"/>
  <status-switch value="0"/>
  <status-power value="0.0"/>
  <status-energy value="0.0"/>
</zone>
<zone>
  <no value="7"/>
  <rf value="33"/>
  <address value="504F01"/>
  <type value="3"/>
  <attr value="1"/>
  <latch value="0"/>
  <name value=""/>
  <status1 value="80"/>
  <status2 value="00"/>
  <rssi value="00"/>
</zone>
  </xmldata>
</command>
  </commands>
</polling>
"""

CLIMAX_CMD_BDY = r"""<polling>
  <mac value="00:1D:94:03:0F:16"/><rptipid value="0730"/>
  <ver value="CTC-1815 1.0.38 I1815W39A "/>
  <sensor_mod value="0"/>
  <commands>
<referer value="panel/run"/>
<command id="98" action="setMode">
   <result>1</result>
   <message>OK</message>
</command>
<command id="97" action="getUsers">
  <result>1</result>
  <message>OK</message>
  <xmldata>
<user>
  <index value="1"/>
  <code value="1234"/>
  <name value=""/>
  <latch value="enabled"/>
</user>
<user>
  <index value="2"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="3"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="4"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="5"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="6"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="7"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="8"/>
  <code value=""/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="9"/>
  <code value="798213"/>
  <name value=""/>
  <latch value="disabled"/>
</user>
<user>
  <index value="10"/>
  <code value="1111"/>
  <name value=""/>
  <latch value="disabled"/>
</user>
  </xmldata>
</command>
  </commands>
</polling>"""



class answerFrom_climax():
    '''
    Command received from the CLimax GW
    '''


    def __init__(self, db_cur, MAC, user_ID, GW_ID):
        '''
        Constructor
        '''
        
        self.db_cur = db_cur 
        self.MAC = MAC
        self.user_ID = user_ID
        self.GW_ID = GW_ID
        
    def getUsers(self, data):   
        
        value= ( self.GW_ID,)
        req ="DELETE FROM %s WHERE %s = %%s" % ("alarm_users", "gwID_id")
        logging.debug("req={}\nvalues={}".format(req,value ))
        self.db_cur.executerReq(req, value)
        self.db_cur.commit()  

# store all sensors parameters to DB       
        for cmdParam in data:
            logging.debug("{} -{}".format(cmdParam.tag, cmdParam.text))
            if cmdParam.tag == "xmldata":

                users=cmdParam.findall("user")
                for user in users: 
                
                    fields ="(gwID_id,"           # chain that will contain  the field names dynamically built
                    values =[self.GW_ID,]            # list of corresponding values
                    balises = "(%s,"

                    logging.debug("{}".format(user.tag) )       
                    for params in user:
                        logging.debug("   {}= {}".format(params.tag, params.get ("value", "0")) )
                        field = params.tag.replace("-","_")   # mysql : field names with "-" are not allowed
                        
                        if field == "index":
                            field = field +"_usr"           # "index" is a reserved keyword for mysql 
                                 
                        fields = fields + field + ","     
                        balises = balises + "%s,"
                        
                        value = params.get("value", "0")
                        
                        if field == "latch":                    # when reading from GW, latch = enabled/disabled 
                            if value == "disabled":
                                value = "0"                     # when writing to gw, it should be "0" or "1"
                            else:
                                value= "1"
                                
                        values.append(value)          
                    
                    balises = balises[:-1] + ")" 
                    fields = fields[:-1] + ")" 
                    req ="INSERT INTO %s %s VALUES %s" % ("alarm_users", fields, balises)
                    logging.debug( "req={}\nvalues={}".format(req,values))
                    self.db_cur.executerReq(req, values)
                    self.db_cur.commit()  
        
    
        
    def getSensors(self, data): 
         
         
# Delete previous sensor configuration in DB 
# DELETE FROM sensors where gwID=23;

        value= ( self.GW_ID,)
        req ="DELETE FROM %s WHERE %s = %%s" % ("alarm_sensors", "gwID_id")
        logging.debug( "req={}\nvalues={}".format(req,value ))
        self.db_cur.executerReq(req, value)
        self.db_cur.commit()  

# store all sensors parameters to DB       
        for cmdParam in data:
            logging.debug("{} -{}".format(cmdParam.tag, cmdParam.text))
            if cmdParam.tag == "xmldata":

                zones=cmdParam.find("size")
                size=int(zones.get ("value", "0"))
                logging.debug("size = {}\n".format(size))
                

                zones=cmdParam.findall("zone")
                for zone in zones: 
                
                    fields ="(gwID_id,"           # chain that will contain  the field names dynamically built
                    values =[self.GW_ID,]            # list of corresponding values
                    balises = "(%s,"

                    logging.debug("{}".format(zone.tag) )       
                    for params in zone:
                        logging.debug("   {}= {}".format(params.tag, params.get ("value", "0")) )                                        
                        fields = fields + params.tag.replace("-","_") + ","     # mysql : field names with "-" are not allowed
                        balises = balises + "%s,"
                        values.append(params.get("value", "0"))          
                    balises = balises[:-1] + ")" 
                    fields = fields[:-1] + ")" 
                    req ="INSERT INTO %s %s VALUES %s" % ("alarm_sensors", fields, balises)
                    logging.debug( "req={}\nvalues={}".format(req,values))
                    self.db_cur.executerReq(req, values)
                    self.db_cur.commit()  
                    
    def getMode(self, data): 
 
        #find mode in xml
        for cmdParam in data:
            logging.debug("{} -{}".format(cmdParam.tag, cmdParam.text))
            if cmdParam.tag == "xmldata":
                elt=cmdParam.find("mode")
                mode=elt.get ("value", "0")
                break
            # store result in DB
        db = DB_gw(self.db_cur)        
        db.upd_polling_gw(self.MAC, mode)

    def parsing(self, commands):
        '''
        parse all commands
        '''
                    
        cmd_list=commands.findall("command")
        
        for cmd in cmd_list:
            
            cmd_name = cmd.get ("action", "0")
            cmd_ID = cmd.get ("id", "0")
            
            logging.debug("{} -{} -{}".format(cmd.tag, cmd_ID, cmd_name))
            
            # each time a answer is received, up the cmd_id in the GW DB
            db = DB_gw(self.db_cur)        
            db.upd_cmd_id_gw(self.GW_ID, cmd_ID)
            
            # indicate in the command queue that the answer has been received
            queue=cmd_queue(self.db_cur)
            queue.ack( self.GW_ID, cmd_ID)
            
            if cmd_name == "getSensors":
                self.getSensors(cmd)
            
            if cmd_name == "getMode":
                self.getMode(cmd)
                
            if cmd_name == "getUsers":
                self.getUsers(cmd)
            
         

def main(argv):
    
    db_cur= DB_mngt("config.ini")
            
    if db_cur.echec:
        sys.exit()
    
    cmd_list=answerFrom_climax(db_cur,"00:1D:94:03:0F:16", "usr001", 23)
    
    climax_xml= etree.fromstring((CLIMAX_CMD_HDR+CLIMAX_CMD_BDY).encode('iso-8859-1'))
    commands_xml=climax_xml.find("commands")
    
    if cmd_list != None:
        cmd_list.parsing(commands_xml)
        
    db_cur.commit()
    db_cur.close()
   
        

                
if __name__ == '__main__':
    main(sys.argv)
