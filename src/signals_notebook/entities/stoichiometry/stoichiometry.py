import abc
import cgi
from typing import cast, Optional, Union

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ChemicalDrawingFormat, EID, File, Response, ResponseData
from signals_notebook.entities.stoichiometry.cell import ColumnDefinitions
from signals_notebook.entities.stoichiometry.data_grid import (
    Conditions,
    DataGridKind,
    DataGrids,
    Products,
    Reactants,
    Solvents,
)


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class StoichiometryDataResponse(Response[DataGrids]):
    pass


class Stoichiometry(BaseModel, abc.ABC):
    eid: EID = Field(allow_mutation=False)
    reactants: Reactants = Field(default=[])
    products: Products = Field(default=[])
    solvents: Solvents = Field(default=[])
    conditions: Conditions = Field(default=[])

    class Config:
        validate_assignment = True

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'stoichiometry'

    @classmethod
    def _get_stoichiometry(cls, data: ResponseData) -> 'Stoichiometry':
        body = cast(DataGrids, data.body)
        stoichiometry = Stoichiometry(
            eid=data.eid,
            reactants=body.reactants,
            products=body.products,
            solvents=body.solvents,
            conditions=body.conditions,
        )

        return stoichiometry

    @classmethod
    def fetch_data(cls, entity_eid: EID) -> Union['Stoichiometry', list['Stoichiometry']]:
        api = SignalsNotebookApi.get_default_api()
        fields = ', '.join(DataGridKind)

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), entity_eid),
            params={'fields': fields, 'value': 'normalized'},
        )

        result = StoichiometryDataResponse(**response.json())
        data = cast(ResponseData, result.data)

        if isinstance(data, list):
            stoichiometry_list = []
            for item in data:
                stoichiometry = cls._get_stoichiometry(data=item)
                stoichiometry_list.append(stoichiometry)
            return stoichiometry_list
        else:
            stoichiometry = cls._get_stoichiometry(data=data)
            return stoichiometry

    def fetch_structure(self, row_id: str, format: Optional[ChemicalDrawingFormat] = None) -> File:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, row_id, 'structure'),
            params={'format': format},
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        return File(
            name=params.get('filename', ''),
            content=response.content,
            content_type=response.headers.get('content-type', ''),
        )
