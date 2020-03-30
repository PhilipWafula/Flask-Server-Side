def organization_not_found(organization_id: int):
    response = {
        'error': {
            'message': 'Organization with id {} not found.'.format(organization_id),
            'status': 'Fail'
        }
    }
    return response, 404


def organization_id_not_provided():
    response = {
        'error': {
            'message': 'Please provide and organization id.',
            'status': 'Fail'
        }
    }
    return response, 422
