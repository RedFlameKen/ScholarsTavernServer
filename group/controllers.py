from account.models import User
from group.models import Group, GroupMember, GroupTag, Tag
from util.checker import Checker


def create_tag(name: str):
    existing = Tag.tags.filter(name=name)

    if existing.count() > 0:
        return None

    tag = Tag(name=name)
    tag.save()

    return tag


def create_group_tag(group_id: Group, tag_id: Tag):
    group_tag = GroupTag(
        group_id=group_id,
        tag_id=tag_id,
    )

    group_tag.save()

    return group_tag


def create_group(group_data: dict, user_id: int):
    name: str = group_data["name"]
    is_public: bool = group_data["is_public"]
    tags: list = group_data["tags"]

    group = Group(
        name=name,
        is_public=is_public,
    )

    group.save()
    owner = User.users.get(id=user_id)  # assumes that cookie is validated and this user has only one instance

    group_owner = GroupMember(
        is_owner=True,
        is_moderator=True,
        user_id=owner,
        group_id=group
    )

    group_owner.save()

    for tag in tags:
        created_tag = create_tag(tag)
        if created_tag:
            create_group_tag(group, created_tag)

    return Checker(
        success=True,
        message="Successfully created the group!"
    )
