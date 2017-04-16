from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.http import JsonResponse

from camera.models import camera, action_list, file_list

@login_required(login_url="login/")
def index(request):
    username = request.user.get_username()
    cameras = camera.objects.filter(user__username=username)
    
    return render(request,'cameraList.html', locals())

@login_required(login_url="login/")    
def cameraAdd (request):
    c = {}
    c.update(csrf(request))
    return render(request,"cameraAdd.html", c)

@login_required(login_url="login/")
def cameraSettings(request):
    username = request.user.get_username()
    cameras = camera.objects.filter(user__username=username)
    
    return render(request,'cameraSettings.html', locals())

@login_required(login_url="login/")    
def saveCamera (request):
    current_user = request.user
    n=camera.objects.create(CameraMac=request.POST['mac'], description=request.POST['description'],user_id=current_user.id,securityStatus='1')
    n.save()
    return redirect('/camera/cameraSettings/')
    
@login_required(login_url='login/')
def cameraDelete(request, pk):
    username = request.user.get_username()
    camera.objects.filter(pk=pk).filter(user__username=username).delete()
    return redirect('/camera/cameraSettings/')
    
@login_required(login_url='login/')    
def cameraEdit(request, pk): 
    c = {}
    username = request.user.get_username()
    #c['actions'] = action_list.objects.filter(cameraID__CameraMac=cam_mac)
    c['cameras'] = camera.objects.filter(pk=pk).filter(user__username=username)
    c['files'] = file_list.objects.filter(camera_id=pk).order_by('-timestamp')


    return render(request,'cameraEdit.html', c)
    
@login_required(login_url="login/")
def cameraArming(request):
    cameraId=request.GET.get('cameraId', '')
    securityStatus=request.GET.get('status', '')
    
    cmd1='GET /adm/set_group.cgi?group=SYSTEM&pir_mot_mode=1&pir_mode=' + securityStatus +' HTTP/1.1\r\n'
    cmd2='GET /adm/set_group.cgi?group=EVENT&event_trigger=1&event_interval=0&event_pir=ftpu:1&event_attach=avi,1,10,20 HTTP/1.1\r\n'
    n=action_list.objects.create(action=cmd1, camera_id=cameraId)
    n.save()
    n=action_list.objects.create(action=cmd2, camera_id=cameraId)
    n.save()
    
    camera.objects.filter(id=cameraId).update(securityStatus=securityStatus)
    
    data = {
        'attribute' : 'securiyStaus= ok'
    }
    return JsonResponse(data)
