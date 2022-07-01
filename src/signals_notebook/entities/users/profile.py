from datetime import datetime
from typing import List, Literal, Union

from pydantic import BaseModel, Field

from signals_notebook.common_types import EntityType, Response
from signals_notebook.entities import Entity


class Role(BaseModel):
    id: int
    name: str


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


class Group(Entity):
    type: Literal[EntityType.GROUP] = Field(allow_mutation=False)
    eid: str
    id: str
    is_system: bool = Field(alias='isSystem', allow_mutation=False)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.GROUP


class GroupResponse(Response[Group]):
    pass
