from django.urls import path
from account.rest import login, signin

urlpatterns = [
    path('login', login),
    path('signin', signin),
]
