from dateutil import parser
from flask import request


def paginate_query(query, queried_object=None, order_override=None):
    """
    Paginates an sqlalchemy query, gracefully managing missing queries.
    Default ordering is to show most recently created first.
    Unlike raw paginate, defaults to showing all results if args aren't supplied

    :param query: base query
    :param queried_object: underlying object being queried. Required to sort most recent
    :param order_override: override option for the sort parameter.
    :returns: tuple of (item list, total number of items, total number of pages)
    """

    updated_after = request.args.get('updated_after')
    page = request.args.get('page')
    per_page = request.args.get('per_page')

    if updated_after:
        parsed_time = parser.isoparse(updated_after)
        query = query.filter(queried_object.updated_at > parsed_time)

    if order_override:
        query = query.order_by(order_override)
    elif queried_object:
        query = query.order_by(queried_object.created_at.desc())

    if per_page is None:

        items = query.all()

        return items, len(items), 1

    if page is None:
        per_page = int(per_page)
        paginated = query.paginate(0, per_page, error_out=False)

        return paginated.items, paginated.total, paginated.pages

    per_page = int(per_page)
    page = int(page)

    paginated = query.paginate(page, per_page, error_out=False)

    return paginated.items, paginated.total, paginated.pages
