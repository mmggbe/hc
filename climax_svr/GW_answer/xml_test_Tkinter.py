#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter.messagebox import *
import sys
import time

from lxml import etree


CLIMAX_CMD_HDR  = r'<?xml version="1.0" encoding="ISO-8859-1"?>'

"""
CLIMAX_CMD_BDY = r'<polling>' \
    '<mac value="00:1D:94:03:0F:16"/>' \
    '<rptipid value=""/>' \
    '<date value="28/07/2016 14:27:11" />' \
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

CLIMAX_CMD_BDY = r"""<polling>
  <mac value="00:1D:94:03:0A:5A"/><rptipid value=""/>
  <ver value="CTC-1815 1.0.34 I1815W36A "/>
  <sensor_mod value="0"/>
  <commands>
<referer value="panel/update"/>
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
  <rf value="49"/>
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
</polling>"""

def tk_parse(mac, inwin, outwind):
#    try: 
        climax_xml= etree.fromstring((CLIMAX_CMD_HDR+CLIMAX_CMD_BDY).encode('iso-8859-1'))
        result = etree.tostring(climax_xml, pretty_print=True, method="html")
        print (result)

#        root=climax_xml.getroot()
#        print("Root attri {} {}".format(root[0],root[1]))

# Class ElementTree
        walkAll = climax_xml.getiterator()
 
        for elt in walkAll:
            print( "{} -{}".format(elt.tag, elt.attrib ) )  

        print("0...")
        elt=climax_xml.find("mac")
        if elt != None:
                print("{} -{}".format(elt.tag, elt.get ("value", "0")))  
     
        print("1...")
        elt=climax_xml.find("commands")
        if elt != None:
            tst=elt.find("command")
            for cmd in tst:
                print("{} -{} -{}".format(cmd.tag, cmd.get ("id", "0"), cmd.get ("action", "0")))  
     
            for content in elt:
                print("{} -{} -{}".format(content.tag, content.get ("id", "0"), content.get ("action", "0")))  
                for subcontent in content:
                    print("   {}= {}".format(subcontent.tag, subcontent.get ("value", "0")) ) 
                    keys=subcontent.keys()
                    vals=subcontent.values()
                    for subsubcontent in subcontent:
                        print("      {}= {}".format(subsubcontent.tag, subsubcontent.get ("value", "0")) ) 
                        for subsubsubcontent in subsubcontent:
                            print("      {}= {}".format(subsubsubcontent.tag, subsubsubcontent.get ("value", "0")) ) 

#class Element 
        print("2...")          
        elt = climax_xml.getchildren() 
        for content in elt:
                print("{} -{}".format(content.tag, content.get ("value", "0")))  
#class Element 
        print("3...") 
        elt=climax_xml.find("mac")
        print("{} -{}".format(elt.tag, elt.get ("value", "0")))  
        
        elt.set("value", "00:1D:94:AA:AA:AA")
        
        result = etree.tostring(climax_xml, pretty_print=True, method="html")
        print (result)


# <date value="28/07/2016 14:27:11" />

        now = time.strftime("%d/%m/%Y %H:%M:%S")
        print("{}".format(now))
        
        outwind.delete("1.0",'end-1c')
        outwind.insert(INSERT, result)
#    except:
#        showerror("Error", "Invalid xml cmd")



    
def main(argv):
    
    fenetre = Tk()
    
    lbl1= Label(fenetre, text="Xml parsing").grid(row=1, padx=5, pady=5, sticky=W)
    
    # entrée
    
    value = StringVar()
    value.set("Hello!")
    entree = Entry(fenetre, width=15, textvariable=value)
    entree.grid(row=2, column=1, padx=5, pady=5)


    Label(fenetre, text="Input").grid(row=3, column=1, padx=5, pady=5, sticky=W)
    Label(fenetre, text="Output").grid(row=4, column=1, padx=5, pady=5, sticky=W)
    
    
    e1 = Text(fenetre, height=15)
    e2 = Text(fenetre, height=20)
    
    e1.grid(row=3, column=2, padx=5, pady=5)
    e2.grid(row=4, column=2, padx=5, pady=5)

#    enc_cmd = StringVar()
#    enc_cmd.set(ENC_CLIMAX_COMMAND)
    e1.insert(INSERT, CLIMAX_CMD_HDR+CLIMAX_CMD_BDY)
    
    

    b2 = Button(fenetre,text="Parse", command= lambda: tk_parse(entree, e1, e2))
#    b1 = Button(fenetre,text="Encrypter")
#    b2 = Button(fenetre,text="Decrypter")
    

    b2.grid(row=5, column=2, padx=5, pady=5, sticky=E)
    
    fenetre.mainloop()


if __name__ == '__main__':
    main(sys.argv)
