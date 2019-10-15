from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from PIL import Image, ImageDraw, ImageFont
import random
from manage_system.settings import BASE_DIR
from manage_system.secret import decodeRSA, ipAddress
import base64, time
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import re


# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def loginView(request):
    return render(request, 'login.html')


@csrf_exempt
@require_http_methods(["POST"])
def loginUser(request):
    data = request.POST.get("data")

    # print(request.GET)
    # print(request.POST)
    # print(request.body)
    #
    # return JsonResponse({"msg": "andbs", "code": 200, "user": {"id": 1,"title":"管理系统",
    # "username": 'admin',
    # "password": '123456',
    # "avatar": 'https://raw.githubusercontent.com/taylorchen709/markdown-images/master/vueadmin/user.png',
    # "name": '周佐政'}})

    if data:
        data = decodeRSA(data)
        username = data['username']
        password = data['password']
        checkCode = str(data['code']).lower()
        setCode = str(request.session.get("check_code", "")).lower()

        if setCode != checkCode:
            if setCode == "none" or setCode == "":
                message = "验证码已过期!"
            else:
                message = "验证码错误!"
            return JsonResponse({"status": 1, "message": message})

        current = int(time.time())
        record = base64.b64encode("&&".join([str(current), username, checkCode]).encode('utf-8')).decode("utf-8")

        user = authenticate(username=username, password=password)

        if user is not None:
            request.session['user'] = username
            request.session['record'] = record
            request.session["lastTime"] = current

            login(request, user)

            response = JsonResponse({"status": 0, "message": "登陆成功!", "url": "/index/"})
            response.set_cookie("record", record)

            return response
        else:
            return JsonResponse({"status": 1, "message": "用户名或密码错误!"})

    else:
        return JsonResponse({"status": 1, "message": "输入参数为空!"})


def logoutUser(request):
    logout(request)

    return HttpResponseRedirect('/')


@csrf_exempt
@require_http_methods(["POST"])
def flashCode(request):
    res_data = {}
    try:
        img1 = Image.new(mode="RGB", size=(132, 40), color=(225, 233, 239))

        draw1 = ImageDraw.Draw(img1, mode="RGB")

        font1 = ImageFont.truetype(BASE_DIR + "/static/font/arial.ttf", 28)
        font1 = ImageFont.truetype(BASE_DIR + "/login/static/font/arial.ttf", 28)
        check_code = ""
        for i in range(4):
            char1 = random.choice([chr(random.randint(65, 90)), str(random.randint(0, 9))])
            check_code += char1

            draw1.text([i * 33, 0], char1, (84, 93, 118), font=font1)

        with open(BASE_DIR + "/login/static/img/code.png", "wb") as f:
            img1.save(f, format="png")

        with open(BASE_DIR + "/static/img/code.png", "wb") as f:
            img1.save(f, format="png")

        request.session["check_code"] = check_code
        res_data['success'] = True

    except Exception as e:
        res_data['success'] = False
        res_data['message'] = e

    return JsonResponse(res_data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def resetPassword(request):
    old_password = request.POST.get("old")
    new_password = request.POST.get("new")
    confirm = request.POST.get('confirm')
    username = request.session['user']

    if old_password == new_password:
        return JsonResponse({"status": 1, "message": "旧密码和新密码相同!"})

    if new_password != confirm:
        return JsonResponse({"status": 1, "message": "新密码和确认密码不相同!"})

    """判断新密码组成: 要求大于等于8位,需包含数字、大小写字母、特殊字符"""
    if not re.findall("\d+", new_password) or not re.findall("[a-z]", new_password) or not re.findall("[A-Z]",
                                                                                                      new_password) or not re.findall(
        "[`~!@#$^&*()=\-+<>?<>\/\[\]]", new_password) or len(new_password) < 8:
        return JsonResponse({"status": 1, "message": "新密码强度不够,密码需包含数字、大小写字母、特殊字符且大于等于8位!"})

    user = authenticate(username=username, password=old_password)

    if user is not None:
        u = User.objects.get(username__exact=username)
        u.set_password(new_password)
        u.save()

        logoutUser(request)

        return JsonResponse({"status": 0, "message": "密码修改成功!", "url": "/"})

    else:
        return JsonResponse({"status": 1, "message": "旧密码错误，请重新输入!"})


@csrf_exempt
@require_http_methods(["POST"])
def modifyUserInfo(request):
    phone = request.POST.get("phone")
    email = request.POST.get("email")

    if not phone or not email:
        return JsonResponse({"status": 1, "message": "参数信息缺失!"})

    if not re.findall(r'^1[3456789]\d{9}$', str(phone)):
        return JsonResponse({"status": 1, "message": "手机号码错误!"})

    if not re.findall(r'^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$', str(email)):
        return JsonResponse({"status": 1, "message": "邮箱格式错误!"})

    return JsonResponse({"status": 0, "message": "个人信息修改成功!", "url": "/index/"})
