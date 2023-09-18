import json
import logging
from time import time
import uuid
from django.conf import settings
from django.http.response import HttpResponse
from user.utils import  create_request_log

logger = logging.getLogger("main")


class RequestHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not (
            request.path in ["/", "/swagger", "/schema/", "/user/swagger/login/"]
            or "webhook" in request.path
            or settings.BACKEND_ADMIN_URL in request.path
        ):
            platform_key = request.headers.get("x-api-key")
            if not platform_key or platform_key != settings.PLATFORM_KEY:
                return HttpResponse(status=401)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"

        return response



class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        request.start_time = time()
        requestId = str(uuid.uuid4())
        request.id = requestId
        logger.info(
            "ACCESS_REQUEST: "
            + json.dumps(
                {
                    "requestId": requestId,
                    "url": request.path,
                    "method": request.method,
                    "headers": request.headers.__dict__,
                }
            )
        )

        try:
            response = self.get_response(request)
            duration = time() - request.start_time

        except Exception as e:
            logger.info(
                "ACCESS_EXCEPTION: "
                + json.dumps({"message": e.get_message(), "requestId": requestId})
            )
            raise e

        try:
            user = request.user
            user_login_token = user.user_login_token if user.is_authenticated else ""
            if user_login_token:
                create_request_log(request, response.status_code, user_login_token)
            logger.info(
                "ACCESS_RESPONSE: "
                + json.dumps(
                    {
                        "status": response.status_code,
                        "requestId": requestId,
                        "user_login_token": user_login_token,
                    }
                )
            )
        except:
            logger.info("ACCESS_RESPONSE: " + json.dumps({"requestId": requestId}))
        response.headers["X-REQUEST-ID"] = requestId
        response.headers["X-Processing-Time"] = str(duration)
        return response
