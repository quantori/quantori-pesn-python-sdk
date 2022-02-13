import abc
import json
import mimetypes
from typing import cast, List, Type, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities import Entity
from signals_notebook.entities.entity import ChildClass
from signals_notebook.types import EntitySubtype, Response, ResponseData


class Container(Entity, abc.ABC):

    @classmethod
    @abc.abstractmethod
    def _get_subtype(cls) -> EntitySubtype:
        pass

    def add_child(
        self,
        name: str,
        content: bytes,
        child_class: Type[ChildClass],
        content_type: str,
        force: bool = True,
    ) -> ChildClass:
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

        result = Response[child_class](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    def get_children(self) -> List[ChildClass]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'children'),
        )

        entity_classes = (*Entity.get_subclasses(), Entity)

        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        return [cast(ResponseData, item).body for item in result.data]
