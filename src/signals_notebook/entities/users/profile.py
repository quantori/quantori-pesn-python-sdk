from datetime import datetime
from typing import List, Literal, Union, Generator, cast

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ObjectType, Response, ResponseData


class Privelege(BaseModel):
    can_move_experiments: bool = Field(alias='canMoveExperiments', default=True)
    can_manage_system_templates: bool = Field(alias='canManageSystemTemplates', default=True)
    can_trash_requests: bool = Field(alias='canTrashRequests', default=True)
    can_trash_samples: bool = Field(alias='canTrashSamples', default=True)
    can_share: bool = Field(alias='canShare', default=True)
    can_add_materials: bool = Field(alias='canAddMaterials', default=True)
    can_trash_experiments: bool = Field(alias='canTrashExperiments', default=True)
    can_trash_materials: bool = Field(alias='canTrashMaterials', default=True)
    can_trash_notebooks: bool = Field(alias='canTrashNotebooks', default=True)
    can_view_materials: bool = Field(alias='canViewMaterials', default=True)
    can_manage_material_libraries: bool = Field(alias='canManageMaterialLibraries', default=True)
    can_share_templates: bool = Field(alias='canShareTemplates', default=True)
    can_manage_attributes: bool = Field(alias='canManageAttributes', default=True)
    can_manage_groups: bool = Field(alias='canManageGroups', default=True)
    can_search_eln_archive: bool = Field(alias='canSearchElnArchive', default=True)
    can_configure: bool = Field(alias='canConfigure', default=True)
    can_edit_materials: bool = Field(alias='canEditMaterials', default=True)

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


class Role(BaseModel):
    id: int
    name: str
    description: str
    privileges: Privelege

    @classmethod
    def _get_entity_type(cls) -> ObjectType:
        return ObjectType.ROLE

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'roles'

    @classmethod
    def get_list(cls) -> Generator['Role', None, None]:
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
        )
        result = RoleResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

    @classmethod
    def get(cls, role_id: str) -> 'Role':
        """Get role by id

        Args:
            role_id: Unique role identifier
        Returns:
            Role
        """
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), role_id),
        )
        result = RoleResponse(**response.json())
        return cast(ResponseData, result.data).body


class RoleResponse(Response[Role]):
    pass


class Licence(BaseModel):
    id: Union[int, str]
    name: str
    expires_at: datetime = Field(alias='expiresAt')
    valid: bool
    has_service_expired: bool = Field(alias='hasServiceExpired')
    has_user_found: bool = Field(alias='hasUserFound')
    has_user_activated: bool = Field(alias='hasUserActivated')

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True


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
