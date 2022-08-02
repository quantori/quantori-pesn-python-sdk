import logging
from typing import cast, Literal, Union

from pydantic import Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File, ResponseData, Response
from signals_notebook.entities.contentful_entity import ContentfulEntity

log = logging.getLogger(__name__)


class SubExperimentSummary(ContentfulEntity):
    type: Literal[EntityType.SUB_EXPERIMENT_SUMMARY] = Field(allow_mutation=False)
    # _template_name: ClassVar = 'excel.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SUB_EXPERIMENT_SUMMARY

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'subexpSummary'

    # def get_content(self) -> File:
    #     """Get Excel content
    #
    #     Returns:
    #         File
    #     """
    #     return super()._get_content()

    def get_rows(self):
        api = SignalsNotebookApi.get_default_api()
        # log.debug('Create Entity: %s...', cls.__name__)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'rows'),
        )
        # log.debug('Entity: %s was created.', cls.__name__)

        result = Response(**response.json())  # type: ignore
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = Response(**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]
