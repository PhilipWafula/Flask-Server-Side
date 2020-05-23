def test_send_sms(mock_sms_client, test_client, initialize_database):
    from app.server.utils.messaging import send_sms
    send_sms('+254712345678', 'Testing testing, ...sms testing.')
    messages = mock_sms_client
    assert len(messages) == 1
    assert messages == [
        {'phone': '+254712345678', 'message': 'Testing testing, ...sms testing.'}
    ]


def test_send_one_time_pin(mock_sms_client, test_client, initialize_database, create_client_user):
    from app.server.utils.messaging import send_one_time_pin
    client_user = create_client_user
    send_one_time_pin(user=client_user)
    messages = mock_sms_client
    assert len(messages) == 1
    assert messages[0].get('phone') == '+254712345678'
    assert f'Hello {client_user.given_names}, your activation code' in messages[0].get('message')
