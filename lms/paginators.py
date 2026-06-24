from rest_framework.pagination import PageNumberPagination

class StandardResultsPagination(PageNumberPagination):
    page_size = 5                    # можно 10-15
    page_size_query_param = 'page_size'
    max_page_size = 50