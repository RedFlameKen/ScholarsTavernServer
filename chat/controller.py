from group.models import Group
from util.result import Result
from util.checker import Checker
from chat.models import ChatChannelGroup, ChatChannel, VoiceChannel


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
