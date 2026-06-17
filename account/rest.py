from http.client import UNAUTHORIZED
from json import JSONDecoder
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

from account.controllers import auth_login_user, login_user, logout_user, register_user
from account.models import User


@require_http_methods(["POST"])
def login(request: HttpRequest):
    if request.content_type != "application/json":
        print(f"Invalid content type {request.content_type}")
        return HttpResponseBadRequest()

    content_json = JSONDecoder().decode(request.body.decode())
    if type(content_json) is not dict:
        print(f"Invalid json format: {type(content_json)}")
        return HttpResponseBadRequest()

    if "data" not in content_json:
        print("standard json structure malformed")
        return HttpResponseBadRequest()

    data = content_json["data"]

    user_query = User.users.filter(email=data["email"])
    if user_query.count() <= 0:
        print("user not found")
        return HttpResponseForbidden()

    login_status = login_user(data)

    if not login_status.success:
        return HttpResponse(status=UNAUTHORIZED, content=login_status.__str__().encode())

    response = HttpResponse(content=login_status.__str__().encode())

    response.set_cookie(
        key="auth_token",
        value=login_status.data["token"],
        httponly=True,
        secure=True,
        path="/",
        max_age=24 * 3600 * 62
    )

    response.set_cookie(
        key="user_id",
        value=user_query[0].id,
        httponly=True,
        secure=True,
        path="/",
        max_age=24 * 3600 * 62
    )

    return response


@require_http_methods(["GET", "POST"])
def logout(request: HttpRequest):
    auth_token = request.COOKIES["auth_token"]
    user_id = request.COOKIES["user_id"]

    status = logout_user(auth_token, user_id)

    if not status.success:
        return HttpResponseForbidden(content=status.__str__().encode())

    return HttpResponse(content=status.__str__().encode())


@require_http_methods(["GET", "POST"])
def auth_login(request: HttpRequest):
    auth_token = request.COOKIES["auth_token"]
    user_id = request.COOKIES["user_id"]

    print(f"auth_token: {auth_token}")
    print(f"user_id: {user_id}")
    status = auth_login_user(auth_token, user_id)

    if not status.success:
        print("auth login failed")
        return HttpResponse(status=UNAUTHORIZED, content=status.__str__().encode())

    return HttpResponse(content=b"successfully logged in")


@require_http_methods(["POST"])
def signin(request: HttpRequest):
    if request.content_type != "application/json":
        print(f"Invalid content type {request.content_type}")
        return HttpResponseBadRequest()

    content_json = JSONDecoder().decode(request.body.decode())
    if type(content_json) is not dict:
        print(f"Invalid json format: {type(content_json)}")
        return HttpResponseBadRequest()

    if "data" not in content_json:
        print("standard json structure malformed")
        return HttpResponseBadRequest()

    data = content_json["data"]

    status = register_user(data)

    if not status.success:
        return HttpResponseBadRequest(content=json.dumps(status.__dict__).encode())

    return HttpResponse(content=json.dumps(status.__dict__).encode())
