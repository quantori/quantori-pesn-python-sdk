import json

import arrow
import pytest

from signals_notebook.common_types import ChemicalDrawingFormat, EntityType, File, ObjectType
from signals_notebook.entities import ChemicalDrawing, Entity
from signals_notebook.entities.chemical_drawing import ChemicalStructure, ChemicalDrawingPosition, Structure


@pytest.fixture()
def get_response(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


@pytest.fixture()
def templates():
    return {
        'links': {
            'self': 'https://ex.com/api/rest/v1.0/entities'
            '?includeTypes=chemicalDrawing&includeOptions=template&page[offset]=0&page[limit]=20',
            'first': 'https://ex.com/api/rest/v1.0/entities'
            '?includeTypes=chemicalDrawing&includeOptions=template&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'chemicalDrawing:a530ffb5-1e31-4ee6-8138-5e12fc62959f',
                'links': {
                    'self': 'https://ex.com/api/rest/v1.0/entities/chemicalDrawing:a530ffb5-1e31-4ee6-8138-5e12fc62959f'
                },
                'attributes': {
                    'id': 'chemicalDrawing:a530ffb5-1e31-4ee6-8138-5e12fc62959f',
                    'eid': 'chemicalDrawing:a530ffb5-1e31-4ee6-8138-5e12fc62959f',
                    'name': 'DEFAULT_CHEMICALDRAWING',
                    'description': '',
                    'createdAt': '2021-10-22T13:36:02.942Z',
                    'editedAt': '2022-07-16T10:21:09.015Z',
                    'type': 'chemicalDrawing',
                    'digest': '62677800',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'DEFAULT_CHEMICALDRAWING'}},
                    'flags': {'canEdit': True},
                },
            }
        ],
    }


@pytest.fixture()
def chemical_drawing_stoichiometry_mock(mocker):
    return mocker.patch('signals_notebook.entities.ChemicalDrawing.stoichiometry')


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
@pytest.mark.parametrize(
    'entity_class, entity_type, content_type, file_extension',
    [
        (ChemicalDrawing, EntityType.CHEMICAL_DRAWING, 'chemical/x-cdxml', 'cdxml'),
    ],
)
def test_create(
    api_mock, experiment_factory, eid_factory, digest, force, entity_class, entity_type, content_type, file_extension
):
    container = experiment_factory(digest=digest)
    eid = eid_factory(type=entity_type)
    file_name = 'chemDraw'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': entity_type,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = ChemicalDrawing.create(
        container=container, name=file_name, content_type=content_type, content=content, force=force
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.{file_extension}'),
        params={
            'digest': container.digest,
            'force': 'true' if force else 'false',
        },
        headers={
            'Content-Type': content_type,
        },
        data=content,
    )

    assert isinstance(result, entity_class)
    assert result.eid == eid
    assert result.digest == response['data']['attributes']['digest']
    assert result.name == response['data']['attributes']['name']
    assert result.created_at == arrow.get(response['data']['attributes']['createdAt'])
    assert result.edited_at == arrow.get(response['data']['attributes']['editedAt'])


