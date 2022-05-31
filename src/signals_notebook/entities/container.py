import abc
import json
import logging
import mimetypes
from typing import cast, List, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, Response, ResponseData
from signals_notebook.entities import Entity

log = logging.getLogger(__name__)


class Container(Entity, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def _get_entity_type(cls) -> EntityType:
        pass

    def add_child(
        self,
        name: str,
        content: bytes,
        content_type: str,
        force: bool = True,
    ) -> Entity:
        api = SignalsNotebookApi.get_default_api()

        extension = mimetypes.guess_extension(content_type)
        file_name = f'{name}{extension}'

        response = api.call(
            method='POST',
            path=(self._get_endpoint(), self.eid, 'children', file_name),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            headers={
                'Content-Type': content_type,
            },
            data=content,
        )
        log.debug('Added child: %s to Container: %s', self.name, self.eid)

        entity_classes = (*Entity.get_subclasses(), Entity)
        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def get_children(self) -> List[Entity]:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get children for: %s', self.eid)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'children'),
            params={
                'order': 'layout',
            },
        )

        entity_classes = (*Entity.get_subclasses(), Entity)

        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        return [cast(ResponseData, item).body for item in result.data]
