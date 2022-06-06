import abc
import cgi
import logging
from typing import Optional

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File
from signals_notebook.entities import Entity
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class ContentfulEntity(Entity, abc.ABC):

    @classmethod
    @abc.abstractmethod
    def _get_entity_type(cls) -> EntityType:
        pass

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
            name=params['filename'], content=response.content, content_type=response.headers.get('content-type')
        )

    def get_html(self) -> str:
        file = self._get_content()
        data = {
            'name': self.name,
            'content': 'data:{};base64,{}'.format(file.content_type, file.base64.decode('ascii')),
        }
        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
