
from django.shortcuts import render,  redirect, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from alarm.models import gateways

from .models import Care, CareRule
from .forms import rulesForm
from datetime import date
from datetime import datetime

from history.models import events



# Create your views here.

@login_required(login_url="/")    
def carePage (request):
    rules = ["ab","cd"]


    try:
        care_sts= Care.objects.get(gwID__userWEB=request.user)

    except ObjectDoesNotExist:      # Care mode has never been used : create the config (Mode=ON-OFF)
        
        current_gw=gateways.objects.get(userWEB=request.user)
        care_sts = Care.objects.create(gwID=current_gw,latch = "0")

    finally: 
        rules = CareRule.objects.filter(sensor__gwID__userWEB=request.user)   
        return render(request,"care.html",{'status': care_sts.latch,'rules':rules})




@login_required(login_url="/")
def care_cmd( request ):
    
    btn = request.GET.get('btnActive', None) 
    btn = btn[0:3]      # for security
    print("Btn= {}".format(btn))
    switch = 0
    
    if btn == 'ON':
        switch="1"
    else:
        switch="0"  
    

    care_status = Care.objects.filter(gwID__userWEB=request.user).update(latch = switch)
    data = {
        'attribute' : 'Care = ' + btn
    }
    return JsonResponse(data) 


@login_required(login_url="/")

def care_add_rule( request ):

    if request.method == 'POST':
        rule_form = rulesForm(request.POST)
        if rule_form.is_valid():
            post = rule_form.save()
            return redirect('care')

    else:
        rule_form = rulesForm()

    return render( request, 'rule_edit.html', {'form': rule_form})



        

@login_required(login_url="/")
def care_del_rule( request, pk ):
    care_rule = CareRule.objects.filter(pk=pk).delete()
    return redirect('care')
    

@login_required(login_url="/")
def care_exe_rule( request ):
    
    gw_list= Care.objects.filter(latch= 1)
    for gw in gw_list:
        print("Gw= {}".format(gw.gwID) )
    
    rules = CareRule.objects.filter(sensor__gwID= 4 )
    rules = CareRule.objects.filter(sensor__gwID__userWEB=request.user)
        
    d = date.today()
    
    for rule in rules:
        print("Rule= {}".format(rule) )

        start= datetime.combine(d, rule.start_time)
        end= datetime.combine(d, rule.end_time)
        
        evt_cnt= events.objects.filter(sensorID=rule.sensor).filter(timestamp__range=(start, end)).count()

        print("Event Qty= {}".format(evt_cnt) )
        
    return redirect('care')
 

