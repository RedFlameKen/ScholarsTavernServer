from django.db import models
from django.core import serializers
from django.db.models.manager import Manager


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=24)
    salt = models.CharField(max_length=24)
    bio = models.CharField(max_length=1024, default="")
    date_created = models.DateTimeField(auto_now=True)

    users = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class AuthTokens(models.Model):
    name = models.CharField(max_length=255)
    salt = models.CharField(max_length=24)
    expiration = models.DateTimeField(auto_now=True)

    tokens = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])
