from signals_notebook.common_types import ChemicalDrawingFormat, File, MaterialType, MID


def test_library_property(batch_factory, library_factory, mocker):
    library = library_factory()

    mock = mocker.patch('signals_notebook.materials.material_store.MaterialStore')
    mock.get.return_value = library

    batch = batch_factory(_library=None)

    result = batch.library

    assert result == library
    mock.get.assert_called_once_with(MID(f'{MaterialType.LIBRARY}:{batch.asset_type_id}'))


def test_get_chemical_drawing(batch_factory, api_mock):
    batch = batch_factory()

    file_name = 'batch.cdxml'
    content = b'<?xml version="1.0" encoding="UTF-8" ?>'
    content_type = 'chemical/x-cdxml'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = batch.get_chemical_drawing(format=ChemicalDrawingFormat.CDXML)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('materials', batch.eid, 'drawing'),
        params={
            'format': ChemicalDrawingFormat.CDXML,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_image(batch_factory, api_mock):
    batch = batch_factory()

    file_name = 'PKI-000001-0001.dna'
    content = b'PNG'
    content_type = 'image/png'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = batch.get_image()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('materials', batch.eid, 'image'),
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_bio_sequence(batch_factory, api_mock):
    batch = batch_factory()

    file_name = 'PKI-000001-0001.dna'
    content = b'GGA TCC ATG GCC CTG TGG ATG CG'
    content_type = 'application/vnd.snapgene.dna'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = batch.get_bio_sequence()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('materials', batch.eid, 'bioSequence'),
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type
