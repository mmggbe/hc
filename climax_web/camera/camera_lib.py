#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on 17 April 2018

@author: marc
'''

from camera.models import camera, action_list


class camera_cmd():
    
    def arm_camera_in_List(self, userID):
        
        cameras = camera.objects.filter(user=userID)
        
        for cam in cameras:
            if cam.activateWithAlarm == True:
    
    
                cmd1='GET /adm/set_group.cgi?group=SYSTEM&pir_mode=1 HTTP/1.1\r\n'
                cmd2='GET /adm/set_group.cgi?group=EVENT&event_trigger=1&event_interval=0&event_pir=ftpu:1&event_attach=avi,1,10,20 HTTP/1.1\r\n'
                n=action_list.objects.create(action=cmd1, camera_id=cam.id)
                n.save()
                n=action_list.objects.create(action=cmd2, camera_id=cam.id)
                n.save()
                
                   #change the camera security status 
                camera.objects.filter(id=cam.id).update(securityStatus="1")
 

    def disarm_camera_in_List(self, userID):
        
        cameras = camera.objects.filter(user=userID)
        
        for cam in cameras:
            if cam.activateWithAlarm == True:

                cmd1='GET /adm/set_group.cgi?group=SYSTEM&pir_mode=0 HTTP/1.1\r\n'
                n=action_list.objects.create(action=cmd1, camera_id=cam.id)
                n.save()
                
                    #change the camera security status 
                camera.objects.filter(id=cam.id).update(securityStatus="0")
 