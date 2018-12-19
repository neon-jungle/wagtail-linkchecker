from django.conf import settings
from django.core.paginator import Paginator, EmptyPage


def paginate(request, items, page_key='page'):
    paginator = Paginator(items, 50)

    try:
        page_number = int(request.GET[page_key])
        page = paginator.page(page_number)
    except (ValueError, KeyError, EmptyPage):
        page = paginator.page(1)

    return paginator, page
