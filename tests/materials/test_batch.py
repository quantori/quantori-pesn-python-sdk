from signals_notebook.types import MaterialType, MID


def test_library_property(batch_factory, library_factory, mocker):
    library = library_factory()
    batch = batch_factory()

    mock = mocker.patch('signals_notebook.materials.material_store.MaterialStore')
    mock.get.return_value = library

    result = batch.library

    assert result == library
    mock.get.assert_called_once_with(MID(f'{MaterialType.LIBRARY}:{batch.asset_type_id}'))
