from typing import Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.generics import GenericModel

from signals_notebook.common_types import EID, ObjectType

CellValueType = TypeVar('CellValueType')


class SampleCellContent(GenericModel, Generic[CellValueType]):
    value: Optional[CellValueType]
    name: Optional[str]
    eid: Optional[EID]
    values: Optional[List[CellValueType]]
    display: Optional[str]
    units: Optional[str]
    _changed: bool = PrivateAttr(default=False)

    def _set_value(self, new_value: CellValueType) -> None:
        """Set new value

        Args:
            new_value: new value for value field

        Returns:

        """
        self.value = new_value
        self._changed = True

    def _set_values(self, new_values: List[CellValueType]) -> None:
        """Set new values

        Args:
            new_values: new list of values for values field

        Returns:

        """
        self.values = new_values
        self._changed = True

    def _set_name(self, new_name: str) -> None:
        """Set new name

        Args:
            new_name: new name for name field

        Returns:

        """
        self.name = new_name
        self._changed = True

    @property
    def is_changed(self) -> bool:
        """Get is_changed value

        Returns:
            bool: True/False
        """
        return self._changed


class Content(BaseModel):
    content: Optional[SampleCellContent]


class SampleCellBody(BaseModel):
    id: Optional[Union[UUID, str]]
    type: str = ObjectType.PROPERTY
    attributes: Content


class SampleCell(BaseModel):
    id: Optional[str]
    name: Optional[str]
    content: SampleCellContent = Field(default=SampleCellContent())
    read_only: Optional[bool] = False

    def _is_cell_mutable(self):
        if self.name == 'Amount':
            raise TypeError('Property is immutable')
        if self.read_only:
            raise TypeError('Cell is read only')

    def set_content_value(self, new_value: CellValueType) -> None:
        """Set new content value

        Args:
            new_value: new value of SampleCellContent value field

        Returns:

        """
        self._is_cell_mutable()
        self.content._set_value(new_value)

    def set_content_values(self, new_values: List[CellValueType]) -> None:
        """Set new content values

        Args:
            new_values: new list of values of SampleCellContent values field

        Returns:

        """
        self._is_cell_mutable()
        self.content._set_values(new_values)

    def set_content_name(self, new_name: str) -> None:
        """Set new content name

        Args:
            new_name: new name of SampleCellContent name field

        Returns:

        """
        self._is_cell_mutable()
        self.content._set_name(new_name)

    @property
    def content_value(self) -> Optional[CellValueType]:
        """Get content value

        Returns:
            Optional[CellValueType]
        """
        return self.content.value

    @property
    def content_values(self) -> Optional[List[CellValueType]]:
        """Get content values

        Returns:
            Optional[List[CellValueType]]
        """
        return self.content.values

    @property
    def content_name(self) -> Optional[str]:
        """Get content name

        Returns:
            Optional[str]
        """
        return self.content.name

    @property
    def is_changed(self) -> bool:
        """Checking if SampleCell has been modified

        Returns:
            bool
        """
        return False if self.content is None else self.content.is_changed

    @property
    def representation_for_update(self) -> SampleCellBody:
        """Get representation of body for update

        Returns:
            SampleCellBody
        """
        return SampleCellBody(
            id=str(self.id), attributes=Content(content=self.content.dict(include={'value', 'values', 'name'}))
        )
