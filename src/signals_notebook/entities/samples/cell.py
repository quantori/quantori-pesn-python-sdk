from typing import TypeVar, Generic, Optional
from pydantic.generics import GenericModel

from signals_notebook.common_types import EntityType, EID

CellContentType = TypeVar('CellContentType')


class CellPropertyContent(GenericModel, Generic[CellContentType]):
    value: Optional[CellContentType]
    type: Optional[EntityType] = None
    eid: Optional[EID]
    name: Optional[str]
