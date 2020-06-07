from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView

from app.server import db
from app.server.models.organization import Organization
from app.server.schemas.organization import organization_schema
from app.server.schemas.organization import organizations_schema
from app.server.templates.responses import (
    organization_id_not_provided,
    organization_not_found,
)
from app.server.utils.auth import requires_auth
from app.server.utils.organization import process_create_or_update_organization_request
from app.server.utils.query import paginate_query

organization_blueprint = Blueprint("organization", __name__)


def get_organization_by_id(organization_id):
    organization = Organization.query.execution_options(show_all=True).get(
        organization_id
    )
    return organization


class OrganizationAPI(MethodView):
    """
    Creates organization
    """

    def post(self):
        organization_data = request.get_json()

        response, status_code = process_create_or_update_organization_request(
            organization_data
        )
        if status_code == 200:
            db.session.commit()
            status_code = 201

        return make_response(jsonify(response), status_code)

    @requires_auth(authenticated_roles=["ADMIN"])
    def get(self, organization_id):
        if organization_id:
            organization = Organization.query.execution_options(show_all=True).get(
                organization_id
            )

            if not organization:
                response, status_code = organization_not_found(
                    organization_id=organization_id
                )
                return make_response(jsonify(response), status_code)

            response = {
                "data": {"organization": organization_schema.dump(organization).data},
                "message": "Successfully loaded organization data.",
                "status": "Success",
            }
            return make_response(jsonify(response), 200)

        else:
            organizations_query = Organization.query.execution_options(show_all=True)

            organizations, total_items, total_pages = paginate_query(
                organizations_query, Organization
            )

            if not organizations:
                response = {
                    "error": {
                        "message": "No organizations were found.",
                        "status": "Fail",
                    }
                }
                return make_response(jsonify(response), 404)

            response = {
                "data": {
                    "organizations": organizations_schema.dump(organizations).data
                },
                "items": total_items,
                "message": "Successfully loaded all organizations.",
                "pages": total_pages,
                "status": "Success",
            }
            return make_response(jsonify(response), 200)

    @requires_auth(authenticated_roles=["ADMIN"])
    def put(self, organization_id: int):
        # get organization data to edit
        organization_data = request.get_json()

        if organization_id:
            # add organization id to attributes
            organization_data["organization_id"] = organization_id

            response, status_code = process_create_or_update_organization_request(
                organization_attributes=organization_data,
                update_organization_allowed=True,
            )

            if status_code == 200:
                db.session.commit()

            return make_response(jsonify(response), status_code)

        response, status_code = organization_id_not_provided()
        return make_response(jsonify(response), status_code)


organization_view = OrganizationAPI.as_view("organization_view")
single_organization_view = OrganizationAPI.as_view("single_organization_view")

organization_blueprint.add_url_rule(
    "/organization/", view_func=organization_view, methods=["POST"]
)

organization_blueprint.add_url_rule(
    "/organization/",
    view_func=organization_view,
    methods=["GET"],
    defaults={"organization_id": None},
)

organization_blueprint.add_url_rule(
    "/organization/<int:organization_id>/",
    view_func=single_organization_view,
    methods=["GET", "PUT"],
)
