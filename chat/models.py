from django.core import serializers
from django.db import models
from django.db.models.base import CASCADE
from django.db.models.manager import Manager

from group.models import Group


class ChatChannelGroup(models.Model):
    name = models.CharField(max_length=100)
    group_id = models.ForeignKey(Group, on_delete=CASCADE)

    chat_channel_groups = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class ChatChannel(models.Model):
    name = models.CharField(max_length=100)
    channel_group_id = models.ForeignKey(ChatChannelGroup, on_delete=CASCADE)

    chat_channels = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class VoiceChannel(models.Model):
    name = models.CharField(max_length=100)
    channel_group_id = models.ForeignKey(ChatChannelGroup, on_delete=CASCADE)

    voice_channels = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class Chat(models.Model):
    type = models.CharField(max_length=24)
    chat_id = models.ForeignKey(ChatChannel, on_delete=CASCADE)

    chats = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class TextChats(models.Model):
    text = models.CharField(max_length=100)
    chat_id = models.ForeignKey(Chat, on_delete=CASCADE)

    text_chats = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])


class FileChats(models.Model):
    text = models.BinaryField()
    content_type = models.CharField(max_length=100)
    chat_id = models.ForeignKey(Chat, on_delete=CASCADE)

    text_chats = Manager()

    def __str__(self):
        return serializers.serialize('json', [self,])
