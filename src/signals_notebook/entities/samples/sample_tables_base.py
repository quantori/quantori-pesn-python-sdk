import json
from abc import ABC, abstractmethod

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File
from signals_notebook.entities.contentful_entity import ContentfulEntity


class SamplesTableBase(ContentfulEntity, ABC):

    @classmethod
    @abstractmethod
    def _get_entity_type(cls):
        raise NotImplementedError

    def get_content(self) -> File:
        return super()._get_content()

    @classmethod
    def _get_sample_tables_endpoint(cls) -> str:
        return 'samplesTables'

    def fetch_sample_from_table(self, sample_ids=None, fields=None):
        api = SignalsNotebookApi.get_default_api()
        if sample_ids is not None:
            sample_ids = ','.join(sample_ids)

        sample_fields = ''
        if fields is not None:
            pass

        response = api.call(
            method='GET',
            path=(self._get_sample_tables_endpoint(), self.eid, 'rows'),
            params={
                'sampleIds': sample_ids,
                'fields': sample_fields
            },
        )
        print(response.json())

    def patch_sample_in_table(self, sample_ids=None, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()
        if sample_ids is not None:
            sample_ids = ','.join(sample_ids)

        response = api.call(
            method='PATCH',
            path=(self._get_sample_tables_endpoint(), self.eid, 'rows'),
            params={
                'digest': digest,
                'force': json.dumps(force),
                'sampleIds': sample_ids,
            },
        )
        print(response.json())
