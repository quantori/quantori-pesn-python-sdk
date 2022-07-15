from signals_notebook.common_types import File


def test_get_content(material_table_factory, api_mock):
    materials_table = material_table_factory()
    file_name = 'Test.csv'
    content = b'Some text'
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = materials_table.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', materials_table.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(material_table_factory, snapshot, api_mock):
    material_table = material_table_factory(name='name')
    file_name = 'Test.csv'
    content = b'Some text'
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    material_table_html = material_table.get_html()

    snapshot.assert_match(material_table_html)
