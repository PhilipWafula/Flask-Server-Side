# system imports

# third party imports
from flask import Blueprint, request, jsonify, make_response
from flask.views import MethodView

# application imports
from app.server import app_logger, db
from app.server.models.mpesa_transaction import MPesaTransaction
from app.server.utils.enums.transaction_enums import MpesaTransactionStatus

africas_talking_payment_validation_blueprint = Blueprint('africas_talking_payment_validation', __name__)


class PaymentValidationAPI(MethodView):
    """
    Callback endpoint for payment validations
    """
    def post(self):
        validation_data = request.get_json()

        # get africas talking validation data
        service_provider_transaction_id = validation_data.get('transactionId')
        phone_number = validation_data.get('phoneNumber')
        amount = validation_data.get('amount')

        try:
            # get initiated transaction.
            transaction = MPesaTransaction.query.filter_by(
                service_provider_transaction_id=service_provider_transaction_id).first()

            # validate transaction
            if transaction and transaction.destination_account == phone_number and transaction.amount == amount:
                response = {
                    'status': 'Validated'
                }
            else:
                response = {
                    'status': 'Failed'
                }

            return make_response(jsonify(response))
        except Exception as exception:
            app_logger.error(
                f'There was an error validating transaction: {service_provider_transaction_id}. Error:{exception}')


class PaymentNotificationsAPI(MethodView):
    """
    Callback endpoint for payment notifications
    """
    def post(self):
        payment_data = request.get_json()

        # get relevant transaction data
        # B2C
        service_provider_transaction_id = payment_data.get('transactionId')
        status = payment_data.get('status')
        status_description = payment_data.get('description')
        amount = float(payment_data.get('value').lstrip('KES '))

        try:
            # find transaction and confirm its status
            transaction = MPesaTransaction.query.get(service_provider_transaction_id=service_provider_transaction_id)

            if transaction and transaction.amount == amount:
                # update transaction status
                if status == 'Success':
                    transaction.status = MpesaTransactionStatus.COMPLETE
                else:
                    transaction.status = MpesaTransactionStatus.FAILED

                # update status description
                transaction.status_description = status_description

            db.session.add(transaction)
            db.session.commit()
        except Exception as exception:
            app_logger.error(
                f'There was an error confirming transaction: {service_provider_transaction_id}. Error:{exception}')


africas_talking_payment_validation_view = PaymentValidationAPI.as_view('africas_talking_payment_validation_view')
africas_talking_payment_notification_view = PaymentNotificationsAPI.as_view('africas_talking_payment_notification_view')

africas_talking_payment_validation_blueprint.add_url_rule(
    '/africas_talking/validate_payment/',
    view_func=africas_talking_payment_validation_view,
    methods=["POST"]
)

africas_talking_payment_validation_blueprint.add_url_rule(
    '/africas_talking/confirm_payment/',
    view_func=africas_talking_payment_notification_view,
    methods=["POST"]
)
