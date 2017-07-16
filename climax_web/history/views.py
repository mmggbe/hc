from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from camera.models import file_list, camera

@login_required(login_url="login/")
def index(request):
    username = request.user.get_username()
    c = {}
    c['history'] = file_list.objects.filter(camera_id__user__username=username).order_by('-timestamp')
 
    return render(request,"historyList.html", c)