@pytest.mark.parametrize(
    'structure_type, positions, reaction_type',
    [
        (
            ChemicalStructure.REACTANT,
            ChemicalDrawingPosition.REACTANTS,
            ObjectType.REACTION_REACTANT,
        ),
        (
            ChemicalStructure.PRODUCT,
            ChemicalDrawingPosition.PRODUCTS,
            ObjectType.REACTION_REACTANT,
        ),
        (
            ChemicalStructure.REAGENT,
            ChemicalDrawingPosition.REAGENTS,
            ObjectType.REACTION_REACTANT,
        ),
    ],
)
def test_get_structures(
    chemical_drawing_factory, structure_factory, api_mock, structure_type, positions, reaction_type
):
    structure = structure_factory(id=1, type=structure_type)
    chemical_drawing = chemical_drawing_factory()

    response = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/reactants'},
        'data': [
            {
                'type': reaction_type,
                'id': structure.id,
                'attributes': {
                    'type': structure.type,
                    'id': structure.id,
                    'inchi': structure.inchi,
                    'cdxml': structure.cdxml,
                },
            }
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result = chemical_drawing.get_structures(positions=positions)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('chemicaldrawings', chemical_drawing.eid, 'reaction', positions),
    )

    assert isinstance(result, list)
    assert result[0].id == structure.id
    assert result[0].inchi == structure.inchi
    assert result[0].cdxml == structure.cdxml


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
@pytest.mark.parametrize(
    'structure_type, positions, reaction_type, data_type, data',
    [
        (
            ChemicalStructure.REACTANT,
            ChemicalDrawingPosition.REACTANTS,
            ObjectType.REACTION_REACTANT,
            'inchi',
            'InChI=1S/C3H8/c1-3-2/h3H2,1-2H3',
        ),
        (
            ChemicalStructure.PRODUCT,
            ChemicalDrawingPosition.PRODUCTS,
            ObjectType.REACTION_REACTANT,
            'cdxml',
            '<?xml version=1.0',
        ),
        (
            ChemicalStructure.REAGENT,
            ChemicalDrawingPosition.REAGENTS,
            ObjectType.REACTION_REACTANT,
            'inchi',
            'InChI=1S/C3H8/c1-3-2/h3H2,1-2H3',
        ),
    ],
)
def test_add_structures(
    api_mock,
    chemical_drawing_factory,
    structure_factory,
    digest,
    force,
    structure_type,
    positions,
    reaction_type,
    data_type,
    data,
):
    chemical_drawing = chemical_drawing_factory()
    structure = structure_factory(id=1, type=structure_type)

    if data_type == 'inchi':
        structure.inchi = data
    else:
        structure.cdxml = data
    response = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/products'},
        'data': {
            'type': reaction_type,
            'id': structure.id,
            'attributes': {
                'type': structure.type,
                'id': structure.id,
                'inchi': structure.inchi,
                'cdxml': structure.cdxml,
            },
        },
    }
    api_mock.call.return_value.json.return_value = response

    result = chemical_drawing.add_structures(structure=structure, positions=positions, digest=digest, force=force)

    request_body = {
        'data': {
            'attributes': {'dataType': data_type, 'data': data},
        }
    }

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('chemicaldrawings', chemical_drawing.eid, 'reaction', positions),
        params={
            'digest': digest,
            'force': 'true' if force else 'false',
        },
        json=request_body,
    )
    assert isinstance(result, Structure)
    assert result.id == structure.id
    assert result.inchi == structure.inchi
    assert result.cdxml == structure.cdxml


