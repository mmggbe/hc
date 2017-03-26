import socket
import time
import sys
#import curses.ascii
from socket import error as SocketError
import errno

from GW_DB.Dj_Server_DB import DB_mngt, DB_gw



# [0730#74 181751000032CA2]

EventCode={ b'100':"Medical",
            b'101':"Personal Emergency",
            b'110':"Fire",
            b'111':"Smoke",
            b'120':"Panic",
            b'121':"Duress",
            b'130':"Buglar",
            b'131':"Perimeter",
            b'132':"Interior",
            b'137':"Tamper Burglar",
            b'139':"Verification/alarm confirmation",
            b'147':"Sensor supervision failure",
            b'154':"Water leakage",
            b'162':"CO detector",
            b'301':"AC failure",
            b'302':"Low Battery",
            b'344':"Interference",
            b'354':"Net device miss",
            b'400':"by remote controller",
            b'401':"by WEB panel",
            b'406':"Cancel",
            b'407':"by remote keypad",
            b'602':"Periodic test report",
            b'611':"Technical alarm",
            b'641':"Mobility",
            b'655':"Test reporting",
            b'704':"Entry zone",
            b'750':"Mobility DC",
            b'751':"Mobility IR",
            b'752':"Siren sound On/Off",}

ArmingRequest={ b'00':"General",
                b'01':"Home arm",
                b'02':"Force arm",
                b'03':"Force home arm",}
                
                
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
        
        if Q== b'1':
            if sensor == b'14' or sensor == b'15' :
                alarmMsg += "Disarm: "
            else:
                alarmMsg += "New event: "
                
        elif Q == b'3':
            if sensor == b'14' or sensor == b'15' :
                alarmMsg += "Armed: "
            else:
                alarmMsg += "Restore: "
        else:
            alarmMsg += ""
        
        
        # arm vie RC
        if evt == b'400':
            alarmMsg += EventCode[evt]
            alarmMsg += "User "
            alarmMsg += sensor.decode()
            
        # arm via WEB
        elif evt ==b'401' and (sensor == b'14' or sensor == b'15'):
            alarmMsg += EventCode[evt]

        # arm via Keypad
        elif evt == b'407':
            alarmMsg += EventCode[evt]
            alarmMsg += "User "
            alarmMsg += sensor.decode()

        
        else:
            alarmMsg += EventCode[evt]
            alarmMsg += " Sensor "
            alarmMsg += sensor.decode()
            
            
    except:
        print("Error ContactID")
    else:
        print("Event= {}".format(alarmMsg), end='') 
    
    


def Main():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('192.168.157.4', 52016)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
    
    db_cur= DB_mngt("config.ini") 

    if db_cur.echec:
        print("Cannot open DB")
        sys.exit()

    gw=DB_gw(db_cur)

    
    while True:
        # Wait for a connection
#        print ('waiting for a connection')
        
        try:
            connection, client_address = sock.accept()
 #          print ('connection from {}'.format(client_address))
    
        # Receive the data in small chunks and retransmit it
            while True:
         
                try: 
                    data = connection.recv(32)
                    if data:
                        connection.sendall( b'\x06' )
                        print ("Received: {} ".format(data))
                        translate(data)
#                        [0730#74 181751000032CA2]

                        rptipid = data[1:5].decode()
                        tmp = data[6:].split(b' ')
                        acct2 = tmp[0].decode()
                        
                        gw_id = gw.search_gw_from_acct( rptipid, acct2 )
                        if gw_id == []:    
                            print( " No Gw found with acct2= {}".format(acct2))
                        else:
                            print( " on Gw_id {}".format(gw_id[0][0]))
                            now = time.strftime("%Y-%m-%d %H:%M:%S")
     
                            req="INSERT INTO {} (event, eventtime, gwID_id) VALUES ( %s, %s, %s )".format("alarm_events")
                            value= (data.decode(), now, gw_id[0][0],)
                            db_cur.executerReq(req, value)
                            db_cur.commit() 

                    else:
#                        print ('no more data from {}'.format(client_address))
                        break   
                                    
                except SocketError as e:
                    errno, strerror = e.args
                    print("Socket errorI/O error({0}): {1}".format(errno,strerror))
                    
    
        finally:
            # Clean up the connection
            connection.close()


    db_cur.close()       
            
            
            
            
            
        
if __name__ == '__main__':
    Main()