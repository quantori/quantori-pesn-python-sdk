import cgi
from datetime import datetime
from typing import cast, List, Optional, Union

from pydantic import BaseModel, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File


class User(BaseModel):
    isEnabled: Optional[bool]
    userId: str
    userName: str
    email: str
    firstName: str
    lastName: str
    country: str
    organization: str
    lastLoginAt: datetime
    createdAt: datetime
    _picture: Optional[File] = PrivateAttr(default=None)

    def create(self):
        pass

    def save(self):
        pass

    def delete(self):
        pass

    @property
    def picture(self) -> Optional[File]:
        if self._picture:
            return self._picture

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=('users', self.userId, 'picture'),
        )
        if response.content == b'':
            return self._picture

        content_disposition = response.headers.get('content-disposition', '')
        content_type = response.headers.get('content-type')
        _, params = cgi.parse_header(content_disposition)
        file_name = f'{self.firstName}_{self.lastName}.{content_type.split("/")[-1]}'
        self._picture = File(name=file_name, content=response.content, content_type=content_type)
        return self._picture

    def get_system_groups(self):
        pass
