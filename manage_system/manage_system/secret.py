import time
from manage_system.settings import SESSION_CHECK_REQUEST_TIMEOUT
from django.http import JsonResponse
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
from django.contrib.auth.models import User
from login.models import loginTimes
from manage_system.settings import MAX_LOGIN_TIMES


def time_check(timeInfo, timeSample="%Y-%m-%d %H:%M:%S"):
    try:
        time_array = time.strptime(timeInfo, timeSample)
        time_stamp = int(time.mktime(time_array))
        return time_stamp
    except:
        return 0


def time_return(number, timeSample="%Y-%m-%d %H:%M:%S"):
    try:
        time_array = time.localtime(int(number))
        other_style = time.strftime(timeSample, time_array)
        return other_style
    except:
        return None


def check_time(number):
    number_ = 3600 - number
    minutes = int(number_) // 60
    seconds = int(number_) % 60

    return "%s分%s秒" % (str(minutes), str(seconds))


def decodeRSA(rsa_txt):
    private_key_str = '-----BEGIN RSA PRIVATE KEY-----\n' \
                      + 'MIICXAIBAAKBgQDMqNExDMYadBXKNlC1SHfsW5paOYJmSL/fWmXEhvUZpeuif6sa\n' \
                      + 'WQX6731hFeKa4houuAw5PxZGirmbFXdgukHWzJv7AlwCB7Kv+9ww5809E1m8AsH9\n' \
                      + 'NYdeB9K9pRZ9Fiih5kjG3gV2/RCRkXKBhwhhiipuWBMGNQgfpYNCGIzi6QIDAQAB\n' \
                      + 'AoGAWvLao/WNQ8w6srYYf7dIs9yxZ08PR+0kd1lwyDlBSriVUo1xuC+/nJg5G5/i\n' \
                      + 'J/o6sHBR3k7O02JqwSR0/KNJBiOqrWa/KmfXlIT4//BhTCRVAPIfABwQRrZWRUZk\n' \
                      + 'RFLS5bwb87m0BGKfBrZL3MOho3KI4rgVE/6dFYlFRzFghgECQQD3yxMcFwJjMl7R\n' \
                      + 'cLZeBVkmaE4rXIPibz5LxE6lXFU5HbEe0fnXtZhJg1P2WqzL4Im5kaHRNBBQfIlh\n' \
                      + 'y9d+KoiRAkEA03AH2PBbvEB/m3Imq2IG9zwiAkrEk0IComGFJNezj+iVlTShlmZj\n' \
                      + 'nj/7fk9AXDzXdjKT6SUaoz5f0O3yDR0g2QJATHR3D/q1fN/ky6CIVFg4GpaiT9S6\n' \
                      + 'yJnkUcJfNbxYe0gDB2xoNztLopsHxAJUQI+mTwB1OjRjOEJErU0Uz1PWUQJBAJe3\n' \
                      + 'gcoG3qx8U5SFGn5LvtfVDEo8wEUyTpWaCGHhbXVL3VnNBE3Zdo3tN1bxIyuMdMbZ\n' \
                      + 'kAzxlOWiMjrHIrKKPjECQCbEL2uhkXhNboDKGA9foEQW1D8STGLJDKmjYH9axaLc\n' \
                      + 'o7/s2ycRS/eC5SRUqqkkc4tsbnC1JtLZtpXpR9xsuvQ=\n' \
                      + '-----END RSA PRIVATE KEY-----'

    rsakey = RSA.importKey(private_key_str)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    res_data = eval(cipher.decrypt(base64.b64decode(rsa_txt), "ERROR"))
    return res_data


def time_out_verify(func):
    def check_time(request, *args, **kwargs):
        last_visit = request.session.get("lastTime", None)
        now_time = int(time.time())

        time_out = False
        if last_visit is not None:
            if now_time - last_visit >= int(SESSION_CHECK_REQUEST_TIMEOUT):
                time_out = True
            else:
                request.session["lastTime"] = now_time
        else:
            time_out = True

        if time_out:
            return JsonResponse({"status": 1, "message": "页面超时,请重新登录!",
                                 "timeout": True,
                                 "url": "/",
                                 "reason": "页面超时,请重新登录!",
                                 "rows": [], "total": 0, "index_count": 0,
                                 "data": [{"id": 0, "disabled": True, "groupName": "组织名",
                                           "groupId": 1, "selected": False, "name": ""}]})

        return func(request, *args, **kwargs)

    return check_time


def isSuperUser(request):
    username = request.session['user']
    if username:

        try:
            user = User.objects.filter(username__exact=username).last()
            if user:
                if user.is_superuser:
                    return True

        except Exception as e:
            print(e)

    return False


def writeRecord(**kwargs):
    pass


def ipAddress(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ipAddress = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ipAddress = request.META['REMOTE_ADDR']
    return ipAddress


def loginTimesCheck(username, password, ipAddress):
    loginTimesInfo = 0
    message = ""
    status = False

    timesCheck = loginTimes.objects.filter(username=username, effective=0).last()


    if timesCheck:
        try:
            loginTimesInfo = int(timesCheck.times)
            lastTime = time_check(str(timesCheck.dateTime).split(".")[0])
            currentTime = int(time.time())

            print(loginTimesInfo, lastTime, currentTime)

            if loginTimesInfo == MAX_LOGIN_TIMES:
                if currentTime - lastTime < 3600:
                    message = '该用户已被锁定,请 [%s] 后再试!' % check_time(currentTime - lastTime)
                    status = True
            else:
                loginTimes.objects.filter(username__exact=username, effective=0).update(effective=1)
                loginTimesInfo = 0

        except Exception as e:
            print(e)

    return status, loginTimesInfo, message
