from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

#from camera.models import camera
from history.models import events

@login_required(login_url="/")
def historyList(request):
    username = request.user
    c = {}

    c['history'] = events.objects.filter(userWEB_id=username).order_by('-timestamp')[:40]
 
    return render(request,"historyList.html", c)