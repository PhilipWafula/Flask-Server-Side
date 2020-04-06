from typing import List
from typing import Optional

from app.server import db
from app.server.constants import SUPPORTED_ACCESS_CONTROL_TYPES
from app.server.models.configuration import Configuration
from app.server.models.organization import Organization
from app.server.schemas.configuration import configuration_schema
from app.server.utils.enums.access_control_enums import AccessControlType


def add_organization_configuration(access_control_type=None,
                                   access_roles: Optional[List] = None,
                                   access_tiers: Optional[List] = None,
                                   domain=None,
                                   organization_id=None):
    configuration = Configuration(access_control_type=access_control_type,
                                  access_roles=access_roles,
                                  access_tiers=access_tiers,
                                  domain=domain,
                                  organization_id=organization_id)
    db.session.add(configuration)

    response = {
        'message': 'Successfully created configuration for organization id {}'.format(
            organization_id),
        'status': 'Success'}

    return response, 200


def update_organization_configuration(configuration: Configuration,
                                      access_control_type=None,
                                      access_roles: Optional[List] = None,
                                      access_tiers: Optional[List] = None,
                                      domain=None,
                                      mailer_settings=None):
    if access_control_type:
        configuration.access_control_type = access_control_type

    if access_roles:
        configuration.set_access_attribute(access_attribute_type='role',
                                           roles_list=access_roles)

    if access_tiers:
        configuration.set_access_attribute(access_attribute_type='tier',
                                           tiers_list=access_tiers)

    if domain:
        configuration.domain = domain

    if mailer_settings:
        configuration.add_mailer_settings(mailer_settings)

    return configuration


def process_add_or_update_organization_configuration(configuration_attributes: dict,
                                                     update_configuration_allowed=False):

    organization_id = configuration_attributes.get('organization_id', None)
    access_control_type = configuration_attributes.get('access_control_type', None)
    access_roles = configuration_attributes.get('access_roles', None)
    access_tiers = configuration_attributes.get('access_tiers', None)
    domain = configuration_attributes.get('domain', None)
    mailer_settings = configuration_attributes.get('mailer_settings', None)

    # check that configuration are tied to a specific organization
    if not organization_id:
        response = {
            'error':
                {
                    'message': 'No organization ID provided. Configurations must be tied to an organization.',
                    'status': 'Fail'
                }}
        return response, 422

    if not access_roles:
        access_roles = []

    if not access_tiers:
        access_tiers = []

    if access_control_type:
        if access_control_type not in SUPPORTED_ACCESS_CONTROL_TYPES:
            response = {
                'error':
                    {
                        'message': 'Access control type not supported.',
                        'status': 'Fail'
                    }
            }
            return response, 422

        if access_control_type == 'STANDARD':
            access_control_type = AccessControlType.STANDARD_ACCESS_CONTROL

        if access_control_type == 'TIERED':
            access_control_type = AccessControlType.TIERED_ACCESS_CONTROL

    if update_configuration_allowed:

        # check if organization exists
        existing_organization = Organization.query.get(organization_id)

        if existing_organization:
            # get organization's configuration
            existing_organization_configuration = existing_organization.configuration

            if existing_organization_configuration:
                try:
                    updated_configuration = update_organization_configuration(existing_organization_configuration,
                                                                              access_control_type=access_control_type,
                                                                              access_roles=access_roles,
                                                                              access_tiers=access_tiers,
                                                                              domain=domain,
                                                                              mailer_settings=mailer_settings)
                    db.session.commit()
                    response = {
                        'data': {'configuration': configuration_schema.dump(updated_configuration).data},
                        'message': 'Successfully updated configuration for organization id {}'.format(organization_id),
                        'status': 'Success'}

                    return response, 200

                except Exception as exception:
                    response = {
                        'error': {
                            'message': 'An error occurred: {}'.format(exception),
                            'status': 'Fail'
                        }}
                    return response, 400

        else:
            response = {
                'error': {
                    'message': 'Organization not found for organization id {}'.format(organization_id),
                    'status': 'Fail'
                }
            }
            return response, 404

    try:
        configuration = add_organization_configuration(access_control_type=access_control_type,
                                                       access_roles=access_roles,
                                                       access_tiers=access_tiers,
                                                       domain=domain,
                                                       organization_id=organization_id)
        db.session.add(configuration)
        response = {
            'data': {'configuration': configuration_schema.dump(configuration).data},
            'message': 'Successfully added configuration for organization id {}'.format(organization_id),
            'status': 'Success'}
        return response, 200
    except Exception as exception:
        response = {
            'error':
                {
                    'message': 'An error occurred: {}'.format(exception),
                    'status': 'Fail'
                }
        }
        return response, 422
