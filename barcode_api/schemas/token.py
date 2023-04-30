from fastapi_oidc import IDToken
from pydantic import Extra, validator

from .auth import AuthRole, AuthScopes


class OIDCToken(IDToken):
    role: set[AuthRole] | AuthRole
    email: str
    name: str
    scope: set[AuthScopes]

    # Might be missing if the authentication scope does not cover jkp_api
    aud: str | None

    @validator("scope", pre=True)
    def validate_scope(cls, v: list[str]) -> set[AuthScopes]:
        scopes = set()
        for scope in v:
            try:
                scopes.add(AuthScopes(scope))
            except ValueError:
                pass
        return scopes

    def is_in_any_role(self, permissions: list[AuthRole]) -> bool:
        return any(role in permissions for role in self.roles)

    @property
    def user_id(self) -> str:
        return self.sub

    @property
    def roles(self) -> set[AuthRole]:
        if isinstance(self.role, set):
            return self.role
        return {self.role}

    @property
    def scopes(self) -> set[AuthScopes]:
        return self.scope

    @property
    def user_email(self) -> str:
        return self.email

    @property
    def user_name(self) -> str:
        return self.name

    class Config:
        extra = Extra.allow
        # Required for pydantic to accept enum values as strings
        use_enum_values = True
