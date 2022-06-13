import csv
import json
from abc import ABC, abstractmethod
from io import StringIO
from typing import cast, Generator, List

from pydantic import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EID, File, Response, ResponseData
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.samples.sample_table_row import SampleTableRow
from signals_notebook.jinja_env import env


class SamplesTableResponse(Response[SampleTableRow]):
    pass


class SamplesTableBase(ContentfulEntity, ABC):
    _samples_rows: List[SampleTableRow] = PrivateAttr(default=[])

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

    def _reload_samples_rows(self) -> None:
        self._samples_rows = []
        for item in self.fetch_samples_from_table():
            self._samples_rows.append(item)

    def fetch_samples_from_table(
        self, sample_ids: List[EID] = None, fields: List[str] = None
    ) -> Generator[SampleTableRow, None, None]:
        api = SignalsNotebookApi.get_default_api()

        sample_fields = ''
        if fields is not None:
            for field in fields:
                sample_fields += '&fields[samplesTableColumn]=' + field
            sample_fields = sample_fields[1:]

        response = api.call(
            method='GET',
            path=(self._get_sample_tables_endpoint(), self.eid, 'rows'),
            params={
                'sampleIds': None if sample_ids is None else ','.join(sample_ids),
                'fields': sample_fields,
            },
        )
        result = SamplesTableResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

    def patch_sample_in_table(self, sample_ids: List[EID] = None, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for item in self.samples_rows:
            request_body.append(item.representation_for_update)

        api.call(
            method='PATCH',
            path=(self._get_sample_tables_endpoint(), self.eid, 'rows'),
            params={
                'digest': digest,
                'force': json.dumps(force),
                'sampleIds': None if sample_ids is None else ','.join(sample_ids),
            },
            json={
                'data': request_body,
            },
        )
        self._reload_samples_rows()

    def get_html(self) -> str:
        file = self.get_content()
        content = StringIO(file.content.decode('utf-8'))
        csv_data = list(csv.reader(content))
        table_head = csv_data[0]
        rows = csv_data[1:]
        template = env.get_template(self._template_name)
        return template.render(name=self.name, table_head=table_head, rows=rows)
