import time


# [0730#74 181751000032CA2]

EventCode={  '100':"Medical",
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

ArmingRequest={  '00':"General",
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
        
        if Q==  '1':
            if sensor ==  '14' or sensor ==  '15' :
                alarmMsg += "Disarm: "
            else:
                alarmMsg += "New event: "
                
        elif Q ==  '3':
            if sensor ==  '14' or sensor ==  '15' :
                alarmMsg += "Armed: "
            else:
                alarmMsg += "Restore: "
        else:
            alarmMsg += ""
        
        
        # arm vie RC
        if evt ==  '400':
            alarmMsg += EventCode[evt]
            alarmMsg += "User "
            alarmMsg += sensor
            
        # arm via WEB
        elif evt == '401' and (sensor ==  '14' or sensor ==  '15'):
            alarmMsg += EventCode[evt]

        # arm via Keypad
        elif evt ==  '407':
            alarmMsg += EventCode[evt]
            alarmMsg += "User "
            alarmMsg += sensor

        
        else:
            alarmMsg += EventCode[evt]
            alarmMsg += " Sensor "
            alarmMsg += sensor
            
            
    except:
        return("Error ContactID {}".format(contactID))
    else:
        return( alarmMsg ) 
    