from bin.common.Const import OK


def render_response(status: str = OK, **kwargs):
    response = {'status': status}

    for section_key, section_value in kwargs.items():
        response[section_key] = section_value

    return response


def get_section_paginate(paginate, items):
    section_paginate = {
        "count": paginate.total,
        "pagination": {
            "page": paginate.page,
            "links": {
                "current": paginate.page,
                "first": 1,
                "last": paginate.pages,
                "previous": paginate.prev_num,
                "next": paginate.next_num
            },
            "exists": True,
            "limit": paginate.per_page
        },
        "items": items
    }

    return section_paginate


def get_section_item(item):
    section_item = {
        "item": item
    }

    return section_item
