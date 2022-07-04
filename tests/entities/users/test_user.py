from signals_notebook.common_types import File
from signals_notebook.entities.users.user import User, UserCreationBody


def test_create(api_mock):
    response = {
        'links': {'self': 'https://snb.perkinelmer.net/api/rest/v1.0/users/100'},
        'data': {
            'id': '100',
            'type': 'user',
            'attributes': {
                'isEnabled': True,
                'userId': '100',
                'userName': 'foo.bar@perkinelmer.com',
                'email': 'unique2@quantori.com',
                'firstName': 'first_name',
                'lastName': 'last_name',
                'alias': 'alias',
                'country': 'USA',
                'organization': 'orga',
                'lastLoginAt': '2021-11-29T04:00:02.295Z',
                'createdAt': '2020-07-17T21:48:33.262Z',
            },
        },
    }
    new_user_body = UserCreationBody(
        alias='alias',
        country='USA',
        email='unique2@quantori.com',
        first_name='first_name',
        last_name='last_name',
        organization='orga',
    )
    api_mock.call.return_value.json.return_value = response

    result = User.create(request=new_user_body)

    api_mock.call.assert_called_once_with(
        method='POST',
        path=('users',),
        json={
            'data': {
                'attributes': new_user_body.dict(by_alias=True, exclude_none=True),
            }
        },
    )

    assert isinstance(result, User)
    assert result.id == response['data']['attributes']['userId']
    assert result.alias == response['data']['attributes']['alias']
    assert result.country == response['data']['attributes']['country']
    assert result.first_name == response['data']['attributes']['firstName']
    assert result.last_name == response['data']['attributes']['lastName']
    assert result.organization == response['data']['attributes']['organization']


def test_save(api_mock, user_factory):
    user = user_factory()
    new_first_name = 'Update first name'
    assert user.first_name != new_first_name

    user.first_name = new_first_name

    user.save()

    api_mock.call.assert_called_once_with(
        method='PATCH',
        path=('users', user.id),
        json={
            'data': {
                'attributes': {
                    'alias': user.alias,
                    'country': user.country,
                    'firstName': 'Update first name',
                    'lastName': user.last_name,
                    'organization': user.organization,
                },
            },
        },
    )
    assert user.first_name == new_first_name


def test_delete(api_mock, user_factory):
    user = user_factory()
    user.delete()

    api_mock.call.assert_called_once_with(
        method='DELETE',
        path=('users', user.id),
    )


def test_picture(api_mock, user_factory):
    content_type = 'image/jpeg'
    content = b'image'

    user = user_factory()
    file_name = f'{user.first_name}_{user.last_name}.{content_type.split("/")[-1]}'

    api_mock.call.return_value.content = content
    api_mock.call.return_value.headers = {
        'content-type': content_type,
        'content-disposition': f'attachment; filename={file_name}',
    }
    result = user.picture

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('users', user.id, 'picture'),
    )

    assert isinstance(result, File)
    assert result.name == file_name
    assert result.content == content
    assert result.content_type == content_type
