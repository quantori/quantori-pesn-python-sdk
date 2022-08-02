import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.entities.parallel_experiment.cell import SubExperimentSummaryCell

log = logging.getLogger(__name__)


class Row(BaseModel):
    id: Optional[Union[UUID, str]]
    cells: Optional[List[SubExperimentSummaryCell]] = Field(alias='columns')
    _cells_dict: Dict[Union[UUID, str], SubExperimentSummaryCell] = PrivateAttr(default={})

    class Config:
        validate_assignment = True

    def __init__(self, **data):
        super().__init__(**data)

        for cell in self.cells:
            self._cells_dict[cell.key] = cell

    def get(self, value: Union[str, UUID], default: Any = None) -> Union[SubExperimentSummaryCell, Any]:
        """Get one of the cells

        Args:
            value: key to get one of the cells
            default: default value if key doesn't exist

        Returns:
            Union[Cell, Any]
        """
        try:
            return self[value]
        except KeyError:
            log.debug('KeyError were caught. Default value returned')
            return default

    @property
    def is_changed(self) -> bool:
        """Get is_changed field

        Returns:
            bool: True/False
        """
        return any([cell.is_changed for cell in self.cells])

    def __getitem__(self, index: str) -> SubExperimentSummaryCell:
        if isinstance(index, str):
            if index in self._cells_dict:
                return self._cells_dict[index]

        log.exception('IndexError were caught. Invalid index')
        raise IndexError('Invalid index')

    def __iter__(self):
        return self.cells.__iter__()
