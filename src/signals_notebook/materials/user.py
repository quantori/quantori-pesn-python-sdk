from typing import Optional

from pydantic import BaseModel, Field


class Picture(BaseModel):
    link: Optional[str] = None


class User(BaseModel):
    user_id: str = Field(alias='userId')
    user_name: str = Field(alias='userName')
    email: str = Field(alias='email')
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    picture: Picture = Field(alias='picture')
    is_enabled: bool = Field(alias='isEnabled')
