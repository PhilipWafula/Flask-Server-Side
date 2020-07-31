# application imports
from app.server.models.mpesa_transaction import MpesaTransaction


def test_get_all_mpesa_transactions(test_client,
                                    activated_admin_user,
                                    create_initiated_mpesa_transaction,
                                    create_failed_mpesa_transaction):
    """
    GIVEN a flask application
    WHEN a GET request is sent to '/api/v1/mpesa_transactions/' by an activated admin user
    THEN check that all mpesa_transactions are returned.
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.get(
        "/api/v1/mpesa_transactions/",
        headers={
            "Authorization": f"Bearer {authentication_token}",
            "Accept": "application/json",
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert len(response.json["data"]["mpesa_transactions"]) == len(
            MpesaTransaction.query.all()
        )
