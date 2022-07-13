import abc
import json
import logging
import mimetypes
from typing import cast, Generator, Optional, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, Response, ResponseData
from signals_notebook.entities import Entity
from signals_notebook.utils.fs_handler import FSHandler

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
        content_type: Optional[str] = None,
        force: bool = True,
    ) -> Entity:
        """Upload a file to an entity as a child.

        Args:
            name: file name
            content: entity content
            content_type: entity type
            force: Force to post attachment

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()

        if content_type:
            extension = mimetypes.guess_extension(content_type)
            file_name = f'{name}{extension}'
        else:
            content_type = mimetypes.guess_type(name)[0]
            file_name = name

        response = api.call(
            method='POST',
            path=(self._get_endpoint(), self.eid, 'children', file_name),
            params={
                'digest': None if force else self.digest,
                'force': json.dumps(force),
            },
            headers={
                'Content-Type': content_type or 'application/octet-stream',
            },
            data=content,
        )
        log.debug('Added child: %s to Container: %s', self.name, self.eid)

        entity_classes = (*Entity.get_subclasses(), Entity)
        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def get_children(self, order: str = 'layout') -> Generator[Entity, None, None]:
        """Get children of a specified entity.

        Returns:
            list of Entities
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get children for: %s', self.eid)

        params = {'order': order} if order else {}
        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'children'),
            params=params
        )

        entity_classes = (*Entity.get_subclasses(), Entity)

        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = Response[Union[entity_classes]](**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]

    def dump(self, base_path: str, fs_handler: FSHandler):
        fs_handler.write(fs_handler.join_path(base_path, self.eid, 'metadata.json'), json.dumps(self.dict()))
        for child in self.get_children():
            child.dump(fs_handler.join_path(base_path, self.eid), fs_handler)
