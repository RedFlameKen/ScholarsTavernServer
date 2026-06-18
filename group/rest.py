from json import JSONDecoder
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

from group.controllers import create_group
from account.controllers import validate_auth_token
from util.checker import Checker


@require_http_methods(["POST"])
def create_group_endpoint(request: HttpRequest):
    # TODO: ensure that an existing user is creating the group
    auth_token = request.COOKIES["auth_token"]
    user_id = request.COOKIES["user_id"]

    validation_status = validate_auth_token(auth_token, user_id)

    if not validation_status.success:
        return HttpResponseForbidden(content=validation_status.__str__().encode())

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
        return HttpResponseBadRequest(content=err.__str__().encode())

    if not status.success:
        return HttpResponseBadRequest()

    return HttpResponse(content=status.__str__().encode())


# TODO: return a json that contains a list of group details
def search_groups_endpoint(request: HttpRequest):
    search_query = request.GET["query"]
    pass


def request_group_join_endpoint(request: HttpRequest):
    pass


# TODO: update group
