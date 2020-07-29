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


def test_get_master_organization(test_client, initialize_database, create_master_organization, create_standard_organization):
    from app.server.models.organization import Organization
    # check that there are multiple organizations in the database
    organizations = Organization.query.all()
    assert len(organizations) > 0

    master_organization = Organization.master_organisation()
    assert master_organization.name == 'Test Master Organization'
