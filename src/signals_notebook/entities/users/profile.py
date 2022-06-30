from datetime import datetime
from typing import Union, List, Optional, Literal, ClassVar

from pydantic import BaseModel, Field

from signals_notebook.common_types import ObjectType, EntityType, Response
from signals_notebook.entities import Entity


class Role(BaseModel):
    id: int
    name: str


class Licence(BaseModel):
    id: Union[int, str]
    name: str
    expiresAt: datetime
    valid: bool
    hasServiceExpired: bool
    hasUserFound: bool
    hasUserActivated: bool


class Profile(BaseModel):
    userId: int
    firstName: str
    lastName: str
    email: str
    createdAt: datetime
    tenant: str
    roles: List[Role]
    licenses: List[Licence]


class Group(Entity):
    # type: # Literal[ObjectType.GROUP] = Field(allow_mutation=False)
    eid: str
    id: str
    isSystem: bool
    _template_name: ClassVar = 'group.html'

    @classmethod
    def _get_entity_type(cls) -> ObjectType:
        return ObjectType.GROUP

    def get_html(self):
        pass


class GroupResponse(Response[Group]):
    pass
