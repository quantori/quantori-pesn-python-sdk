import cgi
import json
import logging
from typing import Any, cast, Optional, TYPE_CHECKING

from pydantic import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ChemicalDrawingFormat, File, MaterialType, MID
from signals_notebook.materials.base_entity import BaseMaterialEntity
from signals_notebook.materials.field import FieldContainer

if TYPE_CHECKING:
    from signals_notebook.materials.library import Library

log = logging.getLogger(__name__)


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
        """Fetch material library.

        Returns:
            Library
        """
        if not self._library:
            from signals_notebook.materials.material_store import MaterialStore

            library = MaterialStore.get(MID(f'{MaterialType.LIBRARY}:{self.asset_type_id}'))
            self._library = cast('Library', library)

        return self._library

    def get_chemical_drawing(self, format: Optional[ChemicalDrawingFormat] = None) -> File:
        """Export chemical drawing or image of a specified material.

        Args:
            format: Output type of chemical drawing.

        Returns:
            File
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Chemical Drawing as File for %s', self.eid)

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
        """Export image of a specified material except Compounds/Reagents (SNB).

        Returns:
            File
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Image as File for %s', self.eid)

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
        """Export biological sequence file of a specified material with type is DNA or Protein."

        Returns:
            File
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Bio Sequence as File for %s', self.eid)

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
        """Export an attachment for a specified field of the specific material.

        Args:
            field_id: Unique material field identifier.

        Returns:
            File
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get Attachment as File for %s', self.eid)

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
        """Update properties of a specified material.

        Args:
            force: Force to update properties without digest check.

        Returns:

        """
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
        log.debug('Save %s: %s', self.__class__.__name__, self.eid)

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

    def delete(self, digest: str = None, force: bool = True) -> None:
        """Delete Material by ID

        Args:
            eid: material ID
            digest: Indicate digest of entity. It is used to avoid conflict while concurrent editing.
                If the parameter 'force' is true, this parameter is optional.
                If the parameter 'force' is false, this parameter is required.
            force: Force to delete without doing digest check.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Deleting Material: %s', self.eid)

        api.call(
            method='DELETE',
            path=('entities', self.eid),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
        )
        log.debug('Library: %s was deleted successfully', self.eid)
