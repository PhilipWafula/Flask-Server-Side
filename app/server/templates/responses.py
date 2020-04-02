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
            'message': 'Please provide a valid organization id.',
            'status': 'Fail'
        }
    }
    return response, 422


def user_not_found(user_id: int):
    response = {
        'error': {
            'message': 'User with id {} not found.'.format(user_id),
            'status': 'Fail'
        }
    }
    return response, 404


def user_id_not_provided():
    response = {
        'error': {
            'message': 'Please provide a valid user id.',
            'status': 'Fail'
        }
    }
    return response, 422
