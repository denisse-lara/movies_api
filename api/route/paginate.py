import math

from flask import json

import config


def paginate(query, schema, page, name):
    total_pages = math.ceil(len(query.all()) / config.ROWS_PER_PAGE)
    # don't allow user to go past the last page

    if page > total_pages:
        return {"message": "No more pages.", "status_code": 404}, 404

    items = query.paginate(page=page, per_page=config.ROWS_PER_PAGE)

    results = {
        "page": page,
        "count": config.ROWS_PER_PAGE * (page - 1) + len(items.items),
        name: json.loads(schema.dumps(items.items)),
    }
    return results, 200
