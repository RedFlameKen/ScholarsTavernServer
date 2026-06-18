from django.core import serializers
from django.db import models
from django.db.models.base import CASCADE, Manager
from account.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    is_public = models.BooleanField()

    groups = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class Tag(models.Model):
    name = models.CharField(max_length=128)

    tags = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class GroupTag(models.Model):
    tag_id = models.ForeignKey(Tag, on_delete=CASCADE)
    group_id = models.ForeignKey(Group, on_delete=CASCADE)

    group_tags = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class GroupMember(models.Model):
    is_owner = models.BooleanField()
    is_moderator = models.BooleanField()
    user_id = models.ForeignKey(User, on_delete=CASCADE)
    group_id = models.ForeignKey(Group, on_delete=CASCADE)

    group_members = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class JoinRequest(models.Model):
    user_id = models.ForeignKey(User, on_delete=CASCADE)
    group_id = models.ForeignKey(Group, on_delete=CASCADE)

    join_requests = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])
