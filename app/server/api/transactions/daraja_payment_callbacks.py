# system imports

# third party imports
from flask import Blueprint, request
from flask.views import MethodView

# application imports

daraja_payment_validation_blueprints = Blueprint('daraja_payment_validation', __name__)


class PaymentValidationAPI(MethodView):
    """
    Callback endpoint for payment validation
    """
    def post(self):
        validation_data = request.get_json()

        # get daraja validation data
        validation_data.get('TransactionType')
        validation_data.get('TransID')
        validation_data.get('TransTime')
        validation_data.get('TransAmount')
        validation_data.get('BusinessShortCode')
        validation_data.get('BillRefNumber')
        validation_data.get('InvoiceNumber')
        validation_data.get('OrgAccountBalance')
        validation_data.get('ThirdPartyTransID')
        validation_data.get('MSISDN')
        validation_data.get('FirstName')
        validation_data.get('MiddleName')
        validation_data.get('LastName')


class PaymentConfirmationAPI(MethodView):
    """
    Callback endpoint for payment confirmation
    """
    def post(self):
        daraja_data = request.get_json()

        # get daraja validation data
        daraja_data.get('TransactionType')
        daraja_data.get('TransID')
        daraja_data.get('TransTime')
        daraja_data.get('TransAmount')
        daraja_data.get('BusinessShortCode')
        daraja_data.get('BillRefNumber')
        daraja_data.get('InvoiceNumber')
        daraja_data.get('OrgAccountBalance')
        daraja_data.get('ThirdPartyTransID')
        daraja_data.get('MSISDN')
        daraja_data.get('FirstName')
        daraja_data.get('MiddleName')
        daraja_data.get('LastName')


daraja_payment_validation_view = PaymentValidationAPI.as_view('daraja_payment_validation_view')
daraja_payment_confirmation_view = PaymentValidationAPI.as_view('daraja_payment_confirmation_view')

daraja_payment_validation_blueprints.add_url_rule(
    "/daraja/validate_payment/",
    view_func=daraja_payment_validation_view,
    methods=["POST"]
)

daraja_payment_validation_blueprints.add_url_rule(
    "/daraja/confirm_payment/",
    view_func=daraja_payment_confirmation_view,
    methods=["POST"]
)
