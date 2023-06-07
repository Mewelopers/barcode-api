from enum import Enum


class AuthRole(str, Enum):
    """
    Roles that are used for authorization.
    """

    ADMIN = "admin"
    CLIENT = "client"


class AuthScopes(str, Enum):
    """The OIDC scopes that are used for authentication."""

    OFFLINE_ACCESS = "offline_access"
    OPENID = "openid"
    PROFILE = "profile"
    JKP_API = "jkp-api"
    EMAIL = "email"
    ROLES = "roles"