def test_get_content(chemical_drawing_factory, api_mock):
    chemical_drawing = chemical_drawing_factory()
    file_name = 'chemDraw.cdxml'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    content_type = 'chemical/x-cdxml'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = chemical_drawing.get_content(format=ChemicalDrawingFormat.CDXML)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', chemical_drawing.eid, 'export'),
        params={
            'format': ChemicalDrawingFormat.CDXML,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(api_mock, chemical_drawing_stoichiometry_mock, chemical_drawing_factory, snapshot):
    chemical_drawing = chemical_drawing_factory(name='name')
    file_name = 'chemDraw.cdxml'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    content_type = 'chemical/x-cdxml'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content
    chemical_drawing_stoichiometry_mock.return_value = []

    chemical_drawing_html = chemical_drawing.get_html()

    snapshot.assert_match(chemical_drawing_html)


def test_dump_not_empty_chemical_drawing(api_mock, mocker, chemical_drawing_factory, structure_factory, get_response):
    chemical_drawing = chemical_drawing_factory(name='name')
    file_name = 'chemDraw.cdxml'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    content_type = 'chemical/x-cdxml'


    structure_reactant = structure_factory(
        id=1, type=ChemicalStructure.REACTANT, inchi='InChI=1S/C3H8', cdxml='<?xml version=1.0'
    )
    structure_product = structure_factory(
        id=2, type=ChemicalStructure.PRODUCT, inchi='InChI=1S/C3H8', cdxml='<?xml version=1.0'
    )
    structure_reagent = structure_factory(
        id=3, type=ChemicalStructure.REAGENT, inchi='InChI=1S/C3H8', cdxml='<?xml version=1.0'
    )

    response_reactants = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/reactants'},
        'data': [
            {
                'type': ObjectType.REACTION_REACTANT,
                'id': structure_reactant.id,
                'attributes': {
                    'type': structure_reactant.type,
                    'id': structure_reactant.id,
                    'inchi': structure_reactant.inchi,
                    'cdxml': structure_reactant.cdxml,
                },
            }
        ],
    }
    response_reagents = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/reagents'},
        'data': [
            {
                'type': ObjectType.REACTION_REAGENT,
                'id': structure_reagent.id,
                'attributes': {
                    'type': structure_reagent.type,
                    'id': structure_reagent.id,
                    'inchi': structure_reagent.inchi,
                    'cdxml': structure_reagent.cdxml,
                },
            }
        ],
    }
    response_products = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/products'},
        'data': [
            {
                'type': ObjectType.REACTION_PRODUCT,
                'id': structure_product.id,
                'attributes': {
                    'type': structure_product.type,
                    'id': structure_product.id,
                    'inchi': structure_product.inchi,
                    'cdxml': structure_product.cdxml,
                },
            }
        ],
    }
    content_response = get_response({})
    content_response.content = content
    content_response.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }

    api_mock.call.side_effect = [
        content_response,
        get_response(response_reactants),
        get_response(response_products),
        get_response(response_reagents),
    ]
    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'content_type': content_type,
        **{k: v for k, v in chemical_drawing.dict().items() if k in ('name', 'description', 'eid')},
        'reactants': [
            {'id': structure_reactant.id, 'inchi': structure_reactant.inchi, 'cdxml': structure_reactant.cdxml},
        ],
        'products': [{'id': structure_product.id, 'inchi': structure_product.inchi, 'cdxml': structure_product.cdxml}],
        'reagents': [{'id': structure_reagent.id, 'inchi': structure_reagent.inchi, 'cdxml': structure_reagent.cdxml}],

    }

    chemical_drawing.dump(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, chemical_drawing.eid, 'metadata.json')
    join_path_call_2 = mocker.call(base_path, chemical_drawing.eid, file_name)

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
        ],
        any_order=True,
    )
    fs_handler_mock.write.assert_has_calls(
        [
            mocker.call(fs_handler_mock.join_path(), json.dumps(metadata)),
            mocker.call(fs_handler_mock.join_path(), content),
        ],
        any_order=True,
    )


def test_dump_empty_chemical_drawing(api_mock, mocker, chemical_drawing_factory, structure_factory, get_response):
    file_name = 'chemDraw.cdxml'
    content = b'<CDXML />'
    content_type = 'chemical/x-cdxml'

    content_response = get_response({})
    content_response.content = content
    content_response.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }

    api_mock.call.side_effect = [
        content_response,
    ]
    fs_handler_mock = mocker.MagicMock()

    fs_handler_mock.join_path.assert_not_called()
    fs_handler_mock.write.assert_not_called()



@pytest.mark.parametrize(
    'entity_class, entity_type, content_type, file_extension',
    [
        (ChemicalDrawing, EntityType.CHEMICAL_DRAWING, 'chemical/x-cdxml', 'cdxml'),
    ],
)
def test_load(
    api_mock, experiment_factory, eid_factory, mocker, entity_class, entity_type, content_type, file_extension
):
    container = experiment_factory()
    eid = eid_factory(type=entity_type)
    file_name = 'chemDraw'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    response = {
        'links': {'self': f'https://example.com/{eid}'},
        'data': {
            'type': ObjectType.ENTITY,
            'id': eid,
            'attributes': {
                'eid': eid,
                'name': file_name,
                'description': '',
                'type': entity_type,
                'createdAt': '2019-09-06T03:12:35.129Z',
                'editedAt': '2019-09-06T15:22:47.309Z',
                'digest': '222',
            },
        },
    }

    fs_handler_mock = mocker.MagicMock()
    base_path = './'
    metadata = {
        'file_name': file_name,
        'name': file_name,
        'content_type': content_type,
    }
    api_mock.call.return_value.json.return_value = response
    fs_handler_mock.read.side_effect = [json.dumps(metadata), content]
    fs_handler_mock.join_path.side_effect = [base_path + 'metadata.json', base_path + file_name]

    ChemicalDrawing.load(path=base_path, fs_handler=fs_handler_mock, parent=container)

    fs_handler_mock.join_path.assert_has_calls(
        [
            mocker.call(base_path, 'metadata.json'),
            mocker.call(base_path, file_name),
        ],
        any_order=True,
    )

    fs_handler_mock.read.assert_has_calls(
        [
            mocker.call(base_path + 'metadata.json'),
            mocker.call(base_path + file_name),
        ],
        any_order=True,
    )

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('entities', container.eid, 'children', f'{file_name}.{file_extension}'),
        params={
            'digest': None,
            'force': 'true',
        },
        headers={
            'Content-Type': content_type,
        },
        data=content,
    )


