from django.urls import path
from account.rest import auth_login, login, logout, signin

urlpatterns = [
    path('login', login),
    path('logout', logout),
    path('signin', signin),
    path('auth', auth_login),
]
