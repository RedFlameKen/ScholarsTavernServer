from django.db import models
from django.core import serializers
from django.db.models.manager import Manager


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=44)
    salt = models.CharField(max_length=100)
    bio = models.CharField(max_length=1024, default="")
    date_created = models.DateTimeField(auto_now=True)

    users = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class AuthToken(models.Model):
    token = models.CharField(primary_key=True, max_length=44, null=False)
    salt = models.CharField(max_length=24)
    expiration = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    tokens = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])
