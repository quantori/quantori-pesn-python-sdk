from typing import Generic, Optional, TypeVar, Union

from pydantic import PrivateAttr
from pydantic.generics import GenericModel

SubExperimentSummaryCellValueType = TypeVar('SubExperimentSummaryCellValueType')


class SubExperimentSummaryCell(GenericModel, Generic[SubExperimentSummaryCellValueType]):
    key: Optional[str]
    display: Optional[str]
    value: Optional[Union[str, int]]
    _changed: bool = PrivateAttr(default=False)

    def set_value(self, new_value: SubExperimentSummaryCellValueType) -> None:
        self.value = new_value
        self._changed = True

    @property
    def is_changed(self) -> bool:
        return self._changed

#
# class Content(BaseModel):
#     columns: Optional[SubExperimentSummaryCell]
#
#
# class SubExperimentSummaryCellBody(BaseModel):
#     id: Optional[Union[UUID, str]]
#     type: # str = ObjectType.SUB_EXPERIMENT
#     attributes: Content


# class SubExperimentSummaryCell(BaseModel):
#     id: Optional[Union[UUID, str]]
#     columns: List[SubExperimentSummaryCellContent] = Field(default=SubExperimentSummaryCellContent())
#
#     def set_content_value(self, new_value: SubExperimentSummaryCellValueType) -> None:
#         self.content.set_value(new_value)
#
#     def set_content_values(self, new_values: List[SubExperimentSummaryCellValueType]) -> None:
#         self.content.set_values(new_values)
#
#     def set_content_name(self, new_name: str) -> None:
#         self.content.set_name(new_name)
#
#     @property
#     def content_value(self) -> Optional[SubExperimentSummaryCellValueType]:
#         return self.content.value
#
#     @property
#     def content_values(self) -> Optional[List[SubExperimentSummaryCellValueType]]:
#         return self.content.values
#
#     @property
#     def content_name(self) -> Optional[str]:
#         return self.content.name
#
#     @property
#     def is_changed(self) -> bool:
#         return False if self.content is None else self.content.is_changed
#
#     @property
#     def representation_for_update(self) -> SubExperimentSummaryCellBody:
#         return SubExperimentSummaryCellBody(id=str(self.id), attributes=Content(content=self.content))
