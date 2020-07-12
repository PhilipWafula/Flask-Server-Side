def organization_not_found(organization_id: int):
    response = {
        "error": {
            "message": f"Organization with id {organization_id} not found.",
            "status": "Fail",
        }
    }
    return response, 404


def organization_id_not_provided():
    response = {
        "error": {
            "message": "Please provide a valid organization id.",
            "status": "Fail",
        }
    }
    return response, 422


def user_not_found(user_id: int):
    response = {
        "error": {
            "message": f"User with id {user_id} not found.",
            "status": "Fail",
        }
    }
    return response, 404


def user_id_not_provided():
    response = {
        "error": {
            "message": "Please provide a valid user id.",
            "status": "Fail"
        }
    }
    return response, 422


def invalid_request_on_validation(message: str):
    response = {
        "error": {
            "message": f"Invalid request: {message}",
            "status": "Fail"
        }
    }
    return response, 400


def mailer_not_configured():
    response = {
        "error": {
            "message": "Please configure your mailer, to facilitate admin registration.",
            "status": "Fail",
        }
    }
    return response, 403


def otp_resent_successfully():
    response = {
        "message": "Pin resent successfully.",
        "status": "Success"
    }
    return response, 200


def invalid_amount_type(amount: any):
    response = {
        "error": {
            "message": f"Incorrect amount type: {type(amount)}.",
            "status": "Fail",
        }
    }
    return response, 422


def unsupported_currency_code(currency_code: str):
    response = {
        "error": {
            "message": f"Unsupported currency code: {currency_code}.",
            "status": "Fail",
        }
    }
    return response, 422


def unsupported_provider(provider: str):
    response = {
        "error": {
            "message": f"Unsupported provider: {provider}.",
            "status": "Fail"
        }
    }
    return response, 422


def unsupported_transfer_type(transfer_type: str):
    response = {
        "error": {
            "message": f"Unsupported transfer type: {transfer_type}.",
            "status": "Fail",
        }
    }
    return response, 422


def unsupported_reason(reason: str):
    response = {
        "error": {
            "message": f"Unsupported reason: {reason}.",
            "status": "Fail"
        }
    }
    return response, 422


def invalid_payment_type(payment_type: str):
    response = {
        "error": {
            "message": f"Invalid payment type: {payment_type}",
            "status": "Fail"
        }
    }
    return response, 422


def invalid_payments_service_provider(payments_service_provider: str):
    response = {
        "error": {
            "message": f"Invalid payments service provider: {payments_service_provider}",
            "status": "Fail"
        }
    }
    return response, 422
