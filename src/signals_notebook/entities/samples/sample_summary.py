from typing import Literal, ClassVar

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType
from signals_notebook.entities.samples.sample_tables_base import SamplesTableBase


class SampleSummary(SamplesTableBase):
    type: Literal[EntityType.SAMPLE_SUMMARY] = Field(allow_mutation=False)
    _template_name: ClassVar = 'sampleSummary.html'

    @classmethod
    def _get_entity_type(cls):
        return EntityType.SAMPLE_SUMMARY

    @classmethod
    def _get_sample_summary_endpoint(cls) -> str:
        return 'sampleSummary'

    def fetch_sample_from_sample_summary(self, sample_summary_id):
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_sample_summary_endpoint(), sample_summary_id, 'samples'),
        )
        print(response.json())
