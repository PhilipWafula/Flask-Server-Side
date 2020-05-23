def test_organization_public_identifier(test_client,
                                        initialize_database,
                                        create_master_organization,
                                        create_standard_organization):
    assert create_master_organization.public_identifier is not None
    assert create_standard_organization.public_identifier is not None
