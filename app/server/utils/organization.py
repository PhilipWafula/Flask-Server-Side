from jsonschema import ValidationError

from app.server import db
from app.server.models.organization import Organization
from app.server.schemas.organization import organization_schema
from app.server.schemas.json.organization import organization_json_schema
from app.server.templates.responses import invalid_request_on_validation
from app.server.utils.validation import validate_request


def create_organization(address=None, is_master=False, name=None) -> Organization:
    """
    This function creates an organization with attributes  provided.
    :param address:
    :param is_master:
    :param name: The organization's name.
    :return: An organization object.
    """
    organization = Organization(address=address, name=name, is_master=is_master)

    db.session.add(organization)

    return organization


def update_organization(
    organization: Organization, address=None, name=None
) -> Organization:
    """
    This functions updates an organization's attributes.
    :param address:
    :param organization: The organization object to modify
    :param name: The organizations name.
    :return: An organization object.
    """
    if name:
        organization.name = name

    if address:
        organization.address = address

    return organization


def process_create_or_update_organization_request(
    organization_attributes, update_organization_allowed=False
):
    address = organization_attributes.get("address", None)
    name = organization_attributes.get("name", None)
    is_master = organization_attributes.get("is_master", None)
    organization_id = organization_attributes.get("organization_id", None)

    # check that settings are tied to a specific organization
    try:
        validate_request(
            instance=organization_attributes, schema=organization_json_schema
        )

    except ValidationError as error:
        response, status_code = invalid_request_on_validation(error.message)
        return response, status_code

    if not is_master:
        is_master = False

    existing_organization = None

    if organization_id:
        # check if organization exists
        existing_organization = Organization.query.get(organization_id)

    if existing_organization and update_organization_allowed:
        try:
            organization = update_organization(
                organization=existing_organization, address=address, name=name
            )

            response = {
                "data": {"organization": organization_schema.dump(organization).data},
                "message": "Successfully updated organization.",
                "status": "Success",
            }
            return response, 200
        except Exception as exception:
            response = {"error": {"message": f"{exception}", "status": "Fail"}}
            return response, 400

    organization = create_organization(name=name, address=address, is_master=is_master)

    response = {
        "data": {"organization": organization_schema.dump(organization).data},
        "message": "Successfully created organization.",
        "status": "Success",
    }

    return response, 200
