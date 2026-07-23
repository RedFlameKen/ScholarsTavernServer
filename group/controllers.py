from account.models import User
from group.models import Group, GroupMember, GroupTag, JoinRequest, Tag
from util.checker import Checker
from chat.controller import generate_initial_chat_channels

from thefuzz import fuzz


# returns a list of tuples which contains the group id and the match ratio respectively
# terms is a list of tuples which contains a group id and the group's name respectively
def group_fuzzy_search(search: str, groups: list[Group], user_id: int):
    results: list[dict] = []

    for group in groups:
        ratio = fuzz.token_sort_ratio(search, group.name)

        # if relevance is below 20, don't include in output
        if ratio < 20:
            continue

        tags = []  # tags array within the group dictionary
        group_tags = GroupTag.group_tags.filter(group_id=group)  # get all group tags of the group

        is_member = False
        if GroupMember.group_members.filter(group_id=group, user_id=user_id):
            is_member = True

        has_requested = False
        if JoinRequest.join_requests.filter(group_id=group, user_id=user_id):
            has_requested = True

        members = GroupMember.group_members.filter(group_id=group)

        members_list = []
        for member in members:
            member_user: User = member.user_id
            # TODO: add profile picture
            first_name = member_user.first_name
            last_name = member_user.last_name
            members_list.append({
                "first_name": first_name,
                "last_name": last_name,
            })

        # iterate through group_tags and add all tag names to dictionary's tag field
        for group_tag in group_tags:
            tag = Tag.tags.get(id=group_tag.tag_id.pk)
            tags.append(tag.name)

        group_dict = {
            "id": group.pk,
            "is_member": is_member,
            "has_requested": has_requested,
            "is_public": group.is_public,
            "name": group.name,
            "tags": tags,
            "members": members_list
        }

        results.append(
            {
                "group": group_dict,
                "relevance": ratio
            }
        )

    return results


def search_groups(search: str, user_id: int):
    groups = Group.groups.all()

    search_results = group_fuzzy_search(search, groups, user_id)

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


# TODO: upon group creation, group id should be returned
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

    print("starting generation")

    generation_status = generate_initial_chat_channels(group_id=group)

    print("generated")
    return generation_status


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

    if group.is_public:
        membership = GroupMember(
            user_id=requester,
            group_id=group,
            is_moderator=False,
            is_owner=False
        )

        membership.save()

        return Checker(
            success=True,
            message="Successfully joined the group!"
        )

    pending_requests = JoinRequest.join_requests.filter(user_id=requester, group_id=group)
    if pending_requests.count() > 0:
        return Checker(
            message="User made a request to join this group",
        )

    join_request = JoinRequest(
        user_id=requester,
        group_id=group
    )

    join_request.save()

    return Checker(
        success=True,
        message="successfully sent request to join",
        data={"id": group.pk}
    )


def get_user_join_requests(user_id: int):
    user = User.users.get(id=user_id)

    join_requests = JoinRequest.join_requests.filter(user_id=user)

    request_details = []

    for req in join_requests:
        group_id: Group = req.group_id
        req_dict = {}

        req_dict["id"] = req.pk
        req_dict["name"] = group_id.name
        req_dict["group_id"] = group_id.pk

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


def approve_join_request(mod_id: int, requester_id: int, group_id: int):
    found_mod = GroupMember.group_members.filter(group_id=group_id, user_id=mod_id)

    if found_mod.count() <= 0:
        return Checker(
            message="user is not a member of the group"
        )

    if not found_mod[0].is_moderator:
        return Checker(
            message="user is not a moderator"
        )

    group = Group.groups.get(id=group_id)
    requester = User.users.get(id=requester_id)

    requests = JoinRequest.join_requests.filter(user_id=requester, group_id=group)

    if requests.count() <= 0:
        return Checker(
            message=f"User {requester_id} does not have a request to {group_id}"
        )

    requests[0].delete()

    membership = GroupMember(
        user_id=requester,
        group_id=group,
        is_moderator=False,
        is_owner=False
    )

    membership.save()

    return Checker(
        success=True,
        message="Successfully approved join request!"
    )


def reject_join_request(mod_id: int, requester_id: int, group_id: int):
    found_mod = GroupMember.group_members.filter(group_id=group_id, user_id=mod_id)

    if found_mod.count() <= 0:
        return Checker(
            message="user is not a member of the group"
        )

    if not found_mod[0].is_moderator:
        return Checker(
            message="user is not a moderator"
        )

    group = Group.groups.get(id=group_id)

    requests = JoinRequest.join_requests.filter(user_id=requester_id, group_id=group)

    if requests.count() <= 0:
        return Checker(
            message=f"User {requester_id} does not have a request to {group_id}"
        )

    requests[0].delete()

    return Checker(
        success=True,
        message="request canceled!"
    )


def cancel_join_request(user_id: int, group_id: int):
    user = User.users.get(id=user_id)
    group = Group.groups.get(id=group_id)

    requests = JoinRequest.join_requests.filter(user_id=user, group_id=group)

    if requests.count() <= 0:
        return Checker(
            message=f"User {user.pk} does not have a request to {group.pk}"
        )

    requests[0].delete()

    return Checker(
        success=True,
        message="request canceled!"
    )


def mod_get_group_join_requests(user_id: int):
    modding_groups = GroupMember.group_members.filter(user_id=user_id, is_moderator=True)

    request_details = []

    for membership in modding_groups:
        group = membership.group_id

        join_requests = JoinRequest.join_requests.filter(group_id=group)

        for req in join_requests:
            requester_id: User = req.user_id
            req_dict = {}

            req_dict["id"] = req.pk
            req_dict["name"] = group.name
            req_dict["group_id"] = group.pk
            req_dict["requester"] = {
                "id": requester_id.pk,
                "first_name": requester_id.first_name,
                "last_name": requester_id.last_name,
            }

            request_details.append(req_dict)

    return Checker(
        success=True,
        data={
            "requests": request_details
        }
    )


def get_group_join_requests(group_id: int):
    group = Group.groups.get(id=group_id)

    join_requests = JoinRequest.join_requests.filter(group_id=group)

    request_details = []

    for req in join_requests:
        user_id: User = req.user_id
        req_dict = {}

        req_dict["name"] = group.name
        req_dict["group_id"] = group.pk
        req_dict["user_id"] = user_id.pk

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


def verify_group_member(user_id: int, group_id: int):
    found = GroupMember.group_members.filter(user_id=user_id, group_id=group_id)

    if found.count() <= 0:
        return Checker(
            status=403,
            message=f"user {user_id} is not a member group {group_id}"
        )

    return Checker(
        success=True,
        message="user is a member of the group"
    )
