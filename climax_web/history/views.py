#from django.views.generic import ListView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from history.models import events


@login_required(login_url="/")
def historyList(request):
    
    username = request.user

    queryset = events.objects.filter(userWEB_id=username).order_by('-timestamp')[:200]  
    
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 10)

    try:
        history_page = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        history_page = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        history_page = paginator.page(paginator.num_pages)  
    
 
    return render(request,"historyList.html", {'history': history_page})
