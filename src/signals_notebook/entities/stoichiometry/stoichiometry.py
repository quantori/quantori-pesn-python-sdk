import abc
import cgi
from itertools import chain
from typing import cast, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import EID, File, Response, ResponseData
from signals_notebook.entities.stoichiometry.cell import ColumnDefinition, ColumnDefinitions
from signals_notebook.entities.stoichiometry.data_grid import (
    Condition,
    DataGridKind,
    DataGrids,
    Product,
    Reactant,
    Row,
    Solvent,
)


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class StoichiometryDataResponse(Response[DataGrids]):
    pass


class Stoichiometry(BaseModel, abc.ABC):
    eid: EID = Field(default=None)
    reactants: list[Reactant] = Field(default=[])
    products: list[Product] = Field(default=[])
    solvents: list[Solvent] = Field(default=[])
    conditions: list[Condition] = Field(default=[])
    _stoichiometry_rows: list[Row] = PrivateAttr(default=[])
    _stoichiometry_rows_by_id: dict[Union[int, UUID], Row] = PrivateAttr(default={})

    @classmethod
    def _get_stoichiometry_endpoint(cls) -> str:
        return 'stoichiometry'

    def fetch_stoichiometry_data(self) -> None:
        api = SignalsNotebookApi.get_default_api()
        fields = ', '.join(DataGridKind)

        response = api.call(
            method='GET',
            path=(self._get_stoichiometry_endpoint(), self.eid),
            params={'fields': fields, 'value': 'normalized'},
        )

        result = StoichiometryDataResponse(**response.json())
        body = cast(ResponseData, result.data).body

        self._stoichiometry_rows = []
        self._stoichiometry_rows_by_id = {}
        self.reactants = getattr(body, DataGridKind.REACTANTS, [])
        self.products = getattr(body, DataGridKind.PRODUCTS, [])
        self.solvents = getattr(body, DataGridKind.SOLVENTS, [])
        self.conditions = getattr(body, DataGridKind.CONDITIONS, [])

        for row in chain(self.reactants, self.products, self.solvents, self.conditions):
            assert row.row_id
            self._stoichiometry_rows.append(row)
            self._stoichiometry_rows_by_id[row.row_id] = row

    def get_stoichiometry_row_by_id(self, row_id: Union[int, str, UUID]) -> Row:
        if not self._stoichiometry_rows_by_id:
            self.fetch_stoichiometry_data()

        if isinstance(row_id, str):
            return self._stoichiometry_rows_by_id[UUID(row_id)]

        return self._stoichiometry_rows_by_id[row_id]

    def fetch_structure(self, row_id: Union[int, str, UUID], format: Optional[str] = None) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_stoichiometry_endpoint(), self.eid, str(row_id), 'structure'),
            params={'format': format},
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params.get('filename', ''),
            content=response.content,
            content_type=response.headers.get('content-type', ''),
        )

    def get_column_definitions_list(
        self, entity_eid: Union[EID, str], data_grid_kind: DataGridKind
    ) -> list[ColumnDefinition]:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET', path=(self._get_stoichiometry_endpoint(), entity_eid, 'columns', data_grid_kind)
        )

        result = ColumnDefinitionsResponse(**response.json())
        body = cast(ResponseData, result.data).body

        return getattr(body, data_grid_kind, [])

    def get_column_definitions_map(
        self, entity_eid: Union[EID, str], data_grid_kind: DataGridKind
    ) -> dict[str, ColumnDefinition]:
        column_definitions = self.get_column_definitions_list(entity_eid=entity_eid, data_grid_kind=data_grid_kind)
        column_definitions_map: dict[str, ColumnDefinition] = {}

        for column_definition in column_definitions:
            column_definitions_map[str(column_definition.key)] = column_definition
            column_definitions_map[column_definition.title] = column_definition

        return column_definitions_map
