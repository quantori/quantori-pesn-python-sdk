import logging
from typing import cast, ClassVar, Dict, List, Literal, Union
from uuid import UUID

from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File, Response, ResponseData
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.plates.plate_row import PlateRow
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class PlateContainerDataResponse(Response[PlateRow]):
    pass


class PlateContainer(ContentfulEntity):
    type: Literal[EntityType.PLATE_CONTAINER] = Field(allow_mutation=False)
    _rows: List[PlateRow] = PrivateAttr(default=[])
    _rows_by_id: Dict[UUID, PlateRow] = PrivateAttr(default={})
    _template_name: ClassVar = 'plate_container.html'

    def __getitem__(self, index: Union[int, str, UUID]) -> PlateRow:
        if not self._rows:
            self._reload_data()

        if isinstance(index, int):
            return self._rows[index]

        if isinstance(index, str):
            return self._rows_by_id[UUID(index)]

        if isinstance(index, UUID):
            return self._rows_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._rows:
            self._reload_data()

        return self._rows.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.PLATE_CONTAINER

    def _reload_data(self):
        api = SignalsNotebookApi.get_default_api()
        log.debug('Reloading rows for Plate Container: %s...', self.eid)

        response = api.call(
            method='GET',
            path=('plates', self.eid, 'summary'),
        )
        result = PlateContainerDataResponse(**response.json())
        self._rows = []
        self._rows_by_id = {}
        for item in result.data:
            row = cast(PlateRow, cast(ResponseData, item).body)
            assert row.id

            self._rows.append(row)
            self._rows_by_id[row.id] = row
        log.debug('Data in Plate Container: %s were reloaded', self.eid)

    def get_content(self) -> File:
        """Get PlateContainer content

        Returns:
            File
        """
        return super()._get_content()

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered HTML in string format
        """
        if not self._rows:
            self._reload_data()
        table_head = None
        if self._rows:
            table_head = self._rows[0]

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(name=self.name, table_head=table_head, rows=self._rows)
