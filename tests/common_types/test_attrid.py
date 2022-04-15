import pytest
from pydantic import BaseModel

from signals_notebook.common_types import AttrID, ObjectType
from signals_notebook.exceptions import EIDError


class Model(BaseModel):
    id: AttrID


@pytest.mark.parametrize(
    'input_data',
    [
        'attribute',
        'attribute:',
        'batch:8682fa324cd24z'
        '',
        1,
    ],
)
def test_incorrect_data(input_data):
    with pytest.raises(EIDError) as e:
        AttrID(input_data)

    assert str(e.value) == f'incorrect EID value: "{input_data}"'


@pytest.mark.parametrize(
    'input_data,_type,_id',
    [
        (
            'attribute:42',
            ObjectType.ATTRIBUTE,
            42,
        ),
    ],
)
def test_correct_data(input_data, _type, _id):
    eid = AttrID(input_data)

    assert eid.id == _id
    assert eid.type == _type


def test_pydantic_validation():
    data = {
        'id': 'attribute:34',
    }

    model = Model(**data)

    assert model.id == AttrID(data['id'])
    assert isinstance(model.id, AttrID)
