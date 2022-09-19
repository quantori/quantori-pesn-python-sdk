import abc
import cgi
import logging
from typing import cast, ClassVar, Optional, Union

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import ChemicalDrawingFormat, EID, File, Response, ResponseData
from signals_notebook.entities.stoichiometry.cell import ColumnDefinition, ColumnDefinitions
from signals_notebook.entities.stoichiometry.data_grid import (
    Conditions,
    DataGridKind,
    DataGrids,
    Products,
    Reactants,
    Rows,
    Solvents,
)
from signals_notebook.jinja_env import env

log = logging.getLogger(__name__)


class ColumnDefinitionsResponse(Response[ColumnDefinitions]):
    pass


class StoichiometryDataResponse(Response[DataGrids]):
    pass


class Stoichiometry(BaseModel, abc.ABC):
    """Stoichiometry object of Signals Notebook"""

    eid: EID = Field(allow_mutation=False)
    reactants: Reactants = Field(default=Reactants(__root__=[]))
    products: Products = Field(default=Products(__root__=[]))
    solvents: Solvents = Field(default=Solvents(__root__=[]))
    conditions: Conditions = Field(default=Conditions(__root__=[]))
    _template_name: ClassVar = 'stoichiometry.html'

    class Config:
        validate_assignment = True

    @classmethod
    def set_template_name(cls, template_name: str) -> None:
        """Set new template name

        Args:
            template_name: name of the template (str)

        Returns:

        """
        log.debug('Setting new template for: %s...', cls.eid)
        cls._template_name = template_name
        log.debug('New template (%s) for %s was set', template_name, cls.eid)

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

        for grid_kind in DataGridKind:
            grid_kind = cast(DataGridKind, grid_kind)
            grid = getattr(stoichiometry, grid_kind.value)
            grid = cast(Rows, grid)
            column_definitions = stoichiometry.get_column_definitions(grid_kind)
            grid.set_column_definitions(column_definitions)

        return stoichiometry

    @classmethod
    def fetch_data(cls, entity_eid: EID) -> Union['Stoichiometry', list['Stoichiometry']]:
        """Fetch stoichiometry data of experiment or chemicalDrawing by entity_id.
        Accepted entity types: experiment, chemicalDrawing.

        Args:
            entity_eid: Unique entity identifier

        Returns:
            Stoichiometry object or list of Stoichiometry objects
        """
        api = SignalsNotebookApi.get_default_api()
        fields = ', '.join(DataGridKind)
        log.debug('Fetching data for: %s...', entity_eid)

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
            log.debug('Returned stoichiometry data as list for: %s.', entity_eid)
            return stoichiometry_list
        else:
            stoichiometry = cls._get_stoichiometry(data=data)
            log.debug('Returned a single stoichiometry for: %s.', entity_eid)

            return stoichiometry

    def fetch_structure(self, row_id: str, format: Optional[ChemicalDrawingFormat] = None) -> File:
        """Fetch structure of reactants/products. Accepted entity types: chemicalDrawing.

        Args:
            row_id: row_id of grid data.
            format: one of the ChemicalDrawingFormat formats

        Returns:
            File
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Fetching structure for: %s, using row: (%s)...', self.eid, row_id)

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.eid, row_id, 'structure'),
            params={'format': format},
        )

        content_disposition = response.headers.get('content-disposition', '')
        _, params = cgi.parse_header(content_disposition)

        log.debug('Return fetched structure as File for %s', self.eid)
        return File(
            name=params.get('filename', ''),
            content=response.content,
            content_type=response.headers.get('content-type', ''),
        )

    def get_column_definitions(self, data_grid_kind: DataGridKind) -> list[ColumnDefinition]:
        """Get column definitions of stoichiometry grid.

        Args:
            data_grid_kind (DataGridKind): kind of data grids in stoichiometry

        Returns:
            list of ColumnDefinition objects
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Getting column definitions for: %s...', self.eid)

        response = api.call(method='GET', path=(self._get_endpoint(), self.eid, 'columns', data_grid_kind))

        result = ColumnDefinitionsResponse(**response.json())
        body = cast(ResponseData, result.data).body

        log.debug('Column definitions for %s was returned', self.eid)
        return getattr(body, data_grid_kind, [])

    def get_html(self) -> str:
        """Get in HTML format

        Returns:
            Rendered template as a string
        """
        data = {
            'reactants_html': self.reactants.get_html(),
            'products_html': self.products.get_html(),
            'solvents_html': self.solvents.get_html(),
            'conditions_html': self.conditions.get_html(),
        }

        template = env.get_template(self._template_name)
        log.info('Html template for %s:%s has been rendered.', self.__class__.__name__, self.eid)

        return template.render(data=data)
