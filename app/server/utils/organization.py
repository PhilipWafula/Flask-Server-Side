from typing import Dict
from typing import Optional

from jsonschema import ValidationError

from app.server import db
from app.server.models.organization import Organization
from app.server.schemas.organization import organization_schema
from app.server.schemas.json.organization import organization_json_schema
from app.server.templates.responses import invalid_request_on_validation
from app.server.utils.configuration import add_organization_configuration
from app.server.utils.validation import validate_request


def create_organization(configuration: Optional[Dict] = None,
                        name=None,
                        is_master=False):
    """
    This function creates an organization with attributes  provided.
    :param is_master:
    :param configuration:
    :param name: The organization's name.
    :return: An organization object.
    """
    organization = Organization(name=name,
                                is_master=is_master)
    # create public identifier
    organization.set_public_identifier()

    db.session.add(organization)

    # flush because data dump requires to id
    db.session.flush()

    if configuration:
        access_control_type = configuration.get('access_control_type', None)
        access_roles = configuration.get('access_roles', None)
        access_tiers = configuration.get('access_tiers', None)
        domain = configuration.get('domain', None)

        response, status_code = add_organization_configuration(access_control_type=access_control_type,
                                                               access_roles=access_roles,
                                                               access_tiers=access_tiers,
                                                               domain=domain,
                                                               organization_id=organization.id)

        if status_code != 200:
            return response, status_code

    response = {'data': organization_schema.dump(organization).data,
                'message': 'Successfully created organization.',
                'status': 'Success'}

    return response, 200


def update_organization(organization: Organization,
                        name=None) -> Organization:
    """
    This functions updates an organization's attributes.
    :param organization: The organization object to modify
    :param name: The organizations name.
    :return: An organization object.
    """
    if name:
        organization.name = name

    return organization


def process_create_or_update_organization_request(organization_attributes,
                                                  update_organization_allowed=False):

    name = organization_attributes.get('name', None)
    is_master = organization_attributes.get('is_master', None)
    configuration = organization_attributes.get('configuration', None)
    organization_id = organization_attributes.get('organization_id', None)

    # check that configuration are tied to a specific organization
    try:
        validate_request(instance=organization_attributes,
                         schema=organization_json_schema)

    except ValidationError as error:
        response, status_code = invalid_request_on_validation(error.message)
        return response, status_code

    if not is_master:
        is_master = False

    existing_organization = None

    if organization_id:
        # check if organization exists
        existing_organization = Organization.query.get(id=organization_id)

    if existing_organization and update_organization_allowed:
        try:
            organization = update_organization(organization=existing_organization,
                                               name=name)

            db.session.commit()
            response = {
                'data': organization_schema.dump(organization).data,
                'message': 'Successfully updated organization.',
                'status': 'Success'
            }
            return response, 200
        except Exception as exception:
            response = {
                'error': {
                    'message': '{}'.format(exception),
                    'status': 'Fail'}
            }
            return response, 400

    response, status_code = create_organization(configuration=configuration,
                                                name=name,
                                                is_master=is_master)

    if status_code == 200:
        db.session.commit()
        status_code = 201

    return response, status_code
