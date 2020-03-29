from typing import Dict
from typing import Optional

from jsonschema import validate
from jsonschema import ValidationError

from app.server import db
from app.server.models.configuration import Configuration
from app.server.models.organization import Organization
from app.server.schemas.organization import organization_schema
from app.server.schemas.json.organization import organization_json_schema


def add_organization_configuration(access_control_type=None,
                                   access_roles=None,
                                   access_tiers=None,
                                   organization_id=None):
    # check that configurations are tied to a specific organization
    if not organization_id:
        response = {
            'error':
                {'message': 'Configurations must be tied to an organization.',
                 'status': 'Fail'}}
        return response, 422

    # check that access control type is defined
    if not access_control_type:
        response = {
            'error':
                {'message': 'Access control type cannot be empty for an organization\'s configurations.',
                 'status': 'Fail'}}
        return response, 422

    if not access_roles:
        access_roles = []

    if not access_tiers:
        access_tiers = []

    configurations = Configuration(access_control_type=access_control_type,
                                   access_roles=access_roles,
                                   access_tiers=access_tiers,
                                   organization_id=organization_id)
    db.session.add(configurations)

    response = {'message': 'Successfully created configurations for organization id {}'.format(organization_id),
                'status': 'Success'}

    return response, 200


def create_organization(configurations: Optional[Dict] = None,
                        name=None,
                        is_master=False):
    """
    This function creates an organization with attributes  provided.
    :param is_master:
    :param configurations:
    :param name: The organization's name.
    :return: An organization object.
    """
    organization = Organization(name=name,
                                is_master=is_master)
    db.session.add(organization)

    # flush because data dump requires to id
    db.session.flush()

    if configurations:
        access_control_type = configurations.get('access_control_type', None)
        access_roles = configurations.get('access_roles', None)
        access_tiers = configurations.get('access_tiers', None)

        response, status_code = add_organization_configuration(access_control_type=access_control_type,
                                                               access_roles=access_roles,
                                                               access_tiers=access_tiers,
                                                               organization_id=organization.id)

        if status_code != 200:
            return response, status_code

    response = {'data': organization_schema.dump(organization).data,
                'message': 'Successfully created organization.',
                'status': 'Success'}

    return response, 200


def update_organization(organization, name=None):
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
    # check that configurations are tied to a specific organization
    try:
        validate(instance=organization_attributes,
                 schema=organization_json_schema)

    except ValidationError as exception:
        response = {
            'error':
                {'message': exception.message,
                 'status': 'Fail'}}
        return response, 422

    name = organization_attributes.get('name', None)
    is_master = organization_attributes.get('is_master', None)
    configurations = organization_attributes.get('configurations', None)

    if not name:
        response = {
            'error':
                {'message': 'Organization name cannot be empty.',
                 'status': 'Fail'}}
        return response, 422

    if not is_master:
        is_master = False

    # check if organization exists
    existing_organization = Organization.query.filter_by(name=name).first()

    if existing_organization and update_organization_allowed:
        try:
            organization = update_organization(organization=existing_organization,
                                               name=name)

            db.session.commit()
            response = {'data': organization_schema.dump(organization).data,
                        'message': 'Successfully updated organization.',
                        'status': 'Success'}
            return response, 200
        except Exception as exception:
            response = {
                'error':
                    {'message': '{}'.format(exception),
                     'status': 'Fail'}}
            return response, 400

    response, status_code = create_organization(configurations=configurations,
                                                name=name,
                                                is_master=is_master)

    if status_code == 200:
        db.session.commit()
        status_code = 201

    return response, status_code
