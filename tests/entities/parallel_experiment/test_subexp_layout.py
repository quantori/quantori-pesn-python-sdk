from signals_notebook.common_types import File


def test_get_content(sub_experiment_layout_factory, api_mock):
    sub_experiment_layout = sub_experiment_layout_factory()
    file_name = 'Test.csv'
    content = b'Plate,Well,Row,Column,Name\r\n'
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = sub_experiment_layout.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', sub_experiment_layout.eid, 'export'),
        params={
            'format': 'csv',
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(sub_experiment_layout_factory, snapshot, api_mock):
    sub_experiment_layout = sub_experiment_layout_factory(name='test')
    file_name = 'Test.csv'
    content = b'Plate,Well,Row,Column,Name\r\n'
    content_type = 'text/csv'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    material_table_html = sub_experiment_layout.get_html()

    snapshot.assert_match(material_table_html)
