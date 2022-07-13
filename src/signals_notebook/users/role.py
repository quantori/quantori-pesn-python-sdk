import logging
from typing import cast, Generator, Optional

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import Response, ResponseData


log = logging.getLogger(__name__)


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
    id: str
    name: str
    description: Optional[str]
    privileges: Optional[Privelege]

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'roles'

    @classmethod
    def get_list(cls) -> Generator['Role', None, None]:
        log.debug('Get List of Roles')

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
        )
        result = RoleResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

        log.debug('List of Roles were got successfully.')

    @classmethod
    def get(cls, role_id: str) -> 'Role':
        """Get role by id

        Args:
            role_id: Unique role identifier
        Returns:
            Role
        """
        log.debug('Getting Role: ', role_id)

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), role_id),
        )
        result = RoleResponse(**response.json())

        log.debug('Role: %s was got successfully.', role_id)

        return cast(ResponseData, result.data).body


class RoleResponse(Response[Role]):
    pass
