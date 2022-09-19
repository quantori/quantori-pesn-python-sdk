import pytest


@pytest.fixture()
def task_properties():
    return {
        'data': [
            {
                'type': 'property',
                'id': '1',
                'attributes': {
                    'id': '1',
                    'name': 'Task ID',
                    'content': {
                        'type': 'task',
                        'display': 'Task-4',
                        'value': 'task:58ebedd9-c158-4bf3-b737-b45aea636a61',
                    },
                },
            },
            {
                'type': 'property',
                'id': '2',
                'attributes': {'id': '2', 'name': 'Task Type', 'content': {'display': 'Task', 'value': 'Task'}},
            },
            {
                'type': 'property',
                'id': '3',
                'attributes': {
                    'id': '3',
                    'name': 'Reference ID',
                    'content': {
                        'type': 'experiment',
                        'display': 'Synthesis of SPI',
                        'value': 'experiment:8d7eab5c-75a5-4458-ae6a-285ab0116a44',
                    },
                },
            },
            {
                'type': 'property',
                'id': '4',
                'attributes': {'id': '4', 'name': 'Requestor Comment', 'content': {'display': '5545', 'value': '5545'}},
            },
            {
                'type': 'property',
                'id': '5',
                'attributes': {'id': '5', 'name': 'Analyst Comment', 'content': {}},
            },
            {
                'type': 'property',
                'id': '6',
                'attributes': {'id': '6', 'name': 'Required By', 'content': {}},
            },
            {
                'type': 'property',
                'id': '7',
                'attributes': {
                    'id': '7',
                    'name': 'Analyst',
                    'content': {
                        'userInfo': {
                            'links': {'self': 'https://example.com/api/rest/v1.0/users/119'},
                            'data': {'type': 'user', 'id': '119'},
                        },
                        'value': {
                            'userId': '119',
                            'userName': 'evgeniy.pokidov@quantori.com',
                            'email': 'evgeniy.pokidov@quantori.com',
                            'firstName': 'Evgeniy',
                            'lastName': 'Pokidov',
                            'picture': {},
                        },
                    },
                },
            },
            {
                'type': 'property',
                'id': '8',
                'attributes': {
                    'id': '8',
                    'name': 'Experiment Link',
                    'content': {
                        'type': 'experiment',
                        'display': 'Test experiment creation by SDK',
                        'value': 'experiment:f7fb12b2-1180-4fa0-9bcd-ccc2f7ec0e8f',
                    },
                },
            },
            {
                'type': 'property',
                'id': '9',
                'attributes': {
                    'id': '9',
                    'name': 'Request Link',
                    'content': {
                        'type': 'request',
                        'display': 'TRX-000002',
                        'value': 'request:f56f61c5-9e1a-4c33-aa89-e9416027a586',
                    },
                },
            },
            {
                'type': 'property',
                'id': '10',
                'attributes': {
                    'id': '10',
                    'name': 'Status',
                    'content': {'display': 'In Progress', 'value': 'In Progress'},
                },
            },
            {
                'type': 'property',
                'id': '11',
                'attributes': {
                    'id': '11',
                    'name': 'Attached Docs',
                    'content': {'display': '0', 'value': '0', 'eid': 'task:58ebedd9-c158-4bf3-b737-b45aea636a61'},
                },
            },
            {
                'type': 'property',
                'id': '13',
                'attributes': {'id': '13', 'name': 'Created Date', 'content': {'value': '2022-06-15T21:00:00.000Z'}},
            },
        ],
    }
