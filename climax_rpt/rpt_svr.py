import socket
import time
import sys
import re

from socket import error as SocketError
import errno
import configparser

from GW_DB.Dj_Server_DB import DB_mngt, DB_gw



# [0730#74 181751000032CA2]

EventCode={ '100':"Medical",
            '101':"Personal Emergency",
            '110':"Fire",
            '111':"Smoke",
            '120':"Panic",
            '121':"Duress",
            '130':"Buglar",
            '131':"Perimeter",
            '132':"Interior",
            '137':"Tamper Burglar",
            '139':"Verification/alarm confirmation",
            '147':"Sensor supervision failure",
            '154':"Water leakage",
            '162':"CO detector",
            '301':"AC failure",
            '302':"Low Battery",
            '344':"Interference",
            '354':"Net device miss",
            '400':"by remote controller",
            '401':"by WEB panel",
            '406':"Cancel",
            '407':"by remote keypad",
            '602':"Periodic test report",
            '611':"Technical alarm",
            '641':"Mobility",
            '655':"Test reporting",
            '704':"Entry zone",
            '750':"Mobility DC",
            '751':"Mobility IR",
            '752':"Siren sound On/Off",}

ArmingRequest={ '00':"General",
                '01':"Home arm",
                '02':"Force arm",
                '03':"Force home arm",}
                
                
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

        alarmMsg += ArmingRequest[GG]
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
            alarmMsg += EventCode[evt]
            alarmMsg += "User "
            alarmMsg += sensor
            
        # arm via WEB
        elif evt =='401' and (sensor == '14' or sensor == '15'):
            alarmMsg += EventCode[evt]

        # arm via Keypad
        elif evt == '407':
            alarmMsg += EventCode[evt]
            alarmMsg += "User "
            alarmMsg += sensor

        
        else:
            alarmMsg += EventCode[evt]
            alarmMsg += " Sensor "
            alarmMsg += sensor
            
            
    except:
        print("Error ContactID: {}".format(contactID), end=' ')
    else:
#        print("Event= {}".format(alarmMsg), end='')
        print("Event= {}".format(alarmMsg), end=' ') 
    
    


def Main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    config = configparser.ConfigParser()
    config.read("config.ini")
    server_port=config.get('server', 'port')
    server_ip=config.get('server', 'ip')
    server_address = (server_ip, int(server_port))
    
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
    
    db_cur= DB_mngt("config.ini") 

    if db_cur.echec:
        print("Cannot open DB")
        sys.exit()

    gw=DB_gw(db_cur)


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
                    print("Socket errorI/O error({0}): {1}".format(errno,strerror))

                else:
                    
                    if data:
                        
                        data = data.decode()
                        now = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        if Contact_ID_filter.match(data):
                            connection.sendall( b'\x06' )       # respond only if Contact ID is correct
                            
                            print ("Received correct Contact ID: {} {} ".format(now, data), end=' ')
                            
                            try:                         
#                                data = data.decode()
                                
                                translate(data)
        #                        [0730#74 181751000032CA2]   
                                rptipid = data[1:5]
                                tmp = data[6:].split(' ')
                                acct2 = tmp[0]
                                
                                gw_id = gw.search_gw_from_acct( rptipid, acct2 )
                                if gw_id == []:    
                                    print( " No Gw found with acct2= {}".format(acct2))
                                else:
                                    print( " on Gw_id {}".format(gw_id[0][0]))
        #                            now = time.strftime("%Y-%m-%d %H:%M:%S")
             
                                    req="INSERT INTO {} (event, eventtime, gwID_id) VALUES ( %s, %s, %s )".format("alarm_events")
                                    value= (data, now, gw_id[0][0],)
                                    db_cur.executerReq(req, value)
                                    db_cur.commit() 
                            except:
                                print("Error translating ContactID or writing DB")

                        else:
                            print ("Received wrong Contact ID: {} {} ".format(now, data), end=' ')

                                
                    else:
#                        print ('no more data from {}'.format(client_address))
                        break   
                                    
               
                    
    
        finally:
            # Clean up the connection
            connection.close()


    db_cur.close()       
            
            
            
            
            
        
if __name__ == '__main__':
    Main()