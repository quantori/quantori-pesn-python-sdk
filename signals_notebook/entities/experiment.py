from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field

from signals_notebook.entities.entity import Entity
from signals_notebook.types import EntitySubtype


class ExperimentState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class Experiment(Entity):
    name: str
    description: str
    created_at: datetime = Field(alias='createdAt')
    edited_at: datetime = Field(alias='editedAt')
    state: Optional[ExperimentState] = None

    @classmethod
    def get_subtype(cls) -> EntitySubtype:
        return EntitySubtype.EXPERIMENT
