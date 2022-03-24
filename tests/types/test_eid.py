from uuid import UUID

import pytest
from pydantic import BaseModel

from signals_notebook.exceptions import EIDError
from signals_notebook.types import EID, EntityType


class Model(BaseModel):
    eid: EID


@pytest.mark.parametrize(
    'input_data',
    [
        'text',
        'text:',
        'text:vjarjhfwvqq',
        '',
    ],
)
def test_incorrect_data(input_data):
    with pytest.raises(EIDError) as e:
        EID(input_data)

    assert str(e.value) == f'incorrect EID value: "{input_data}"'


@pytest.mark.parametrize(
    'input_data,_type,_id',
    [
        (
            'text:3415fc40-4d11-45a1-ad63-b89ae08125c7',
            EntityType.TEXT,
            UUID(
                '3415fc40-4d11-45a1-ad63-b89ae08125c7',
            ),
        ),
        (
            'unknown:3415fc40-4d11-45a1-ad63-b89ae08125c7',
            'unknown',
            UUID(
                '3415fc40-4d11-45a1-ad63-b89ae08125c7',
            ),
        ),
    ],
)
def test_correct_data(input_data, _type, _id):
    eid = EID(input_data)

    assert eid.id == _id
    assert eid.type == _type


def test_pydantic_validation():
    data = {
        'eid': 'text:3415fc40-4d11-45a1-ad63-b89ae08125c7',
    }

    model = Model(**data)

    assert model.eid == EID(data['eid'])
    assert isinstance(model.eid, EID)
