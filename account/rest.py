from http.client import UNAUTHORIZED
from json import JSONDecoder
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

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

    # TODO: Add decryption

    if user_query[0].password != data["password"]:
        print("unauthorized login")
        return HttpResponse(status=UNAUTHORIZED)

    return HttpResponse(content="Welcome! successfully logged in!".encode())


# def logout(request: HttpRequest):
#     if request.content_type != "application/json":
#         print(f"Invalid content type {request.content_type}")
#         return HttpResponseBadRequest()
#
#     content_json = JSONDecoder().decode(request.body.decode())
#     if type(content_json) is not dict:
#         print(f"Invalid json format: {type(content_json)}")
#         return HttpResponseBadRequest()
#
#     if "data" not in content_json:
#         print("standard json structure malformed")
#         return HttpResponseBadRequest()
#
#     data = content_json["data"]
#
#     return HttpResponse()

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

    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    password = data["password"]

    s = User(first_name=first_name, last_name=last_name, email=email, password=password, bio=data["bio"])
    print(s)

    # TODO: Add encryption

    s.save()

    return HttpResponse()