def test_dump_templates(api_mock, mocker, chemical_drawing_factory, templates, structure_factory, get_response):
    chemical_drawing = chemical_drawing_factory(name='name')
    file_name = 'chemDraw.cdxml'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    content_type = 'chemical/x-cdxml'

    structure_reactant = structure_factory(
        id=1, type=ChemicalStructure.REACTANT, inchi='InChI=1S/C3H8', cdxml='<?xml version=1.0'
    )
    structure_product = structure_factory(
        id=2, type=ChemicalStructure.PRODUCT, inchi='InChI=1S/C3H8', cdxml='<?xml version=1.0'
    )
    structure_reagent = structure_factory(
        id=3, type=ChemicalStructure.REAGENT, inchi='InChI=1S/C3H8', cdxml='<?xml version=1.0'
    )

    response_reactants = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/reactants'},
        'data': [
            {
                'type': ObjectType.REACTION_REACTANT,
                'id': structure_reactant.id,
                'attributes': {
                    'type': structure_reactant.type,
                    'id': structure_reactant.id,
                    'inchi': structure_reactant.inchi,
                    'cdxml': structure_reactant.cdxml,
                },
            }
        ],
    }
    response_reagents = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/reagents'},
        'data': [
            {
                'type': ObjectType.REACTION_REAGENT,
                'id': structure_reagent.id,
                'attributes': {
                    'type': structure_reagent.type,
                    'id': structure_reagent.id,
                    'inchi': structure_reagent.inchi,
                    'cdxml': structure_reagent.cdxml,
                },
            }
        ],
    }
    response_products = {
        'links': {'self': f'https://example.com/chemicaldrawings/{chemical_drawing.eid}/reaction/products'},
        'data': [
            {
                'type': ObjectType.REACTION_PRODUCT,
                'id': structure_product.id,
                'attributes': {
                    'type': structure_product.type,
                    'id': structure_product.id,
                    'inchi': structure_product.inchi,
                    'cdxml': structure_product.cdxml,
                },
            }
        ],
    }
    content_response = get_response({})
    content_response.content = content
    content_response.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }

    api_mock.call.side_effect = [
        get_response(templates),
        content_response,
        get_response(response_reactants),
        get_response(response_products),
        get_response(response_reagents),

    ]
    fs_handler_mock = mocker.MagicMock()

    template_eid = templates['data'][0]['id']
    base_path = './'
    metadata = {
        'file_name': file_name,
        'content_type': content_type,
        'eid': template_eid,
        'name': 'DEFAULT_CHEMICALDRAWING',
        'description': '',
    }

    chemical_drawing.dump_templates(base_path=base_path, fs_handler=fs_handler_mock)

    join_path_call_1 = mocker.call(base_path, 'templates', chemical_drawing.type)
    join_path_call_2 = mocker.call(fs_handler_mock.join_path(), template_eid, file_name)
    join_path_call_3 = mocker.call(fs_handler_mock.join_path(), template_eid, 'metadata.json')

    fs_handler_mock.join_path.assert_has_calls(
        [
            join_path_call_1,
            join_path_call_2,
            join_path_call_3,
        ],
        any_order=True,
    )
