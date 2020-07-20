from jsonschema.exceptions import ValidationError

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView

from app import config
from app.server.schemas.json import payment
from app.server.utils.payments.africas_talking import AfricasTalking
from app.server.utils.auth import requires_auth
from app.server.utils.validation import validate_request
from app.server.templates.responses import (
    invalid_payment_type,
    invalid_payments_service_provider,
    invalid_request_on_validation,
)

payments_blueprint = Blueprint("payments", __name__)


class PaymentAPI(MethodView):
    """
    Receives payment details.
    """

    def __init__(self):
        self.africas_talking_payments_client = AfricasTalking(
            config.AFRICASTALKING_API_KEY, config.AFRICASTALKING_USERNAME)

    # @requires_auth(authenticated_roles=['ADMIN'])
    def get(self):
        payments_service_provider = request.args.get('payments_service_provider', None)
        if payments_service_provider and payments_service_provider == 'africas_talking':
            query_result = self.africas_talking_payments_client.initiate_wallet_balance_request()
            response = query_result[0]
            status_code = query_result[1]
            return make_response(jsonify(response), status_code)
        elif payments_service_provider and payments_service_provider == 'daraja':
            # TODO[Philip]: Implement integration with daraja API
            pass
        else:
            response = {
                'error': {
                    'message': 'Invalid payments service provide.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 403)

    # @requires_auth(authenticated_roles=['ADMIN'])
    def post(self):
        payment_data = request.get_json()

        payments_service_provider = payment_data.get('payments_service_provider', None)
        payment_type = payment_data.get('payment_type', None)

        if payments_service_provider == 'africas_talking':
            if payment_type == 'business_to_business':
                # verify request
                try:
                    validate_request(
                        instance=payment_data,
                        schema=payment.africas_talking_business_to_business_json_schema)

                except ValidationError as error:
                    response, status_code = invalid_request_on_validation(error.message)
                    return make_response(jsonify(response), status_code)

                # make util call to create business to business transaction
                response, status_code = \
                    self.africas_talking_payments_client.create_business_to_business_transaction(
                        amount=payment_data.get('amount'),
                        destination_channel=payment_data.get('destination_account'),
                        destination_account=payment_data.get('destination_channel'),
                        product_name=payment_data.get('product_name'),
                        provider=payment_data.get('provider'),
                        transfer_type=payment_data.get('transfer_type'),
                        currency_code=payment_data.get('currency_code', "KES"),
                        metadata=payment_data.get('metadata')
                    )
                if status_code == 201:
                    result = self.africas_talking_payments_client.initiate_business_to_business_transaction(
                        response)

                    # normalize response to match standard API responses.
                    status_code = result[1]
                    if status_code == 201 and result[0].get("status") == "Queued":
                        response = {
                            'data': result[0],
                            'message': 'Business to business successfully initiated.',
                            'status': 'Success',
                        }
                        return make_response(jsonify(response), status_code)
                    else:
                        response = {
                            'error': {
                                'message': result[0].get('errorMessage'),
                                'status': result[0].get('status')
                            }
                        }
                        return make_response(jsonify(response), status_code)
                else:
                    return make_response(jsonify(response), status_code)

            elif payment_type == 'business_to_consumer':
                # verify request
                try:
                    validate_request(
                        instance=payment_data,
                        schema=payment.africas_talking_business_to_consumer_json_schema)

                except ValidationError as error:
                    response, status_code = invalid_request_on_validation(error.message)
                    return make_response(jsonify(response), status_code)

                response, status_code = \
                    self.africas_talking_payments_client.create_business_to_consumer_transaction(
                        amount=payment_data.get('amount'),
                        phone_number=payment_data.get('phone_number'),
                        product_name=payment_data.get('product_name'),
                        currency_code=payment_data.get('currency_code'),
                        metadata=payment_data.get('metadata'),
                        name=payment_data.get('name'),
                        provider_channel=payment_data.get('provider_channel'),
                        reason=payment_data.get('reason')
                    )
                if status_code == 201:
                    result = self.africas_talking_payments_client.initiate_business_to_consumer_transaction(
                        response)

                    # normalize response to match standard API responses.
                    status_code = result[1]
                    if status_code == 201 and result[0].get("numQueued") > 0:
                        response = {
                            'data': result[0],
                            'message': 'Business to consumer successfully initiated.',
                            'status': 'Success',
                        }
                        return make_response(jsonify(response), status_code)
                    else:
                        response = {
                            'error': {
                                'message': result[0].get('errorMessage'),
                                'status': result[0].get('status')
                            }
                        }
                        return make_response(jsonify(response), status_code)
                else:
                    return make_response(jsonify(response), status_code)

            elif payment_type == 'mobile_checkout':
                # verify request
                try:
                    validate_request(
                        instance=payment_data,
                        schema=payment.africas_talking_checkout_json_schema)

                except ValidationError as error:
                    response, status_code = invalid_request_on_validation(error.message)
                    return make_response(jsonify(response), status_code)

                response, status_code = \
                    self.africas_talking_payments_client.create_mobile_checkout_transaction(
                        amount=payment_data.get('amount'),
                        phone_number=payment_data.get('phone_number'),
                        product_name=payment_data.get('product_name'),
                        currency_code=payment_data.get('currency_code'),
                        metadata=payment_data.get('metadata'),
                        provider_channel=payment_data.get('provider_channel')
                    )
                if status_code == 201:
                    # initiate mobile checkout
                    result = self.africas_talking_payments_client.initiate_mobile_checkout_transaction(
                        response)

                    # normalize response to match standard API responses.
                    status_code = result[1]
                    if status_code == 201 and result[0].get("status") == "PendingConfirmation":
                        response = {
                            'data': result[0],
                            'message': 'Mobile checkout successfully initiated.',
                            'status': 'Success',
                        }
                        return make_response(jsonify(response), status_code)
                    else:
                        response = {
                            'error': {
                                'message': result[0].get('errorMessage'),
                                'status': result[0].get('status')
                            }
                        }
                        return make_response(jsonify(response), status_code)
                else:
                    return make_response(jsonify(response), status_code)
            else:
                response, status_code = invalid_payment_type(payment_type)
                return make_response(jsonify(response), status_code)
        elif payments_service_provider == 'daraja':
            # TODO[Philip]: Implement integration with Daraja API
            pass
        else:
            response, status_code = invalid_payments_service_provider(payments_service_provider)
            return make_response(jsonify(response), status_code)


create_payments_view = PaymentAPI.as_view("payments_view")
get_wallet_balance = PaymentAPI.as_view("wallet_balance_view")

payments_blueprint.add_url_rule(
    "/payments/",
    view_func=create_payments_view,
    methods=["POST"]
)
payments_blueprint.add_url_rule(
    "/wallet_balance/",
    view_func=get_wallet_balance,
    methods=["GET"]
)
