from app.server import db
from app.server.models.organization import Organization
from app.server.schemas.organization import organization_schema


def create_organization(name=None):
    """
    This function creates an organization with attributes  provided.
    :param name: The organization's name.
    :return: An organization object.
    """
    organization = Organization(name=name)
    db.session.add(organization)
    # flush because data dump requires to id
    db.session.flush()

    return organization


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
    name = organization_attributes.get('name')

    if not name:
        response = {'error': {'message': 'Organization name cannot be empty.',
                              'status': 'Fail'}}
        return response, 422

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
            response = {'error': {'message': '{}'.format(exception),
                                  'status': 'Fail'}}
            return response, 400

    organization = create_organization(name=name)

    response = {'data': organization_schema.dump(organization).data,
                'message': 'Successfully updated organization.',
                'status': 'Success'}
    return response, 200
