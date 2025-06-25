from rest_framework.pagination import PageNumberPagination, CursorPagination


class SharedPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class SharedCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"
    page_size_query_param = "page_size"
    max_page_size = 100
