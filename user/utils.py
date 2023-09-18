# import requests
from user.choices import UserType
from rest_framework.exceptions import ValidationError

from user.models import AccessLog


def get_user_ip(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")
    if not ip:
        return ""
    return ip.split(",")[0]


def get_ip_location(ip):
    return ""
    # url = "https://geolocation-db.com/json/" + ip
    # res = requests.get(url)
    # return res.json()


def create_request_log(request, status_code, user_login_token):
    ip = get_user_ip(request)
    user_agent_text = request.META.get("HTTP_USER_AGENT", "-")
    location = get_ip_location(ip)
    AccessLog.objects.create(
        user=request.user,
        device_ip=ip,
        user_agent=user_agent_text,
        location=location,
        user_login_token=user_login_token,
        url=request.path,
        method=request.method,
        status_code=status_code,
    )


def login_data(data, user):
    from user.serializers import UserPrivateProfileSerializer
    userInfo = UserPrivateProfileSerializer(instance=user).data
    data["user"] = userInfo
    
