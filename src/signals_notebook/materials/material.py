import cgi
import json
from typing import Any, cast, Optional, TYPE_CHECKING

from pydantic import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ChemicalDrawingFormat, File, MaterialType, MID
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.field import FieldContainer

if TYPE_CHECKING:
    from signals_notebook.materials.library import Library


class Material(BaseMaterialEntity):

    _material_fields: FieldContainer = PrivateAttr(default={})
    _library: Optional['Library'] = PrivateAttr(default=None)

    def __init__(self, _library: Optional['Library'] = None, **data):
        super().__init__(**data)
        self._library = _library

    def __getitem__(self, key: str) -> Any:
        return self._material_fields[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._material_fields[key] = value

    @property
    def library(self) -> 'Library':
        if not self._library:
            from signals_notebook.materials.material_store import MaterialStore

            library = MaterialStore.get(MID(f'{MaterialType.LIBRARY}:{self.asset_type_id}'))
            self._library = cast('Library', library)

        return self._library

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

    def get_bio_sequence(self) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'bioSequence'),
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )

    def get_attachment(self, field_id: str) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'attachments', field_id),
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )

    def save(self, force: bool = True) -> None:
        request_body = []

        for field_name, field in self._material_fields.items():
            if field.is_changed:
                request_body.append(
                    {
                        'attributes': {
                            'name': field_name,
                            'value': field.value,
                        }
                    }
                )

        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='PATCH',
            path=(self._get_endpoint(), self.eid, 'properties'),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            json={
                'data': request_body,
            },
        )
