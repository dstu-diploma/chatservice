from .roles import UserRoles


class PublicAccess:
    pass


class Group:
    members: frozenset[UserRoles]

    def __init__(self, *members: UserRoles):
        self.members = frozenset(members)


PermissionAcl = UserRoles | Group | PublicAccess


class Permissions:
    __PRIVILEGED = (
        PublicAccess()
    )  # Group(UserRoles.Organizer, UserRoles.Helper, UserRoles.Admin)

    GetSelfRequests = UserRoles.User
    CreateRequest = UserRoles.User
    CreateMessage = UserRoles.User
    CloseRequest = UserRoles.User

    GetAllRequests = __PRIVILEGED
    CreateMessageAsSupport = __PRIVILEGED
    CloseRequestAsSupport = __PRIVILEGED


def perform_check(acl: PermissionAcl, role: UserRoles) -> bool:
    if isinstance(acl, PublicAccess):
        return True
    elif isinstance(acl, UserRoles):
        return role is acl

    return role in acl.members
