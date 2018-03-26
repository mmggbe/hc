from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.http import JsonResponse
import time
import subprocess
import os
import random, string
from HCsettings import HcFTP

from .forms import *

from camera.models import camera, action_list
from history.models import events

from django.contrib.admin.views.decorators import staff_member_required

@login_required(login_url="/")
def cameraList(request):
    username = request.user.get_username()
    cameras = camera.objects.filter(user__username=username)
    
    return render(request,'cameraList.html', locals())

@staff_member_required
def cameraListAdmin(request):
    username = request.user.get_username()
    cameras = camera.objects.all()
    
    return render(request,'cameraListAdmin.html', locals())


def cameraAdd( request ):

    if request.method == 'POST':
        camera_form = cameraEditForm(request.user, request.POST)
        if camera_form.is_valid():
            cam = camera_form.save(commit=False)
            cam.user_id = request.user.id
            cam.securityStatus = '1'            
            cam.save()
            
            #Send the config to the camera
            camID = cam.id
            actionCmd = 'GET /adm/set_group.cgi?group=FTP&address=horus.ovh&username=rc8020&password=1987cameraLDC HTTP/1.1\r\n'
            n=action_list.objects.create(action=actionCmd, camera_id=camID)
            n.save()
            actionCmd = 'GET /adm/set_group.cgi?group=FTP2&address=horus.ovh&username=rc8020&password=1987cameraLDC HTTP/1.1\r\n'
            n=action_list.objects.create(action=actionCmd, camera_id=camID)
            n.save()
      
            return redirect('cameraSettings')

    else:
        camera_form = cameraEditForm(request.user)

    return render( request, 'cameraEdit.html', {'form': camera_form})


@login_required(login_url="/")    
def cameraEdit (request, pk):
    post = get_object_or_404(camera, pk=pk)
    if request.method == 'POST':
        camera_form = cameraEditForm(request.user, request.POST, instance=post)
        if camera_form.is_valid():
            post = camera_form.save(commit=False)
            post.save()
            return redirect('cameraSettings')
    else:
        camera_form = cameraEditForm( request.user, instance = post )
    return render( request, 'cameraEdit.html', {'form': camera_form})


@login_required(login_url="/")
def cameraSettings(request):
    username = request.user.get_username()
    cameras = camera.objects.filter(user__username=username)
    
    return render(request,'cameraSettings.html', locals())
   
@login_required(login_url='/')
def cameraDelete(request, pk):
    VIDEO_STORAGE = HcFTP.config("VIDEO_STORAGE")
    
    queryset=events.objects.filter(cameraID_id=pk).filter(event_code = '800')
    for event in queryset:
        try:
            os.remove(VIDEO_STORAGE + event.video_file + ".mp4") 
        except:
            print ("Cannot delete the file")
        try:
            os.remove(VIDEO_STORAGE + file + ".jpg")
        except:
            print ("Cannot delete the file")
        event.delete()
    events.objects.filter(cameraID_id=pk).delete()
    action_list.objects.filter(camera_id=pk).delete()
    username = request.user.get_username()
    camera.objects.filter(pk=pk).filter(user__username=username).delete()
    return redirect('/camera/cameraSettings/')
    
@login_required(login_url='/')    
def cameraTest(request, pk): 
    c = {}
    c.update(csrf(request))
    c['cam_id'] = pk
    return render(request,'cameraTest.html', c)

@login_required(login_url='/')   
def saveAction(request):
    n=action_list.objects.create(action=request.POST['action'], camera_id=request.POST['camera'])
    n.save()
    return redirect('/camera/')

@login_required(login_url='/')   
def configureFTP(request):
    actionCmd = 'GET /adm/set_group.cgi?group=FTP&address=horus.ovh&username=rc8020&password=1987cameraLDC HTTP/1.1\r\n'
    n=action_list.objects.create(action=actionCmd, camera_id=request.POST['camera'])
    n.save()
    actionCmd = 'GET /adm/set_group.cgi?group=FTP2&address=horus.ovh&username=rc8020&password=1987cameraLDC HTTP/1.1\r\n'
    n=action_list.objects.create(action=actionCmd, camera_id=request.POST['camera'])
    n.save()
    return redirect('/camera/admin')

