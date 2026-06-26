from django.urls import path
from account.rest import auth_login, login, logout, signin, test, test2

urlpatterns = [
    path('login', login),
    path('logout', logout),
    path('signin', signin),
    path('auth', auth_login),
    path('test', test),
    path('test2', test2),
]
