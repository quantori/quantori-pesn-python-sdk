from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from signals_notebook.api import SignalsNotebookApi


class ExperimentState(str, Enum):
    OPEN = 'open'


class Experiment(BaseModel):
    eid: str
    name: str
    description: str
    created_at: datetime = Field(alias='createdAt')
    edited_at: datetime = Field(alias='editedAt')
    state: ExperimentState

    @classmethod
    def get(cls, eid: str) -> 'Experiment':
        api = SignalsNotebookApi.get_default_api()

    @classmethod
    def get_list(cls) -> List['Experiment']:
        pass

    @classmethod
    def delete_by_id(cls, eid: str) -> None:
        pass

    def delete(self) -> None:
        self.delete_by_id(self.eid)

    @classmethod
    def create(cls, **kwargs) -> 'Experiment':
        pass

    def update(self, **kwargs) -> None:
        pass
