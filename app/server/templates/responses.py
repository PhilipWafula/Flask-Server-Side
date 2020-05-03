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


def invalid_request_on_validation(message: str):
    response = {
        'error': {
            'message': 'Invalid request: {}'.format(message),
            'status': 'Fail'
        }
    }
    return response, 400


def mailer_not_configured():
    response = {
        'error': {
            'message': 'Please configure your mailer, to facilitate admin registration.',
            'status': 'Fail'
        }
    }
    return response, 403
