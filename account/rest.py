from http.client import FORBIDDEN, UNAUTHORIZED
from json import JSONDecoder
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.http import require_http_methods

from account.controllers import auth_login_user, get_user_details, login_user, logout_user, register_user, update_user_details, validate_auth_token
from account.models import User
from util.checker import Checker


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
        return HttpResponseForbidden(content=Checker(
            success=False,
            status=FORBIDDEN,
            message="user not found"
        ).__str__().encode(), content_type="application/json")

    login_status = login_user(data)

    if not login_status.success:
        return HttpResponse(status=UNAUTHORIZED, content=login_status.__str__().encode(), content_type="application/json")

    response = HttpResponse(content=login_status.__str__().encode(), content_type="application/json")

    response.set_cookie(
        key="auth_token",
        value=login_status.data["token"],
        samesite="None",
        httponly=True,
        secure=True,
        path="/",
        max_age=24 * 3600 * 62
    )

    response.set_cookie(
        key="user_id",
        value=str(user_query[0].id),
        httponly=True,
        samesite="None",
        secure=True,
        path="/",
        max_age=24 * 3600 * 62
    )

    for _, morsel in response.cookies.items():
        morsel["partitioned"] = True

    return response


@require_http_methods(["GET", "POST"])
def logout(request: HttpRequest):
    auth_token = request.COOKIES["auth_token"]
    user_id = request.COOKIES["user_id"]

    status = logout_user(auth_token, user_id)

    if not status.success:
        return HttpResponseForbidden(content=status.__str__().encode(), content_type="application/json")

    return HttpResponse(content=status.__str__().encode(), content_type="application/json")


@require_http_methods(["GET", "POST"])
def auth_login(request: HttpRequest):
    auth_token = request.COOKIES["auth_token"]
    user_id = request.COOKIES["user_id"]

    status = auth_login_user(auth_token, user_id)

    if not status.success:
        print("auth login failed")
        return HttpResponse(status=UNAUTHORIZED, content=status.__str__().encode(), content_type="application/json")

    return HttpResponse(content=status.__str__().encode(), content_type="application/json")


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
        return HttpResponseBadRequest(content=json.dumps(status.__dict__).encode(), content_type="application/json")

    return HttpResponse(content=json.dumps(status.__dict__).encode(), content_type="application/json")


@require_http_methods(["GET"])
def user_details(_: HttpRequest, user_id=-1):
    if user_id == -1:
        return HttpResponseNotFound(content=json.dumps(Checker(
            success=False,
            status=404,
            message="user not found",
        ).__dict__).encode(), content_type="application/json")

    status = get_user_details(user_id)

    if not status.success:
        return HttpResponseNotFound(content=json.dumps(
            status.__dict__
        ).encode(), content_type="application/json")

    return HttpResponse(content=json.dumps(
        status.__dict__
    ).encode(), content_type="application/json")


def update_user(request: HttpRequest):
    auth_token = request.COOKIES["auth_token"]
    user_id = request.COOKIES["user_id"]

    validation_status = validate_auth_token(auth_token, user_id)

    if not validation_status.success:
        return HttpResponseForbidden(content=validation_status.__str__().encode(), content_type="application/json")

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

    status = update_user_details(data, user_id)

    return HttpResponse(content=json.dumps(
        status.__dict__
    ).encode(), content_type="application/json")
