from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from camera.models import history, camera

@login_required(login_url="/")
def historyList(request):
    username = request.user.get_username()
    c = {}
    c['history'] = history.objects.filter(sensor__user__username=username).order_by('-timestamp')
 
    return render(request,"historyList.html", c)