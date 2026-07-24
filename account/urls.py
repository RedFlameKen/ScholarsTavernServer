from django.urls import path
from account.rest import auth_login, get_profile_picture, login, logout, signin, update_profile_picture_endpoint, update_user, user_details

urlpatterns = [
    path('login', login),
    path('user/pfp/update', update_profile_picture_endpoint),
    path('logout', logout),
    path('signin', signin),
    path('auth', auth_login),
    path('user/<int:user_id>', user_details),
    path('user/pfp/<int:user_id>', get_profile_picture),
    path('user/update', update_user),
]
