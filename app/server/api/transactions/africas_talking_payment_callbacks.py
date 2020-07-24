# system imports

# third party imports
from flask import Blueprint, request
from flask.views import MethodView

# application imports

africas_talking_payment_validation_blueprints = Blueprint('africas_talking_payment_validation', __name__)


class PaymentValidationAPI(MethodView):
    """
    Callback endpoint for payment notifications
    """
    def post(self):
        validation_data = request.get_json()

        # get africas talking validation data
        validation_data.get('provider')
        validation_data.get('clientAccount')
        validation_data.get('productName')
        validation_data.get('phoneNumber')
        validation_data.get('value')
        validation_data.get('providerMetadata')


africas_talking_payment_validation_view = PaymentValidationAPI.as_view('africas_talking_payment_validation_view')

africas_talking_payment_validation_blueprints.add_url_rule(
    "/africas_talking/validate_payment/",
    view_func=africas_talking_payment_validation_view,
    methods=["POST"]
)