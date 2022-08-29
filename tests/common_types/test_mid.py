import pytest
from pydantic import BaseModel

from signals_notebook.common_types import MaterialType, MID
from signals_notebook.exceptions import EIDError


class Model(BaseModel):
    eid: MID


@pytest.mark.parametrize(
    'input_data',
    [
        'asset',
        'asset:',
        'batch:8682fa324cd24z' '',
        'text:8682fa324cd24e',
        1,
    ],
)
def test_incorrect_data(input_data):
    with pytest.raises(EIDError) as e:
        MID(input_data)

    assert str(e.value) == f'incorrect EID value: "{input_data}"'


@pytest.mark.parametrize(
    'input_data,_type,_id',
    [
        (
            'asset:3415fc404d1145a1ad63b89ae08125c7',
            MaterialType.ASSET,
            '3415fc404d1145a1ad63b89ae08125c7',
        ),
        (
            'assetType:3415fc404d1145a1ad63b89ae08125c7',
            MaterialType.LIBRARY,
            '3415fc404d1145a1ad63b89ae08125c7',
        ),
        (
            'batch:3415fc404d1145a1ad63b89ae08125c7',
            MaterialType.BATCH,
            '3415fc404d1145a1ad63b89ae08125c7',
        ),
    ],
)
def test_correct_data(input_data, _type, _id):
    eid = MID(input_data)

    assert eid.id == _id
    assert eid.type == _type


def test_pydantic_validation():
    data = {
        'eid': 'asset:3415fc404d1145a1ad63b89ae08125c7',
    }

    model = Model(**data)

    assert model.eid == MID(data['eid'])
    assert isinstance(model.eid, MID)
