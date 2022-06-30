from datetime import datetime
from typing import Union, List

from pydantic import BaseModel


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
