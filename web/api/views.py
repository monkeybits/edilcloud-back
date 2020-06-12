# -*- coding: utf-8 -*-

import magic
import os
import json
import datetime
import calendar
from datetime import timedelta

from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings

from wsgiref.util import FileWrapper

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class QuerysetMixin(object):

    def get_filters(self):
        filters = dict()
        for key, value in self.request.GET.items():
            if key.startswith('filter__'):
                key = key[8:]
                if key.endswith('__isnull'):
                    filters[key] = json.loads(value.lower())
                elif key.endswith('__in'):
                    filters[key] = value.split(',')[:-1]
                else:
                    filters[key] = value
        return filters

    def get_excludes(self):
        excludes = dict()
        for key, value in self.request.GET.items():
            if key.startswith('exclude__'):
                key = key[9:]
                if key.endswith('__isnull'):
                    excludes[key] = json.loads(value.lower())
                elif key.endswith('__in'):
                    excludes[key] = value.split(',')[:-1]
                else:
                    excludes[key] = value
        return excludes

    def get_order_by(self):
        order_by = list()
        for key, value in self.request.GET.items():
            if key.startswith('order_by__'):
                # key = key[10:]
                order_by.append(value)
        return order_by

    def get_queryset(self):
        filters = self.get_filters()
        excludes = self.get_excludes()
        order_by = self.get_order_by()
        queryset = super(QuerysetMixin, self).get_queryset()
        if filters:
            if isinstance(filters, dict):
                queryset = queryset.filter(**filters)
            else:
                queryset = queryset.filter(filters)
        if excludes:
            queryset = queryset.exclude(**excludes)
        if order_by:
            queryset = queryset.order_by(*order_by).distinct()
        return queryset

    @property
    def paginator(self):
        if self.request.query_params.get('no_page'):
            self.pagination_class = None
        return super(QuerysetMixin, self).paginator


class StatusUpdateViewMixin(object):

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = self.new_status
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        if not request.data._mutable:
            request.data._mutable = True
        request.data['status'] =  self.new_status
        return self.partial_update(request, *args, **kwargs)


class JWTPayloadMixin(object):

    def get_payload(self):
        token = self.request.META['HTTP_AUTHORIZATION'].split()[1]
        return jwt_decode_handler(token)


class WhistleGenericViewMixin(object):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_serializer = serializer.save()
        self.set_output_serializer()
        output_serializer = self.get_serializer(input_serializer)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.set_output_serializer()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        input_serializer = serializer.save()
        self.set_output_serializer()
        output_serializer = self.get_serializer(input_serializer)
        return Response(output_serializer.data)


class DownloadViewMixin(object):

    # attribute model with file field
    file_field_name = 'file_content'

    def get(self, request, *args, **kwargs):
        file = getattr(self.get_object(), self.file_field_name)
        return self.create_download_response(file.path)

    def create_download_response(self, path_file):
        if os.path.exists(path_file):
            with open(path_file, 'rb') as file:
                content_type = magic.from_file(path_file, mime=True)
                response = HttpResponse(FileWrapper(file), content_type=content_type)
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(file.name))
            return response

        return Response({'error': "{}".format(_('attachment not found'))}, status=status.HTTP_400_BAD_REQUEST)


class ArrayFieldInMultipartMixin(object):

    def get_array_from_string(self, data):
        for field_name in self.get_field_names():
            if field_name in data:
                if self.Meta.model._meta.get_field(field_name).get_internal_type() == 'ArrayField':
                    new_data = []
                    for element in data[field_name]:
                        new_data += element.split(',')
                    data[field_name] = new_data
        return data


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def get_first_last_dates_of_month_and_year(month, year):
    if not month or not year:
        return None, None

    d_fmt = "{0:>02}.{1:>02}.{2}"
    date_from = datetime.datetime.strptime(
        d_fmt.format(1, month, year), '%d.%m.%Y').date()
    last_day_of_month = calendar.monthrange(int(year), int(month))[1]
    date_to = datetime.datetime.strptime(
        d_fmt.format(last_day_of_month, month, year), '%d.%m.%Y').date()
    return date_from, date_to


def get_media_root(public):
    if public:
        return 'media'
    return 'media_private'
