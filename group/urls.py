from django.urls import path

from group.rest import approve_group_join_endpoint, cancel_group_join_endpoint, create_group_endpoint, get_group_channels, get_user_groups_endpoint, get_user_join_requests_endpoint, owner_get_join_requests_endpoint, reject_group_join_endpoint, request_group_join_endpoint, search_groups_endpoint

urlpatterns = [
    path('group/', get_user_groups_endpoint),
    path('group/create', create_group_endpoint),
    path('group/search', search_groups_endpoint),
    path('group/join', request_group_join_endpoint),
    path('group/request', owner_get_join_requests_endpoint),
    path('group/request/reject', reject_group_join_endpoint),
    path('group/request/approve', approve_group_join_endpoint),
    path('group/pending', get_user_join_requests_endpoint),
    path('group/pending/cancel', cancel_group_join_endpoint),
    path('group/<int:group_id>', get_group_channels),
]
