from uuid import UUID

import pytest

from signals_notebook.common_types import File
from signals_notebook.entities.plates.cell import PlateCell
from signals_notebook.entities.plates.plate_row import PlateRow


@pytest.fixture()
def plates_response():
    return {
        "links": {
            "self": "https://ex.com/api/rest/v1.0/plates/plateContainer:537d12b9-d8eb-46e8-b2e2-c50d1c01ba0a/summary"
        },
        "data": [
            {
                "type": "plateRow",
                "id": "869491dc-bf8b-3c43-a225-629e2c10900a",
                "attributes": {
                    "id": "869491dc-bf8b-3c43-a225-629e2c10900a",
                    "type": "plateRow",
                    "cells": [
                        {
                            "key": "76a7d17a-75b7-39a5-8549-05f073a064e3",
                            "type": "TEXT",
                            "name": "Well ID",
                            "content": {"user": "A1", "value": "A1"},
                        },
                        {
                            "key": "59f9b60c-a571-3c8e-982d-cdfe7e88e23c",
                            "type": "TEXT",
                            "name": "Row",
                            "content": {"user": "A", "value": "A"},
                        },
                        {
                            "key": "b5ff1ac8-310e-3848-9367-a4b8f4dc7ecc",
                            "type": "INTEGER",
                            "name": "Column",
                            "content": {"user": "1", "value": 1},
                        },
                        {
                            "key": "5a79aad4-7b07-39f1-9634-a2669a149a5b",
                            "type": "TEXT",
                            "name": "Plate",
                            "content": {"user": "Plate-1", "value": "Plate-1"},
                        },
                        {
                            "key": "43a9fcf2-bf40-3ed0-ba54-204275f053df",
                            "type": "INTEGER",
                            "name": "Order",
                            "content": {"user": "1", "value": 1},
                        },
                        {
                            "key": "f2053c2d-985d-3343-97e4-ae35b7fbe9d3",
                            "type": "TEXT",
                            "name": "Plate ID",
                            "content": {},
                        },
                    ],
                },
            },
            {
                "type": "plateRow",
                "id": "1b88b66a-598d-3552-bedc-aa468ea75776",
                "attributes": {
                    "id": "1b88b66a-598d-3552-bedc-aa468ea75776",
                    "type": "plateRow",
                    "cells": [
                        {
                            "key": "76a7d17a-75b7-39a5-8549-05f073a064e3",
                            "type": "TEXT",
                            "name": "Well ID",
                            "content": {"user": "A2", "value": "A2"},
                        },
                        {
                            "key": "59f9b60c-a571-3c8e-982d-cdfe7e88e23c",
                            "type": "TEXT",
                            "name": "Row",
                            "content": {"user": "A", "value": "A"},
                        },
                        {
                            "key": "b5ff1ac8-310e-3848-9367-a4b8f4dc7ecc",
                            "type": "INTEGER",
                            "name": "Column",
                            "content": {"user": "2", "value": 2},
                        },
                        {
                            "key": "5a79aad4-7b07-39f1-9634-a2669a149a5b",
                            "type": "TEXT",
                            "name": "Plate",
                            "content": {"user": "Plate-1", "value": "Plate-1"},
                        },
                        {
                            "key": "43a9fcf2-bf40-3ed0-ba54-204275f053df",
                            "type": "INTEGER",
                            "name": "Order",
                            "content": {"user": "1", "value": 1},
                        },
                        {
                            "key": "f2053c2d-985d-3343-97e4-ae35b7fbe9d3",
                            "type": "TEXT",
                            "name": "Plate ID",
                            "content": {},
                        },
                    ],
                },
            },
        ],
    }


