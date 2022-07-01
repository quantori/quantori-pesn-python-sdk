import csv
from io import StringIO
from typing import cast, ClassVar, Dict, Generator, List, Literal, Union
from uuid import UUID

from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EID, EntityType, File, Response, ResponseData
from signals_notebook.entities import Sample
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.jinja_env import env


class SamplesContainerResponse(Response[Sample]):
    pass


class SamplesContainer(ContentfulEntity):
    type: Literal[EntityType.SAMPLES_CONTAINER] = Field(allow_mutation=False)
    _template_name: ClassVar = 'samplesContainer.html'
    _samples: List[Sample] = PrivateAttr(default=[])
    _samples_by_id: Dict[EID, Sample] = PrivateAttr(default={})

    def __getitem__(self, index: Union[int, str, UUID, EID]) -> Sample:
        if not self._samples:
            self._reload_samples()

        if isinstance(index, int):
            return self._samples[index]

        if isinstance(index, str):
            return self._samples_by_id[EID(index)]

        if isinstance(index, EID):
            return self._samples_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._samples:
            self._reload_samples()
        return self._samples.__iter__()

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SAMPLES_CONTAINER

    def get_content(self) -> File:
        return super()._get_content()

    def _reload_samples(self) -> None:
        self._samples = []
        self._samples_by_id = {}
        for item in self._get_samples():
            sample = cast(Sample, item)
            assert sample.eid

            self._samples.append(item)
            self._samples_by_id[sample.eid] = sample

    def _get_samples(self) -> Generator[Sample, None, None]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(super()._get_endpoint(), self.eid, 'children'),
        )

        result = SamplesContainerResponse(**response.json())

        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = SamplesContainerResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]

    def save(self, force: bool = True) -> None:
        for item in self._samples:
            item.save(force=force)
        self._reload_samples()

    def get_html(self) -> str:
        file = self.get_content()
        content = StringIO(file.content.decode('utf-8'))
        csv_data = list(csv.reader(content))
        table_head = csv_data[0]
        rows = csv_data[1:]
        template = env.get_template(self._template_name)
        return template.render(name=self.name, table_head=table_head, rows=rows)
