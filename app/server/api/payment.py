from jsonschema.exceptions import ValidationError

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask.views import MethodView

from app import config
from app.server.schemas.json import payment
from app.server.utils.payments.africas_talking import AfricasTalking
from app.server.utils.validation import validate_request
from app.server.templates.responses import (
    invalid_payment_type,
    invalid_provider_type,
    invalid_request_on_validation,
)

payment_blueprint = Blueprint("payment", __name__)


class PaymentAPI(MethodView):
    """
    Receives payment details.
    """

    def post(self):
        payment_data = request.get_json()
        payments = AfricasTalking(config.AFRICASTALKING_API_KEY, config.AFRICASTALKING_USERNAME)

        if payment_data['provider_type'] == 'africas_talking':
            if payment_data['payment_type'] == 'business_to_business':
                # verify request
                try:
                    validate_request(
                        instance=payment_data,
                        schema=payment.africas_talking_business_to_business_json_schema)

                except ValidationError as error:
                    response, status_code = invalid_request_on_validation(error.message)
                    return response, status_code

                business_to_business_transaction = payments.create_business_to_business_transaction(
                    payment_data['amount'],
                    payment_data['destination_account'],
                    payment_data['destination_channel'],
                    payment_data['product_name'],
                    payment_data['provider'],
                    payment_data['transfer_type'],
                    payment_data['currency_code'],
                    payment_data['metadata']
                )
                payments.initiate_business_to_business_transaction(business_to_business_transaction)
            elif payment_data['payment_type'] == 'business_to_consumer':
                # verify request
                try:
                    validate_request(
                        instance=payment_data,
                        schema=payment.africas_talking_business_to_consumer_json_schema)

                except ValidationError as error:
                    response, status_code = invalid_request_on_validation(error.message)
                    return response, status_code

                business_to_consumer_transaction = payments.create_business_to_consumer_transaction(
                    payment_data['amount'],
                    payment_data['phone_number'],
                    payment_data['product_name'],
                    payment_data['currency_code'],
                    payment_data['metadata'],
                    payment_data['name'],
                    payment_data['provider_channel'],
                    payment_data['reason']
                )
                payments.initiate_business_to_consumer_transaction(business_to_consumer_transaction)
            elif payment_data['payment_type'] == 'mobile_checkout':
                # verify request
                try:
                    validate_request(
                        instance=payment_data,
                        schema=payment.africas_talking_checkout_json_schema)

                except ValidationError as error:
                    response, status_code = invalid_request_on_validation(error.message)
                    return response, status_code

                mobile_checkout_transaction = payments.create_mobile_checkout_transaction(
                    payment_data['amount'],
                    payment_data['phone_number'],
                    payment_data['product_name'],
                    payment_data['currency_code'],
                    payment_data['metadata'],
                    payment_data['provider_channel']
                )
                payments.initiate_mobile_checkout_transaction(mobile_checkout_transaction)
            else:
                response, status_code = invalid_payment_type(payment_data['payment_type'])
                return make_response(jsonify(response), status_code)
        elif payment_data['provider_type'] == 'daraja':
            print('Daraja')
        else:
            response, status_code = invalid_provider_type(payment_data['provider_type'])
            return make_response(jsonify(response), status_code)


payment_view = PaymentAPI.as_view("payment")

payment_blueprint.add_url_rule(
    "/payment/", view_func=payment_view, methods=["POST"]
)
