from django.core.paginator import Paginator, InvalidPage, EmptyPage

def pagination_results(request, query_set, items_per_page):
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    paginator = Paginator(query_set, items_per_page)
    try:
        results_page = paginator.page(page)
    except (InvalidPage, EmptyPage):
        results_page = paginator.page(1)
    return results_page
