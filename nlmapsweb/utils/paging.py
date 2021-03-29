import math

from flask import url_for


def make_paging_info(current_page, page_size, object_count, view_name,
                     request_args, page_arg_name='page'):
    page_count = math.ceil(object_count / page_size)
    urls = []
    for page in range(1, page_count + 1):
        args = {**request_args, page_arg_name: page}
        urls.append(url_for(view_name, **args))

    paging_info = {
        'current_page': current_page,
        'page_size': page_size,
        'object_count': object_count,
        'page_count': page_count,
        'urls': urls,
    }

    return paging_info

