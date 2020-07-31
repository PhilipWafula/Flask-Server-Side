# third party imports
from flask import Blueprint, jsonify, make_response
from flask.views import MethodView

# application imports
from app.server.models.mpesa_transaction import MpesaTransaction
from app.server.utils.auth import requires_auth
from app.server.utils.query import paginate_query
from app.server.schemas.mpesa_transaction import mpesa_transactions_schema

mpesa_transactions_blueprint = Blueprint("mpesa_transactions", __name__)


class MpesaTransactionAPI(MethodView):
    @requires_auth(authenticated_roles=['ADMIN'])
    def get(self):
        mpesa_transactions_query = MpesaTransaction.query.execution_options(show_all=True)
        mpesa_transactions, total_items, total_pages = paginate_query(
            mpesa_transactions_query, MpesaTransaction
        )

        if not mpesa_transactions:
            response = {
                'error': {
                    'message': 'No mpesa transactions found.',
                    'status': 'Fail'
                }
            }
            return make_response(jsonify(response), 404)

        response = {
            'data': {
                'mpesa_transactions': mpesa_transactions_schema.dump(mpesa_transactions).data
            },
            'items': total_items,
            'message': 'Successfully loaded all mpesa transactions.',
            'pages': total_pages,
            'status': 'Success'
        }
        return make_response(jsonify(response), 200)


mpesa_transactions_view = MpesaTransactionAPI.as_view("mpesa_transactions_view")


mpesa_transactions_blueprint.add_url_rule(
    "/mpesa_transactions/",
    view_func=mpesa_transactions_view,
    methods=["GET"],
)
