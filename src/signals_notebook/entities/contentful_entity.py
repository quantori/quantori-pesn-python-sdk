import cgi
from typing import Optional

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities import Entity
from signals_notebook.types import File


class ContentfulEntity(Entity):
    def get_content(self, format: Optional[str] = None) -> File:
        api = SignalsNotebookApi.get_default_api()

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
