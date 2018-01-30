from .models import sensors
#from .Dj_GW_cmd import Glob

from HCsettings import EventCode

# [0730#74 181751000032CA2]             
                
def translate(contactID, gtw):
    
    alarmMsg=""
    sensor_id=""                       # to be sure it will be processed as a string
    sensor_name = ""

#[0730#74 18_1_751_00_003_2CA2]
#         MT Q EEE GG CCC
    Q = contactID[-14:-13] # Q: Event quialifier 1: new event & disarm 3: restore & arm
    evt= contactID[-13:-10] # EEE: event code
    GG = contactID[-10:-8] # GG: partition number (always 00 for non partitioned panels)
    sensor_id= contactID[-7:-5].lstrip("0") # ZZZ: representing zone number C 1 = 0 (fixed) , C 2 C 3 = Zone number

    #sensor = sensors.objects.filter(gwID = Glob.current_GW.id, no = sensor_id)
    sensor = sensors.objects.filter(gwID__id = gtw.id, no=sensor_id)
    
    if sensor.exists() :      
        sensor_name = sensor[0].name

#    print("Event={}".format(evt))
    try:
        
#        alarmMsg += ArmingRequest[GG]
#        alarmMsg += ": "
        
        if Q ==  '1':
            if sensor_id ==  '14' or sensor_id ==  '15' :
                alarmMsg += "Disarm: "
            else:
                alarmMsg += "New event: "
                
        elif Q ==  '3':
            if sensor_id ==  '14' or sensor_id ==  '15' :
                alarmMsg += "Armed: "
            else:
                alarmMsg += "Restore: "
        else:
            alarmMsg += ""
        
        
        # arm vie RC
        if evt ==  '400':
            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += " User "
            alarmMsg += sensor_name
            
        # arm via WEB
        elif evt == '401' and (sensor ==  '14' or sensor ==  '15'):
            alarmMsg += EventCode.value(evt)[0]

        # arm via Keypad
        elif evt ==  '407':
            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += " User "
            alarmMsg += sensor_name

        
        else:
            alarmMsg += EventCode.value(evt)[0]
            alarmMsg += " Sensor "
            alarmMsg += sensor_name
            
            
    except:
        return("Error ContactID {}".format(contactID))
    else:
        return( alarmMsg ) 
    