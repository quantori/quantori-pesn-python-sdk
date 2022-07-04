from datetime import datetime
from typing import List, Literal, Union

from pydantic import BaseModel, Field

from signals_notebook.common_types import ObjectType, Response


class Privilege(BaseModel):
    pass

class Role(BaseModel):
    id: int
    name: str
    description: str


class Licence(BaseModel):
    id: Union[int, str]
    name: str
    expires_at: datetime = Field(alias='expiresAt')
    valid: bool
    has_service_expired: bool = Field(alias='hasServiceExpired')
    has_user_found: bool = Field(alias='hasUserFound')
    has_user_activated: bool = Field(alias='hasUserActivated')


class Profile(BaseModel):
    id: str = Field(alias='userId', allow_mutation=False)
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    email: str
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    tenant: str
    roles: List[Role]
    licenses: List[Licence]

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class ProfileResponse(Response[Profile]):
    pass


class Group(BaseModel):
    type: Literal[ObjectType.GROUP] = Field(allow_mutation=False)
    eid: str
    id: str
    is_system: bool = Field(alias='isSystem', allow_mutation=False)

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True

    @classmethod
    def _get_entity_type(cls) -> ObjectType:
        return ObjectType.GROUP


class GroupResponse(Response[Group]):
    pass
