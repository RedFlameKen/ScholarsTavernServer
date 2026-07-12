from asgiref.sync import async_to_sync
import json
from channels.generic.websocket import WebsocketConsumer
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from account.controllers import validate_auth_token
from chat.controller import get_group_chat_channels
from group.models import Group
from util.checker import Checker


@require_http_methods(["GET"])
def get_group_channels(request: HttpRequest, group_id=-1):
    if group_id == -1:
        return HttpResponseNotFound(content=json.dumps(Checker(
            success=False,
            status=404,
            message="group not found",
        ).__dict__).encode(), content_type="application/json")

    found_group = Group.groups.filter(id=group_id)

    if found_group.count() <= 0:
        return HttpResponseNotFound(content=json.dumps(Checker(
            success=False,
            status=404,
            message="group not found",
        ).__dict__).encode(), content_type="application/json")

    auth_token = None
    user_id = -1
    if "auth_token" in request.COOKIES:
        auth_token = request.COOKIES["auth_token"]
    if "user_id" in request.COOKIES:
        user_id = request.COOKIES["user_id"]

    validation_status = validate_auth_token(auth_token, user_id)

    if not validation_status.success:
        return HttpResponseForbidden(content=validation_status.__str__().encode(), content_type="application/json")

    status = get_group_chat_channels(group_id=group_id)

    return HttpResponse(
        status=status.status,
        content=status.__str__().encode(),
        content_type="application/json"
    )
