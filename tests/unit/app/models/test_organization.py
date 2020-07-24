def test_organization_public_identifier(
    test_client,
    initialize_database,
    create_master_organization,
    create_standard_organization,
):
    assert create_master_organization.public_identifier is not None
    assert create_standard_organization.public_identifier is not None


def test_get_organization_by_id(test_client, initialize_database, create_master_organization):
    from app.server.api.organization import get_organization_by_id
    organization = get_organization_by_id(organization_id=create_master_organization.id)
    assert organization.name == "Test Master Organization"