@login_required(login_url="/")
def cameraArming(request):
    cameraId=request.GET.get('cameraId', '')
    securityStatus=request.GET.get('status', '')
    
    #polulate Action list list table
    cmd1='GET /adm/set_group.cgi?group=SYSTEM&pir_mode=' + securityStatus +' HTTP/1.1\r\n'
    cmd2='GET /adm/set_group.cgi?group=EVENT&event_trigger=1&event_interval=0&event_pir=ftpu:1&event_attach=avi,1,10,20 HTTP/1.1\r\n'
    n=action_list.objects.create(action=cmd1, camera_id=cameraId)
    n.save()
    n=action_list.objects.create(action=cmd2, camera_id=cameraId)
    n.save()
    
    #change the camera security status 
    camera.objects.filter(id=cameraId).update(securityStatus=securityStatus)
    
    #Log the change in th history table
    if securityStatus == '1':
        descriptionTxt='Camera has been armed'
        code='801'
    else:
        descriptionTxt='Camera has been unarmed'
        code='802'
    
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    n=events.objects.create(timestamp= now, type='CA', userWEB=request.user, event_code=code, event_description=descriptionTxt, cameraID_id=int(cameraId ))
    n.save()
    
    
    data = {
        'attribute' : 'securiyStatus= ok'
    }
    return JsonResponse(data)

def video (request, filename):
    c = {}
    c['username'] = request.user.get_username()
    c['filename'] = filename
    return render(request,"videoPlayer.html", c)

@login_required(login_url='/')    
def cameraRT(request, pk):          #Real Time view
    c = {}
    c.update(csrf(request))
    c['cam_id'] = pk
    letters = string.ascii_lowercase
    randURL= ''.join(random.choice(letters) for i in range(10))
    #randURL= 'test'

    #r=subprocess.run("nohup /usr/local/bin/ffmpeg -i rtp://192.168.0.2:9418 -c:v libx264 -f flv rtmp://horus:aiT7aiYu@intake.live.streamcloud.be/horus/"+ randURL +" & 1>$HOME/out 2>$HOME/error", shell=True)
    
    r=subprocess.Popen("/usr/bin/nohup /usr/local/bin/ffmpeg -i rtp://192.168.0.2:9418 -c:v libx264 -f flv rtmp://horus:aiT7aiYu@intake.live.streamcloud.be/horus/"+ randURL+" & 1>$HOME/out 2>$HOME/error", shell=True, preexec_fn=os.setsid)
    
    cmd1='GET /adm/rtsp_push.cgi?format=1&addr=horus.ovh&vport=9418&aport=20182&action=0 HTTP/1.1\r\n'
    n=action_list.objects.create(action=cmd1, camera_id=pk)
    n.save()
    c['RT_URL']= 'http://live.streamcloud.be/horus/'+ randURL +'/playlist.m3u8'   
    c['pid']= r.pid
    
    return render(request,'videoPlayerRT.html', c)
    
@login_required(login_url='/')
def cameraRTStop(request, pk):
    cmd1='GET /adm/rtsp_push.cgi?format=1&addr=horus.ovh&vport=9418&aport=20182&action=1 HTTP/1.1\r\n'
    n=action_list.objects.create(action=cmd1, camera_id=pk)
    n.save()
    
    username = request.user.get_username()
    cameras = camera.objects.filter(user__username=username)
    
    return render(request,'cameraList.html', locals())

@login_required(login_url='/')    
def SnapShot(request):
    cameraId=request.GET.get('cameraId', '')
    username = request.user.get_username()
    data = {}
    try:
        cameraObj = camera.objects.filter(user__username=username).get(pk=cameraId)
    except camera.DoesNotExist:
        data = {'attribute' : 'camera does not exist'}
    else:
        if cameraObj.status == 1:
            cmd='GET /adm/retrieve_start.cgi?pre_second=10&post_second=0 HTTP/1.1\r\n'
            n=action_list.objects.create(action=cmd, camera_id=cameraId)
            n.save()
            data = {'attribute' : 'ok'}
        else:
            data = {'attribute' : 'camera is off'}
        
    return JsonResponse(data)
