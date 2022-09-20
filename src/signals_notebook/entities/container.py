import abc
import json
import logging
import mimetypes
import os
from typing import cast, Generator, List, Optional, Union

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
            file_name = f'{os.path.splitext(name)[0]}{extension}' if extension else name
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

    def get_children(self, order: Optional[str] = None) -> Generator[Entity, None, None]:
        """Get children of a specified entity.

        Returns:
            list of Entities
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get children for: %s', self.eid)

        params = {'order': order} if order else {}
        response = api.call(method='GET', path=(self._get_endpoint(), self.eid, 'children'), params=params)

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

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        metadata = {k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')}
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata),
            base_alias=alias + [self.name, '__Metadata'] if alias else None,
        )
        for child in self.get_children():
            child.dump(fs_handler.join_path(base_path, self.eid), fs_handler, alias + [self.name] if alias else None)

    @classmethod
    def dump_templates(cls, base_path: str, fs_handler: FSHandler) -> None:
        """Dump Container templates

        Args:
            base_path: content path where create templates dump
            fs_handler: FSHandler

        Returns:

        """
        from signals_notebook.entities import EntityStore

        entity_type = cls._get_entity_type()

        templates = EntityStore.get_list(
            include_types=[entity_type], include_options=[EntityStore.IncludeOptions.TEMPLATE]
        )
        try:
            for template in templates:
                template.dump(
                    fs_handler.join_path(base_path, 'templates', entity_type),
                    fs_handler,
                    ['Templates', entity_type.value],
                )

        except TypeError:
            pass
