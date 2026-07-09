from http.client import UNAUTHORIZED
from json import JSONDecoder
import json
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.http.response import HttpResponseServerError
from django.views.decorators.http import require_http_methods

from group.controllers import create_group, create_join_request, get_user_groups, get_user_join_requests, search_groups
from account.controllers import validate_auth_token
from util.checker import Checker


@require_http_methods(["POST"])
def create_group_endpoint(request: HttpRequest):
    auth_token = None
    user_id = -1
    if "auth_token" in request.COOKIES:
        auth_token = request.COOKIES["auth_token"]
    if "user_id" in request.COOKIES:
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

    try:
        status = create_group(data, user_id=user_id)
    except TypeError:
        err = Checker(
            success=False,
            message="malformed request"
        )
        return HttpResponseBadRequest(content=err.__str__().encode(), content_type="application/json")

    if not status.success:
        return HttpResponseBadRequest()

    return HttpResponse(content=status.__str__().encode(), content_type="application/json")


@require_http_methods(["GET"])
def get_user_groups_endpoint(request: HttpRequest):
    auth_token = None
    user_id = -1
    if "auth_token" in request.COOKIES:
        auth_token = request.COOKIES["auth_token"]
    if "user_id" in request.COOKIES:
        user_id = request.COOKIES["user_id"]

    validation_status = validate_auth_token(auth_token, user_id)

    if not validation_status.success:
        return HttpResponseForbidden(content=validation_status.__str__().encode(), content_type="application/json")

    status = get_user_groups(user_id)

    if not status.success:
        return HttpResponseServerError()

    return HttpResponse(content=status.__str__().encode(), content_type="application/json")


# return a json that contains a list of group details
@require_http_methods(["GET"])
def search_groups_endpoint(request: HttpRequest):
    search_query = request.GET.get("query", "").__str__()
    if not search_query:
        return HttpResponseBadRequest()

    status = search_groups(search_query)

    return HttpResponse(
        content=json.dumps(status, default=lambda r: {
            k: v
            for k, v in r.__dict__.items()
            if k != "_state"
        }).encode()
    )


@require_http_methods(["POST"])
def request_group_join_endpoint(request: HttpRequest):
    auth_token = None
    user_id = -1
    if "auth_token" in request.COOKIES:
        auth_token = request.COOKIES["auth_token"]
    if "user_id" in request.COOKIES:
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

    data: dict = content_json["data"]

    if "group_id" not in data:
        return HttpResponseBadRequest()

    status = create_join_request(user_id, data)

    if not status.success:
        return HttpResponseForbidden(content=status.__str__().encode(), content_type="application/json")

    return HttpResponse(content=status.__str__().encode(), content_type="application/json")


@require_http_methods(["GET"])
def get_user_join_requests_endpoint(request: HttpRequest):
    auth_token = None
    user_id = -1
    if "auth_token" in request.COOKIES:
        auth_token = request.COOKIES["auth_token"]
    if "user_id" in request.COOKIES:
        user_id = request.COOKIES["user_id"]

    validation_status = validate_auth_token(auth_token, user_id)

    if not validation_status.success:
        return HttpResponseForbidden(content=validation_status.__str__().encode(), content_type="application/json")

    status = get_user_join_requests(user_id)

    if not status.success:
        return HttpResponseServerError()

    return HttpResponse(content=status.__str__().encode(), content_type="application/json")

# TODO: update group
