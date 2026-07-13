from datetime import datetime

from account.models import User
from group.models import Group, GroupMember
from util.result import Result
from util.checker import Checker
from chat.models import Chat, ChatChannelGroup, ChatChannel, FileChat, TextChat, VoiceChannel


def create_chat_channel_group(group_id: Group, name: str):
    print(f"finding group {group_id}")
    found_group = Group.groups.filter(id=group_id.pk)

    if found_group.count() <= 0:
        print("group not found")
        return Result(
            status=404,
            error="group not found"
        )

    print("creating new group")

    new_group = ChatChannelGroup(
        name=name,
        group_id=group_id
    )

    new_group.save()

    print("group created")

    return Result(
        data=new_group
    )


def create_chat_channel(chat_channel_group_id: ChatChannelGroup, name: str):
    new_chat_channel = ChatChannel(
        name=name,
        channel_group_id=chat_channel_group_id
    )

    new_chat_channel.save()

    print("new channel created")

    return Result(
        data=new_chat_channel
    )


def create_voice_channel(chat_channel_group_id: ChatChannelGroup, name: str):
    new_voice_channel = VoiceChannel(
        name=name,
        channel_group_id=chat_channel_group_id
    )

    new_voice_channel.save()

    return Result(
        data=new_voice_channel
    )


def generate_initial_chat_channels(group_id: Group):
    print("creating chat channel group")
    text_channels_status = create_chat_channel_group(group_id, name="Text Channels")

    print(f"results were: {text_channels_status.data}")
    if text_channels_status.data is None:
        print(f"unable to create chat channels for {group_id}")
        return Checker(
            status=500,
            message="Unable to create chat channels"
        )

    print(f"creating chat channel with {text_channels_status.data}")
    chat_channel = create_chat_channel(
        chat_channel_group_id=text_channels_status.data,
        name="research-hall"
    )
    print(f"finished generating {chat_channel.data}")

    print("creating voice channel group")

    voice_channels_status = create_chat_channel_group(group_id, name="Voice Channels")
    if voice_channels_status.data is None:
        print(f"unable to create chat channels for {group_id}")
        return Checker(
            status=500,
            message="Unable to create chat channels"
        )

    print(f"creating voice channel with {voice_channels_status.data}")
    voice_channel = create_voice_channel(
        chat_channel_group_id=voice_channels_status.data,
        name="general-lounge"
    )

    print(f"finished generating {voice_channel.data}")
    return Checker(
        success=True,
        message="chat channels created!"
    )


def get_group_chat_channels(group_id: int):
    found_group = Group.groups.filter(id=group_id)

    if found_group.count() <= 0:
        return Checker(
            status=404,
            message="group not found"
        )

    result = []
    channel_groups = ChatChannelGroup.chat_channel_groups.filter(group_id=group_id)
    for group in channel_groups:
        channels = []
        chat_channels = ChatChannel.chat_channels.filter(channel_group_id=group)
        for chat_channel in chat_channels:
            channels.append({
                "id": int(chat_channel.pk),
                "name": chat_channel.name,
                "type": "chat",
            })
        voice_channels = VoiceChannel.voice_channels.filter(channel_group_id=group)
        for voice_channel in voice_channels:
            channels.append({
                "id": int(voice_channel.pk),
                "name": voice_channel.name,
                "type": "voice",
            })
        group_dict = {
            "id": int(group.pk),
            "name": group.name,
            "channels": channels
        }
        result.append(group_dict)

    return Checker(
        status=200,
        success=True,
        message="fetched channels",
        data={
            "group_name": found_group[0].name,
            "channel_groups": result
        }
    )


def verify_chat_channel_user(user_id: int, chat_channel_id: int):
    found_channel = ChatChannel.chat_channels.filter(id=chat_channel_id)
    if found_channel.count() <= 0:
        return Checker(
            status=404,
            message="chat channel not found"
        )

    found_channel_group = ChatChannelGroup.chat_channel_groups.filter(id=found_channel[0].channel_group_id.pk)
    if found_channel_group.count() <= 0:
        return Checker(
            status=404,
            message="channel group not found"
        )

    found_group = Group.groups.filter(id=found_channel_group[0].group_id.pk)
    if found_group.count() <= 0:
        return Checker(
            status=404,
            message="group not found"
        )

    group_id = found_group[0].pk
    found_group_member = GroupMember.group_members.filter(user_id=user_id, group_id=group_id)

    if found_group_member.count() <= 0:
        return Checker(
            status=403,
            message=f"user {user_id} is not a member group {group_id}"
        )

    return Checker(
        success=True,
        message="user is a member of the chat channel",
        data={
            "channel": found_channel[0]
        }
    )


def get_channel_chats(chat_channel_id: int):
    found_chats = Chat.chats.filter(chat_channel=chat_channel_id)

    chats = []
    for chat in found_chats:
        if chat.type == "text":
            text_chat = TextChat.text_chats.filter(chat_id=chat.pk)
            if text_chat.count() <= 0:
                continue
            chats.append({
                "id": chat.pk,
                "text": text_chat[0].text,
                "sender": chat.sender.first_name + chat.sender.last_name,
                "sender_id": chat.sender.pk,
                "time": chat.time_sent.isoformat(),
                "type": "text"
            })
        elif chat.type == "file":
            file_chat = FileChat.file_chats.filter(chat_id=chat.pk)
            if file_chat.count() <= 0:
                continue
            chats.append({
                "id": chat.pk,
                "data": file_chat[0].data,
                "time": chat.time_sent.isoformat(),
                "sender": chat.sender.first_name + chat.sender.last_name,
                "sender_id": chat.sender.pk,
                "content-type": file_chat[0].content_type,
                "type": "file"
            })
    return Checker(
        success=True,
        message="messages fetched!",
        data={
            "chats": chats
        }
    )


def create_text_chat(text: str, sender_id: int, time_sent: datetime, chat_channel_id: int):
    verification_status = verify_chat_channel_user(user_id=sender_id, chat_channel_id=chat_channel_id)

    if not verification_status.success:
        return verification_status

    user = User.users.get(id=sender_id)

    channel = verification_status.data["channel"]

    chat = Chat(
        chat_channel=channel,
        sender=user,
        type="text",
        time_sent=time_sent
    )
    chat.save()

    text_chat = TextChat(
        chat_id=chat,
        text=text
    )

    text_chat.save()

    return Checker(
        success=True,
        message="chat created",
        data={
            "id": chat.pk,
            "text": text,
            "sender": user.last_name + user.first_name,
            "sender_id": sender_id,
            "time": time_sent.isoformat(),
            "type": "text"
        }
    )
