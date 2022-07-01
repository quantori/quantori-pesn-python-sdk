from typing import Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.generics import GenericModel

from signals_notebook.common_types import EID, ObjectType

CellValueType = TypeVar('CellValueType')


class TaskCellContent(GenericModel, Generic[CellValueType]):
    value: Optional[CellValueType]
    name: Optional[str]
    eid: Optional[EID]
    values: Optional[List[CellValueType]]
    _changed: bool = PrivateAttr(default=False)

    def set_value(self, new_value: CellValueType) -> None:
        """Set new value

        Args:
            new_value: new value of Property value field

        Returns:

        """
        self.value = new_value
        self._changed = True

    def set_values(self, new_values: List[CellValueType]) -> None:
        """Set new values

        Args:
            new_values: new list of values of Property values field

        Returns:

        """
        self.values = new_values
        self._changed = True

    def set_name(self, new_name: str) -> None:
        """Set new name

        Args:
            new_name: new name of Property name field

        Returns:

        """
        self.name = new_name
        self._changed = True

    @property
    def is_changed(self) -> bool:
        """Checking if content of Cell has been modified

        Returns:
            bool
        """
        return self._changed


class Content(BaseModel):
    content: Optional[TaskCellContent]


class TaskCellBody(BaseModel):
    id: Optional[Union[UUID, str]]
    type: str = ObjectType.PROPERTY
    attributes: Content


class TaskCell(BaseModel):
    id: Optional[Union[UUID, str]]
    name: Optional[str]
    content: TaskCellContent = Field(default=TaskCellContent())

    def set_content_value(self, new_value: CellValueType) -> None:
        """Set new content value

        Args:
            new_value: new value of Property value field

        Returns:

        """
        self.content.set_value(new_value)

    def set_content_values(self, new_values: List[CellValueType]) -> None:
        """Set new content values

        Args:
            new_values: new list of values of Property values field

        Returns:

        """
        self.content.set_values(new_values)

    def set_content_name(self, new_name: str) -> None:
        """Set new content name

        Args:
            new_name: new name of content name field

        Returns:

        """
        self.content.set_name(new_name)

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
        """Checking if Property has been modified

        Returns:
            bool
        """
        return False if self.content is None else self.content.is_changed

    @property
    def representation_for_update(self) -> TaskCellBody:
        """Get representation of body for update

        Returns:
            TaskCellBody
        """
        return TaskCellBody(id=str(self.id), attributes=Content(content=self.content))
