from typing import Literal, ClassVar, Union
from uuid import UUID

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File, Response, EID, ObjectType
from signals_notebook.entities import Entity
from signals_notebook.entities.container import Container
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env


class SampleProperties:
    id: EID
    type: Literal[ObjectType.PROPERTY]
    # co


# class SamplePropertiesResponse(Response[]):
#     pass


class Sample(ContentfulEntity):
    type: Literal[EntityType.SAMPLE] = Field(allow_mutation=False)
    _template_name: ClassVar = 'sample.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLE

    @classmethod
    def _get_sample_endpoint(cls) -> str:
        return 'samples'

    @classmethod
    def _get_sample_summary_endpoint(cls) -> str:
        return 'sampleSummary'

    @classmethod
    def _get_sample_tables_endpoint(cls) -> str:
        return 'samplesTables'

    def get_properties(self) -> None:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_sample_endpoint(), self.eid, 'properties'),
            params={
                'value': 'normalized',
            },
        )
        print(response.json())

    def get_property_by_id(self, property_id: Union[str, UUID]):
        _property_id = property_id.hex if isinstance(property_id, UUID) else property_id

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_sample_endpoint(), self.eid, 'properties', _property_id),
            params={
                'value': 'normalized',
            },
        )
        print(response.json())

    def fetch_sample_from_sample_summary(self, sample_summary_id):
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_sample_summary_endpoint(), sample_summary_id, 'samples'),
        )
        print(response.json())

    def fetch_sample_from_table(self, samples_table_id, sample_ids=None, fields=None):
        api = SignalsNotebookApi.get_default_api()
        if sample_ids is not None:
            sample_ids = ','.join(sample_ids)

        sample_fields = ''
        if fields is not None:
            pass

        response = api.call(
            method='GET',
            path=(self._get_sample_tables_endpoint(), samples_table_id, 'rows'),
            # params={
            #     'sampleIds': sample_ids,
            #
            # },
        )
        print(response.json())

    @classmethod
    def create(
        cls,
        *,
        container: Container,
        name: str,
        content_type: str,
        content: bytes = b'',
        force: bool = True,
    ) -> Entity:
        return container.add_child(
            name=name,
            content=content,
            content_type=content_type,
            force=force,
        )

    def get_content(self) -> File:
        return super()._get_content()

    def get_html(self) -> str:
        file = self._get_content()
        data = {'name': self.name, 'content': file.content.decode('utf-8')}
        template = env.get_template(self._template_name)

        return template.render(data=data)
