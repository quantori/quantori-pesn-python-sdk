from typing import TypeVar, Generic, Optional
from pydantic.generics import GenericModel

from signals_notebook.common_types import EntityType

CellContentType = TypeVar('CellContentType')


class CellPropertyContent(GenericModel, Generic[CellContentType]):
    value: CellContentType
    type: Optional[EntityType] = None
