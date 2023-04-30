from enum import Enum


class AuthRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"


class AuthScopes(str, Enum):
    OFFLINE_ACCESS = "offline_access"
    OPENID = "openid"
    PROFILE = "profile"
    JKP_API = "jkp-api"
    EMAIL = "email"
    ROLES = "roles"
