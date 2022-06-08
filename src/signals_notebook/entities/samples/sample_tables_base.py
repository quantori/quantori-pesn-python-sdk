import json
from abc import ABC, abstractmethod
from typing import cast, List

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File, Response, ResponseData
from signals_notebook.entities import Sample
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.samples.sample_table_row import SampleTableRow


class SamplesTableResponse(Response[SampleTableRow]):
    pass


class SamplesTableBase(ContentfulEntity, ABC):
    _samples_rows: List[SampleTableRow]

    @classmethod
    @abstractmethod
    def _get_entity_type(cls):
        raise NotImplementedError

    def get_content(self) -> File:
        return super()._get_content()

    @property
    def samples_rows(self) -> List[SampleTableRow]:
        if not self._samples_rows:
            self._reload_samples_rows()
        return self._samples_rows

    @classmethod
    def _get_sample_tables_endpoint(cls) -> str:
        return 'samplesTables'

    def _reload_samples_rows(self):
        self._samples_rows = []
        for item in self.fetch_sample_from_table():
            self._samples_rows.append(item)

    def fetch_sample_from_table(self, sample_ids=None, fields=None):
        api = SignalsNotebookApi.get_default_api()
        if sample_ids is not None:
            sample_ids = ','.join(sample_ids)

        sample_fields = ''
        if fields is not None:
            for field in fields:
                sample_fields += '&fields[samplesTableColumn]=' + field
            sample_fields = sample_fields[1:]

        response = api.call(
            method='GET',
            path=(self._get_sample_tables_endpoint(), self.eid, 'rows'),
            params={
                'sampleIds': sample_ids,
                'fields': sample_fields,
            },
        )

        result = SamplesTableResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

    def patch_sample_in_table(self, sample_ids=None, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()
        if sample_ids is not None:
            sample_ids = ','.join(sample_ids)

        request_body = []
        for item in self.samples_rows:
            request_body.append(item.representation_for_update)

        api.call(
            method='PATCH',
            path=(self._get_sample_tables_endpoint(), self.eid, 'rows'),
            params={
                'digest': digest,
                'force': json.dumps(force),
                'sampleIds': sample_ids,
            },
            json={
                'data': request_body,
            },
        )
        self._reload_samples_rows()

