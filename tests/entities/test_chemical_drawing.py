import arrow
import pytest

from signals_notebook.common_types import EntityType, File, ObjectType
from signals_notebook.entities import ChemicalDrawing, ChemicalDrawingFormat, Entity


@pytest.mark.parametrize('digest, force', [('111', False), (None, True)])
@pytest.mark.parametrize(
    'entity_class, entity_type, content_type, file_extension',
    [
        (ChemicalDrawing, EntityType.CHEMICAL_DRAWING, 'chemical/x-cdxml', 'cdxml'),
        (Entity, EntityType.UPLOADED_RESOURCE, 'image/svg+xml', 'svg'),
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
