# coding: utf-8

from collections import OrderedDict

from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class ThuxPageNumberPagination(PageNumberPagination):
    def get_last_link(self):
        url = self.request.build_absolute_uri()
        page_number = self.page.paginator.num_pages
        return replace_query_param(url, self.page_query_param, page_number)

    def get_first_link(self):
        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, 1)

    def get_paginated_response(self, data):
        next = previous = None
        if self.page.has_next():
            next = self.page.number + 1
        if self.page.has_previous():
            previous = self.page.number - 1
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('first', 1),
            ('first_link', self.get_first_link()),
            ('next', next),
            ('next_link', self.get_next_link()),
            ('current', self.page.number),
            ('previous', previous),
            ('previous_link', self.get_previous_link()),
            ('last', self.page.paginator.num_pages),
            ('last_link', self.get_last_link()),
            ('per_page', self.page.paginator.per_page),
            ('results', data)
        ]))

    def get_page_size(self, request):
        self.page_size_query_param = settings.REST_FRAMEWORK_PAGE_SIZE_QUERY_PARAM
        return super(ThuxPageNumberPagination, self).get_page_size(request)


