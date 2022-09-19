import abc
import cgi
import json
import logging
from enum import Enum
from typing import Any, List, Optional

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.jinja_env import env
from signals_notebook.utils import FSHandler

log = logging.getLogger(__name__)


class ContentfulEntity(Entity, abc.ABC):
    class ContentType(str, Enum):
        BYTES = 'application/octet-stream'

    def get_content(self) -> File:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def _get_entity_type(cls) -> EntityType:
        pass

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str = ContentType.BYTES,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        raise NotImplementedError

    def _get_content(self, format: Optional[str] = None) -> File:
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get content for: %s| %s', self.__class__.__name__, self.eid)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'export'),
            params={
                'format': format,
            },
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params['filename'],
            content=response.content,
            content_type=response.headers.get('content-type'),
        )

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        file = self._get_content()
        data = {
            'name': self.name,
            'content': 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii')),
        }
        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)

    def dump(self, base_path: str, fs_handler: FSHandler, alias: Optional[List[str]] = None) -> None:
        """Dump ContentfulEntity entity

        Args:
            base_path: content path where create dump
            fs_handler: FSHandler
            alias: Backup alias

        Returns:

        """
        content = self.get_content()
        metadata = {
            'file_name': content.name,
            'content_type': content.content_type,
            **{k: v for k, v in self.dict().items() if k in ('name', 'description', 'eid')},
        }
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, 'metadata.json'),
            json.dumps(metadata),
            base_alias=alias + [self.name, '__Metadata'] if alias else None,
        )
        file_name = content.name
        data = content.content
        fs_handler.write(
            fs_handler.join_path(base_path, self.eid, file_name),
            data,
            base_alias=alias + [self.name, file_name] if alias else None,
        )

    @classmethod
    def load(cls, path: str, fs_handler: FSHandler, parent: Container) -> None:
        """Load ContentfulEntity entity

        Args:
            path: content path
            fs_handler: FSHandler
            parent: Container where load ContentfulEntity entity

        Returns:

        """
        cls._load(path, fs_handler, parent)

    @classmethod
    def _load(cls, path: str, fs_handler: FSHandler, parent: Any) -> None:
        metadata_path = fs_handler.join_path(path, 'metadata.json')
        metadata = json.loads(fs_handler.read(metadata_path))
        content_path = fs_handler.join_path(path, metadata['file_name'])
        content_type = metadata.get('content_type')
        content = fs_handler.read(content_path)
        if content_type:
            cls.create(container=parent, name=metadata['name'], content=content, content_type=content_type, force=True)
        else:
            cls.create(container=parent, name=metadata['name'], content=content, force=True)
