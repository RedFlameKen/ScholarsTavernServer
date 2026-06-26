from django.urls import path

from group.rest import create_group_endpoint, get_user_groups_endpoint, get_user_join_requests_endpoint, request_group_join_endpoint, search_groups_endpoint

urlpatterns = [
    path('group/', get_user_groups_endpoint),
    path('group/create', create_group_endpoint),
    path('group/search', search_groups_endpoint),
    path('group/join', request_group_join_endpoint),
    path('group/requests', get_user_join_requests_endpoint),
]
