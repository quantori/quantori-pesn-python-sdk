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

    @property
    def representation_for_update(self):
        return {self.key: {'content': {'value': self.value}}}
