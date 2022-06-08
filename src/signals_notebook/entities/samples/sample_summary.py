from typing import cast, ClassVar, Literal

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, Response, ResponseData
from signals_notebook.entities import Sample
from signals_notebook.entities.samples.sample_tables_base import SamplesTableBase


class SampleSummaryResponse(Response[Sample]):
    pass


class SampleSummary(SamplesTableBase):
    type: Literal[EntityType.SAMPLE_SUMMARY] = Field(allow_mutation=False)
    _template_name: ClassVar = 'sampleSummary.html'

    @classmethod
    def _get_entity_type(cls):
        return EntityType.SAMPLE_SUMMARY

    @classmethod
    def _get_sample_summary_endpoint(cls) -> str:
        return 'sampleSummary'

    def fetch_samples_from_sample_summary(self):
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_sample_summary_endpoint(), self.eid, 'samples'),
        )
        result = SampleSummaryResponse(**response.json())
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = SampleSummaryResponse(**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]
