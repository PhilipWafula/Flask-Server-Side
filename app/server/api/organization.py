from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView

from app.server import db
from app.server.models.organization import Organization
from app.server.schemas.configuration import configuration_schema
from app.server.schemas.organization import organization_schema
from app.server.schemas.organization import organizations_schema
from app.server.templates.responses import organization_id_not_provided
from app.server.templates.responses import organization_not_found
from app.server.utils.auth import requires_auth
from app.server.utils.configuration import process_add_or_update_organization_configuration
from app.server.utils.organization import process_create_or_update_organization_request
from app.server.utils.query import paginate_query

organization_blueprint = Blueprint('organization', __name__)


def get_organization_by_id(organization_id):
    organization = Organization.query.execution_options(show_all=True).get(organization_id)
    return organization


class OrganizationAPI(MethodView):
    """
    Creates organization
    """

    def post(self):
        organization_data = request.get_json()

        response, status_code = process_create_or_update_organization_request(organization_data)
        if status_code == 200:
            db.session.commit()
            status_code = 201

        return make_response(jsonify(response), status_code)

    @requires_auth
    def get(self, organization_id):
        if organization_id:
            organization = Organization.query.execution_options(show_all=True).get(organization_id)

            if not organization:
                response, status_code = organization_not_found(organization_id=organization_id)
                return make_response(jsonify(response), status_code)

            response = {
                'data': {'organization': organization_schema.dump(organization).data},
                'message': 'Successfully loaded organization data.',
                'status': 'Success'}
            return make_response(jsonify(response), 200)

        else:
            organizations_query = Organization.query.execution_options(show_all=True)

            organizations, total_items, total_pages = paginate_query(organizations_query, Organization)

            if not organizations:
                response = {
                    'error':
                        {
                            'message': 'No organizations were found.',
                            'status': 'Fail'
                        }}
                return make_response(jsonify(response), 404)

            response = {
                'data': {'organizations': organizations_schema.dump(organizations).data},
                'items': total_items,
                'message': 'Successfully loaded all organizations.',
                'pages': total_pages,
                'status': 'Success'
            }
            return make_response(jsonify(response), 200)

    @requires_auth
    def put(self, organization_id: int):
        # get organization data to edit
        organization_data = request.get_json()

        if organization_id:
            # add organization id to attributes
            organization_data['organization_id'] = organization_id

            response, status_code = process_create_or_update_organization_request(
                organization_attributes=organization_data,
                update_organization_allowed=True)

            if status_code == 200:
                db.session.commit()

            return make_response(jsonify(response), status_code)

        response, status_code = organization_id_not_provided()
        return make_response(jsonify(response), status_code)


class OrganizationConfigurationAPI(MethodView):
    def post(self, organization_id: int):
        # get configuration creation data
        configuration_creation_data = request.get_json()

        if organization_id:

            # get organization
            organization = get_organization_by_id(organization_id=organization_id)

            if not organization:
                response, status_code = organization_not_found(organization_id=organization_id)
                return response, status_code

            response, status_code = process_add_or_update_organization_configuration(configuration_creation_data)

            return make_response(jsonify(response), status_code)

        response, status_code = organization_id_not_provided()
        return make_response(jsonify(response), status_code)

    @requires_auth
    def get(self, organization_id: int):
        if organization_id:
            # get organization
            organization = get_organization_by_id(organization_id=organization_id)

            if not organization:
                response, status_code = organization_not_found(organization_id=organization_id)
                return response, status_code

            configuration = organization.configuration
            response = {
                'data': {'configuration': configuration_schema.dump(configuration).data},
                'message': 'Successfully loaded configuration for organization {}'.format(
                    organization.name),
                'status': 'Success'
            }
            return make_response(jsonify(response), 200)

        response, status_code = organization_id_not_provided()
        return make_response(jsonify(response), status_code)

    def put(self, organization_id: int):
        if organization_id:
            # get organization configuration data
            organization_configuration_data = request.get_json()

            # add organization id to attributes
            organization_configuration_data['organization_id'] = organization_id

            response, status_code = process_add_or_update_organization_configuration(
                configuration_attributes=organization_configuration_data,
                update_configuration_allowed=True)

            return make_response(jsonify(response), status_code)

        response, status_code = organization_id_not_provided()
        return make_response(jsonify(response), status_code)

    def delete(self, organization_id: int):
        # get data to delete
        data_to_delete = request.get_json()

        access_roles = data_to_delete.get('access_roles', None)
        access_tiers = data_to_delete.get('access_tiers', None)

        if organization_id:
            # get organization
            organization = get_organization_by_id(organization_id=organization_id)

            if not organization:
                response, status_code = organization_not_found(organization_id)
                return make_response(jsonify(response), status_code)

            # get organization configuration
            configuration = organization.configuration

            if not access_roles and not access_tiers:
                response = {
                    'error': {
                        'message': 'Could not delete. No access roles or tiers were provided.',
                        'status': 'Fail'
                    }
                }

                return make_response(jsonify(response), 422)

            if access_roles:
                if isinstance(access_roles, list):
                    for role in access_roles:
                        configuration.remove_specific_access_attribute(access_attribute_type='role',
                                                                       role=role)

                if isinstance(access_roles, str):
                    if access_roles == 'all':
                        configuration.remove_all_access_attributes(access_attribute_type='role')

            if access_tiers:
                if isinstance(access_tiers, list):
                    for tier in access_tiers:
                        configuration.remove_specific_access_attribute(access_attribute_type='tier',
                                                                       tier=tier)

                if isinstance(access_tiers, str):
                    if access_tiers == 'all':
                        configuration.remove_all_access_attributes(access_attribute_type='tier')

            db.session.commit()
            response = {
                'data': {'configuration': configuration_schema.dump(configuration).data},
                'message': 'Successfully deleted.',
                'status': 'Success'
            }
            return make_response(jsonify(response), 200)

        response, status_code = organization_id_not_provided()
        return make_response(jsonify(response), status_code)


organization_view = OrganizationAPI.as_view('organization_view')
single_organization_view = OrganizationAPI.as_view('single_organization_view')
organization_configuration_view = OrganizationConfigurationAPI.as_view('organization_configuration_view')

organization_blueprint.add_url_rule('/organization/',
                                    view_func=organization_view,
                                    methods=['POST', ])

organization_blueprint.add_url_rule('/organization/',
                                    view_func=organization_view,
                                    methods=['GET', ],
                                    defaults={'organization_id': None})

organization_blueprint.add_url_rule('/organization/<int:organization_id>/',
                                    view_func=single_organization_view,
                                    methods=['GET', 'PUT', ])

organization_blueprint.add_url_rule('/organization/<int:organization_id>/configuration/',
                                    view_func=organization_configuration_view,
                                    methods=['GET', 'PUT', ])

organization_blueprint.add_url_rule('/organization/<int:organization_id>/configuration/',
                                    view_func=organization_configuration_view,
                                    methods=['DELETE', ])
