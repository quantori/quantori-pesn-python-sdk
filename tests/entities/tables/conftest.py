import pytest


@pytest.fixture()
def templates():
    return {
        'links': {
            'self': 'https://ex.com/api/rest/v1.0/entities?includeTypes='
            'grid&includeOptions=template&page[offset]=0&page[limit]=20',
            'first': 'https://ex.com/api/rest/v1.0/entities?includeTypes='
            'grid&includeOptions=template&page[offset]=0&page[limit]=20',
        },
        'data': [
            {
                'type': 'entity',
                'id': 'grid:58726e57-a998-46f5-8b9e-b4760210ce74',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/grid:58726e57-a998-46f5-8b9e-b4760210ce74'},
                'attributes': {
                    'id': 'grid:58726e57-a998-46f5-8b9e-b4760210ce74',
                    'eid': 'grid:58726e57-a998-46f5-8b9e-b4760210ce74',
                    'name': 'My Table Template 1 (SK)',
                    'description': '',
                    'createdAt': '2021-11-08T08:03:47.233Z',
                    'editedAt': '2021-11-17T10:00:16.821Z',
                    'type': 'grid',
                    'digest': '81353707',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'My Table Template 1 (SK)'}},
                    'flags': {'canEdit': True},
                },
                'relationships': {
                    'createdBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/103'},
                        'data': {'type': 'user', 'id': '103'},
                    },
                    'editedBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/103'},
                        'data': {'type': 'user', 'id': '103'},
                    },
                    'owner': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/103'},
                        'data': {'type': 'user', 'id': '103'},
                    },
                    'source': {
                        'links': {
                            'self': 'https://ex.com/api/rest/v1.0/entities/'
                            'grid:58726e57-a998-46f5-8b9e-b4760210ce74/export'
                        }
                    },
                },
            },
            {
                'type': 'entity',
                'id': 'grid:288ccb92-cf46-4717-94f5-b36b136255fe',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/grid:288ccb92-cf46-4717-94f5-b36b136255fe'},
                'attributes': {
                    'id': 'grid:288ccb92-cf46-4717-94f5-b36b136255fe',
                    'eid': 'grid:288ccb92-cf46-4717-94f5-b36b136255fe',
                    'name': 'AK-2021-11-10 Test Table Template',
                    'description': '',
                    'createdAt': '2021-11-10T11:59:03.060Z',
                    'editedAt': '2021-11-10T12:05:19.180Z',
                    'type': 'grid',
                    'digest': '62644670',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'AK-2021-11-10 Test Table Template'}},
                    'flags': {'canEdit': True},
                },
                'relationships': {
                    'createdBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/109'},
                        'data': {'type': 'user', 'id': '109'},
                    },
                    'editedBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/109'},
                        'data': {'type': 'user', 'id': '109'},
                    },
                    'owner': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/109'},
                        'data': {'type': 'user', 'id': '109'},
                    },
                    'source': {
                        'links': {
                            'self': 'https://ex.com/api/rest/v1.0/'
                            'entities/grid:288ccb92-cf46-4717-94f5-b36b136255fe/export'
                        }
                    },
                },
            },
            {
                'type': 'entity',
                'id': 'grid:6a596788-4752-4d3d-b6d4-06a4b07523af',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/grid:6a596788-4752-4d3d-b6d4-06a4b07523af'},
                'attributes': {
                    'id': 'grid:6a596788-4752-4d3d-b6d4-06a4b07523af',
                    'eid': 'grid:6a596788-4752-4d3d-b6d4-06a4b07523af',
                    'name': 'Elemental analysis',
                    'description': '',
                    'createdAt': '2021-11-12T08:34:08.857Z',
                    'editedAt': '2021-12-15T14:54:42.738Z',
                    'type': 'grid',
                    'digest': '27531153',
                    'fields': {'Description': {'value': ''}, 'Name': {'value': 'Elemental analysis'}},
                    'flags': {'canEdit': True},
                },
                'relationships': {
                    'createdBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/106'},
                        'data': {'type': 'user', 'id': '106'},
                    },
                    'editedBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/106'},
                        'data': {'type': 'user', 'id': '106'},
                    },
                    'owner': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/106'},
                        'data': {'type': 'user', 'id': '106'},
                    },
                    'source': {
                        'links': {
                            'self': 'https://ex.com/api/rest/'
                            'v1.0/entities/grid:6a596788-4752-4d3d-b6d4-06a4b07523af/export'
                        }
                    },
                },
            },
            {
                'type': 'entity',
                'id': 'grid:416811e8-516d-4dd2-81be-bd21fc4350df',
                'links': {'self': 'https://ex.com/api/rest/v1.0/entities/grid:416811e8-516d-4dd2-81be-bd21fc4350df'},
                'attributes': {
                    'id': 'grid:416811e8-516d-4dd2-81be-bd21fc4350df',
                    'eid': 'grid:416811e8-516d-4dd2-81be-bd21fc4350df',
                    'name': 'Optimization of the reaction conditions',
                    'description': '',
                    'createdAt': '2021-11-12T11:16:17.431Z',
                    'editedAt': '2021-11-12T11:21:59.688Z',
                    'type': 'grid',
                    'digest': '70693790',
                    'fields': {
                        'Description': {'value': ''},
                        'Name': {'value': 'Optimization of the reaction conditions'},
                    },
                    'flags': {'canEdit': True},
                },
                'relationships': {
                    'createdBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/111'},
                        'data': {'type': 'user', 'id': '111'},
                    },
                    'editedBy': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/111'},
                        'data': {'type': 'user', 'id': '111'},
                    },
                    'owner': {
                        'links': {'self': 'https://ex.com/api/rest/v1.0/users/111'},
                        'data': {'type': 'user', 'id': '111'},
                    },
                    'source': {
                        'links': {
                            'self': 'https://ex.com/api/rest/v1.0/'
                            'entities/grid:416811e8-516d-4dd2-81be-bd21fc4350df/export'
                        }
                    },
                },
            },
        ],
    }