@pytest.fixture()
def plate_container_content():
    return (
        b'{"eid":"plateContainer:8728059f-8472-4872-929b-fa033e724fe3","name":"Plates-1","numberOfRows":32,'
        + b'"numberOfColumns":48,"plates":[{"eid":"plate:f7cde4a2-f481-4c04-951f-83f59c45dd64","name":"Plate-1",'
        + b'"plateCustomName":"d","plateContainerEid":"plateContainer:8728059f-8472-4872-929b-fa033e724fe3",'
        + b'"isTemplate":false,"numberOfRows":32,"numberOfColumns":48,"annotationLayers":{},"fields":[]},'
        + b'{"eid":"plate:0b34fefd-71e4-4bbd-ba56-df2363e64877","name":"Plate-2",'
        + b'"plateContainerEid":"plateContainer:8728059f-8472-4872-929b-fa033e724fe3",'
        + b'"isTemplate":false,"numberOfRows":32,"numberOfColumns":48,"annotationLayers":{},"fields":[]}],'
        + b'"annotationLayers":[{"id":"9c41b7eb-e684-4354-9386-2bf97ae961a5",'
        + b'"name":"Well Format","isPredefined":true,'
        + b'"isHidden":false,"annotationClass":"wellformat","dataType":"TEXT","annotationLayerValues":{},'
        + b'"trashed":false,"order":0,"suggestions":[]},{"id":"b31bfe68-daa9-45e5-bda7-6f65733c792c",'
        + b'"name":"Concentration","isPredefined":true,"isHidden":false,"annotationClass":"concentration",'
        + b'"dataType":"DECIMAL","annotationLayerValues":{},"trashed":false,"order":1,"suggestions":[]},'
        + b'{"id":"212dfeb9-fa0d-49d5-927b-7c69054074a6","name":"Material","isPredefined":true,"isHidden":false,'
        + b'"annotationClass":"material","dataType":"LINK","annotationLayerValues":{},"trashed":false,"order":2,'
        + b'"suggestions":[]},{"id":"8dc52048-9c71-4442-b397-78bfdd164f4c","name":"Amount","isPredefined":true,'
        + b'"isHidden":false,"annotationClass":"amount","dataType":"DECIMAL","annotationLayerValues":{},'
        + b'"trashed":false,"order":3,"suggestions":[]},{"id":"e523e1dc-bb17-492e-8a9a-110060dfe561",'
        + b'"name":"Replicate","isPredefined":true,"isHidden":false,"annotationClass":"replicate",'
        + b'"dataType":"INTEGER","annotationLayerValues":{},"trashed":false,"order":4,"suggestions":[]},'
        + b'{"id":"24ea6db0-56ab-4542-9e1f-3b116915cd21","name":"Deviation","isPredefined":true,"isHidden":false,'
        + b'"annotationClass":"deviation","dataType":"TEXT","annotationLayerValues":{},"trashed":false,'
        + b'"order":5,"suggestions":[]}],"fields":[]}'
    )


def test_get_content(api_mock, plate_container_factory, plate_container_content):
    plate_container = plate_container_factory(name='name')
    file_name = 'Test.json'
    content = plate_container_content
    content_type = 'application/json'

    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    api_mock.call.return_value.content = content

    result = plate_container.get_content()

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('entities', plate_container.eid, 'export'),
        params={
            'format': None,
        },
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type


def test_get_html(api_mock, plate_container_factory, plates_response, snapshot):
    plate_container = plate_container_factory(name='name')

    api_mock.call.return_value.json.return_value = plates_response

    plate_container_html = plate_container.get_html()

    snapshot.assert_match(plate_container_html)


@pytest.mark.parametrize(
    'index', [1, '869491dc-bf8b-3c43-a225-629e2c10900a', UUID('869491dc-bf8b-3c43-a225-629e2c10900a')]
)
def test_getitem(api_mock, plate_container_factory, index, plates_response):
    plate_container = plate_container_factory()

    assert plate_container._rows == []
    assert plate_container._rows_by_id == {}

    api_mock.call.return_value.json.return_value = plates_response

    plate = plate_container[0]
    assert isinstance(plate, PlateRow)

    assert plate_container._rows != []
    assert plate_container._rows_by_id != {}

    assert isinstance(plate_container[index], PlateRow)


def test_iter(api_mock, plate_container_factory, plates_response):
    plate_container = plate_container_factory()

    assert plate_container._rows == []
    assert plate_container._rows_by_id == {}

    api_mock.call.return_value.json.return_value = plates_response

    for plate in plate_container:
        assert isinstance(plate, PlateRow)

        plate_property = plate[0]
        assert isinstance(plate_property, PlateCell)

        for item in plate:
            assert isinstance(item, PlateCell)

    assert plate_container._rows != []
    assert plate_container._rows_by_id != {}
