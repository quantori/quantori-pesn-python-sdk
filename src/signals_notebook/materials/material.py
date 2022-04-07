import cgi
from typing import cast, List, Optional, TYPE_CHECKING, Union

from pydantic import BaseModel

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ChemicalDrawingFormat, File, MaterialType, MID
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.user import User

if TYPE_CHECKING:
    from signals_notebook.materials.library import Library

MaterialFieldValue = Union[str, List[str], User]


class MaterialField(BaseModel):
    value: MaterialFieldValue


class Material(BaseMaterialEntity):

    @property
    def library(self) -> 'Library':
        from signals_notebook.materials.material_store import MaterialStore
        library = MaterialStore.get(MID(f'{MaterialType.LIBRARY}:{self.asset_type_id}'))
        return cast('Library', library)

    def get_chemical_drawing(self, format: Optional[ChemicalDrawingFormat] = None) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'drawing'),
            params={
                'format': format,
            },
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )

    def get_image(self) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'image'),
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )
