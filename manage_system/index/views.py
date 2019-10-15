from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from manage_system.secret import isSuperUser
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods



# Create your views here.

@login_required(login_url='/login/')
def index(request):
    superUser = "fa fa-user"
    info = ""
    if isSuperUser(request):
        superUser = "fa fa-user-plus"
        info = """<li>
                      <a class="J_menuItem" href="/index/super/">
                         <i class="{}"></i>
                         <span class="nav-label">超级管理</span>
                      </a>
                   </li>
               """.format(superUser)

    return render(request, 'index.html',
                  {"user": request.session['user'],
                   "message": {"email": 8, "notice": 6},
                   "super": superUser,
                   "super_manage": info})


@login_required(login_url='/login/')
def superManage(request):
    """仅限超级管理员"""
    if isSuperUser(request):
        return render(request, 'super.html')
    else:
        return HttpResponseRedirect('/index/')



@csrf_exempt
@require_http_methods(["GET"])
def mysqlTest(request):
    data = ""

    return JsonResponse({"status":0, "data":data})