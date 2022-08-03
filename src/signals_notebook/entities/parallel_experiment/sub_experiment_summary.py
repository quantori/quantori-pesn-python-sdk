import logging
from typing import cast, Literal, Union, List, Dict
from uuid import UUID
from pydantic import Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EntityType, File, ResponseData, Response
from signals_notebook.entities.contentful_entity import ContentfulEntity
from signals_notebook.entities.parallel_experiment.row import Row

log = logging.getLogger(__name__)


class SubExpSummaryResponse(Response[Row]):
    pass


class SubExperimentSummary(ContentfulEntity):
    type: Literal[EntityType.SUB_EXPERIMENT_SUMMARY] = Field(allow_mutation=False)
    _rows: List[Row] = PrivateAttr(default=[])
    _rows_by_id: Dict[Union[str, UUID], Row] = PrivateAttr(default={})
    _template_name = 'subexp_summary.html'

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.SUB_EXPERIMENT_SUMMARY

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'subexpSummary'

    def __getitem__(self, index: Union[int, str, UUID]) -> Row:
        if not self._rows:
            self._reload_cells()

        if isinstance(index, int):
            return self._rows[index]

        if isinstance(index, str):
            try:
                return self._rows_by_id[UUID(index)]
            except ValueError:
                return self._rows_by_id[index]

        if isinstance(index, UUID):
            return self._rows_by_id[index]

        raise IndexError('Invalid index')

    def __iter__(self):
        if not self._rows:
            self._reload_cells()
        return self._rows.__iter__()

    def _reload_cells(self):
        api = SignalsNotebookApi.get_default_api()
        log.debug('Reloading data in Table: %s...', self.eid)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, 'rows'),
        )

        result = SubExpSummaryResponse(**response.json())  # type: ignore
        cells = [cast(ResponseData, item).body for item in result.data]

        self._rows = []
        self._rows_by_id = {}

        for item in cells:
            subexp_row = cast(Row, item)
            assert subexp_row.id

            self._rows.append(subexp_row)
            self._rows_by_id[subexp_row.id] = subexp_row

    # def save(self, force: bool = True) -> None:
    #     api = SignalsNotebookApi.get_default_api()
    #
    #     request_body = []
    #     for item in self._cells:
    #         if item.is_changed:
    #             request_body.append(item.representation_for_update.dict(exclude_none=True))
    #
    #     if not request_body:
    #         return
    #
    #     api.call(
    #         method='PATCH',
    #         path=(self._get_samples_endpoint(), self.eid, 'properties'),
    #         params={
    #             'force': json.dumps(force),
    #             'value': 'normalized',
    #         },
    #         json={
    #             'data': {'attributes': {'data': request_body}},
    #         },
    #     )
    #     self._reload_cells()