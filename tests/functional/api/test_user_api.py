from app.server.models.user import User


def test_get_all_users(test_client, activated_admin_user):
    """
    GIVEN a flask application
    WHEN a GET request sent to '/api/v1/user/' with a valid auth token
    THEN check all users are returned.
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.get('/api/v1/user/',
                               headers={
                                   'Authorization': f'Bearer {authentication_token}',
                                   'Accept': 'application/json'
                               },
                               content_type='application/json')
    assert response.status_code == 200
    if response.status_code == 200:
        assert len(response.json['data']['users']) == len(User.query.all())


def test_get_single_user(test_client, activated_admin_user, activated_client_user):
    """
    GIVEN a flask application
    WHEN a GET request is sent to '/api/v1/user/<int:user_id>/' by a client or admin user.
    THEN check that the specific user matching the id is returned.
    """
    for user in [activated_admin_user, activated_client_user]:
        authentication_token = user.encode_auth_token().decode()
        response = test_client.get(f'/api/v1/user/{user.id}/',
                                   headers={
                                       'Authorization': f'Bearer {authentication_token}',
                                       'Accept': 'application/json'
                                   },
                                   content_type='application/json')
        assert response.status_code == 200
        if response.status_code == 200:
            assert response.json['data']['user']['given_names'] == user.given_names


# TODO: [Philip] Refactor code to accommodate user edits


def test_delete_user(test_client, activated_admin_user):
    """
    GIVEN a flask application
    WHEN a DELETE request is sent to '/user/<int:user_id>/'
    THEN check that the delete user data is absent from the db.
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.delete(f'/api/v1/user/{activated_admin_user.id}/',
                                  headers={
                                      'Authorization': f'Bearer {authentication_token}',
                                      'Accept': 'application/json'
                                  },
                                  content_type='application/json')
    assert response.status_code == 200
    if response.status_code == 200:
        assert (User.query.get(activated_admin_user.id)) is None
