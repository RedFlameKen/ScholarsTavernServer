from django.urls import path
from account.rest import auth_login, login, logout, signin, update_user, user_details

urlpatterns = [
    path('login', login),
    path('logout', logout),
    path('signin', signin),
    path('auth', auth_login),
    path('user/<int:user_id>', user_details),
    path('user/update', update_user),
]
