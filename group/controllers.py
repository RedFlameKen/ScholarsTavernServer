from account.models import User
from group.models import Group, GroupMember, GroupTag, JoinRequest, Tag
from util.checker import Checker

from thefuzz import fuzz


# returns a list of tuples which contains the group id and the match ratio respectively
# terms is a list of tuples which contains a group id and the group's name respectively
def group_fuzzy_search(search: str, groups: list[Group]):
    results: list[dict] = []

    for group in groups:
        ratio = fuzz.token_sort_ratio(search, group.name)

        # if relevance is below 20, don't include in output
        if ratio < 20:
            continue

        group_dict = group.__dict__
        group_dict["tags"] = []  # tags array within the group dictionary
        group_tags = GroupTag.group_tags.filter(group_id=group)  # get all group tags of the group

        # iterate through group_tags and add all tag names to dictionary's tag field
        for group_tag in group_tags:
            tag = Tag.tags.get(id=group_tag.tag_id.pk)
            group_dict["tags"].append(tag.name)

        results.append(
            {
                "group": group_dict,
                "relevance": ratio
            }
        )

    return results


def search_groups(search: str):
    groups = Group.groups.all()

    search_results = group_fuzzy_search(search, groups)

    # sort by relevance (highest to lowest)
    search_results.sort(key=lambda v: v["relevance"], reverse=True)

    return Checker(
        success=True,
        data={
            "search_results": search_results,
        }
    )


def create_tag(name: str):
    existing = Tag.tags.filter(name=name)

    if existing.count() > 0:
        return existing[0]

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


def get_user_groups(user_id: int):
    user = User.users.get(id=user_id)

    group_memberships = GroupMember.group_members.filter(user_id=user)

    memberships = []

    for membership in group_memberships:
        found_group = Group.groups.filter(id=membership.group_id.pk)
        if found_group.count() <= 0:
            continue
        memberships.append(found_group[0].todict())

    return Checker(
        success=True,
        data={
            "memberships": memberships
        }
    )


def create_join_request(user_id: int, request_data: dict):
    group_id = request_data["group_id"]

    requester = User.users.get(id=user_id)
    group = Group.groups.get(id=group_id)

    existing_member = GroupMember.group_members.filter(user_id=requester, group_id=group)
    if existing_member.count() > 0:
        return Checker(
            message="User is already a member of this group",
        )

    join_request = JoinRequest(
        user_id=requester,
        group_id=group
    )

    join_request.save()

    return Checker(
        success=True,
        message="successfully sent request to join",
    )


def get_user_join_requests(user_id: int):
    user = User.users.get(id=user_id)

    join_requests = JoinRequest.join_requests.filter(user_id=user)

    request_details = []

    for req in join_requests:
        group_id: Group = req.group_id
        req_dict = {}

        req_dict["name"] = group_id.name

        members = GroupMember.group_members.filter(group_id=group_id)

        req_dict["members"] = []
        for member in members:
            member_user: User = member.user_id
            # TODO: add profile picture
            first_name = member_user.first_name
            last_name = member_user.last_name
            req_dict["members"].append({
                "first_name": first_name,
                "last_name": last_name,
            })

        request_details.append(req_dict)

    return Checker(
        success=True,
        data={
            "requests": request_details
        }
    )
