from django.urls import path

from group.rest import create_group_endpoint

urlpatterns = [
    path('group/create', create_group_endpoint),
]
