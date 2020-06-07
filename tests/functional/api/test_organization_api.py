import pytest
from app.server.models.organization import Organization


@pytest.mark.parametrize(
    "name, is_master, expected_status_code",
    [
        ("Test Standard Organization", False, 201),
        ("Test Master Organization", True, 201),
    ],
)
def test_create_standard_organization(
    test_client, initialize_database, name, is_master, expected_status_code
):
    """
    GIVEN a flask application
    WHEN a POST request with a valid standard organization json
    THEN check that organization is created.
    """
    response = test_client.post(
        "/api/v1/organization/",
        headers={"Accept": "application/json"},
        content_type="application/json",
        json={"name": name, "is_master": is_master},
    )
    assert response.status_code == expected_status_code
    if response.status_code == 201:
        assert response.json["data"]["organization"]["name"] == name


def test_get_all_organizations(test_client, activated_admin_user):
    """
    GIVEN a flask application
    WHEN a GET request is sent to '/api/v1/organization/' by an activated admin user
    THEN check that all organizations are returned.
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.get(
        "/api/v1/organization/",
        headers={
            "Authorization": f"Bearer {authentication_token}",
            "Accept": "application/json",
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert len(response.json["data"]["organizations"]) == len(
            Organization.query.all()
        )


def test_get_single_organization(
    test_client, create_master_organization, activated_admin_user
):
    """
    GIVEN a flask application
    WHEN a GET request is sent to '/api/v1/organization/<int:organization_id>/' by an activated admin user
    THEN check that the specific organization matching the id is returned.
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    response = test_client.get(
        f"/api/v1/organization/{create_master_organization.id}/",
        headers={
            "Authorization": f"Bearer {authentication_token}",
            "Accept": "application/json",
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert (
            response.json["data"]["organization"]["name"]
            == create_master_organization.name
        )


def test_edit_organization_data(
    test_client, create_master_organization, activated_admin_user
):
    """
    GIVEN a flask application
    WHEN a PUT request is sent to '/organization/<int:organization_id>/' with attributes being edited
    THEN check that the edited data attribute matches the new organization attribute.
    """
    authentication_token = activated_admin_user.encode_auth_token().decode()
    assert create_master_organization.name == "Test Master Organization"
    response = test_client.put(
        f"/api/v1/organization/{create_master_organization.id}/",
        headers={
            "Authorization": f"Bearer {authentication_token}",
            "Accept": "application/json",
        },
        json={"name": "Sample Master Organization"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert create_master_organization.name == "Sample Master Organization"
