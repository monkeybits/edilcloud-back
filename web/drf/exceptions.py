# -*- coding: utf-8 -*-
"""
Whistle APIExceptions tree
+-- APIException (DRF)
    +-- WhistleAPIException
"""

import logging

from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.views import exception_handler


# API EXCEPTION HANDLER
def whistle_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


# GENERIC CUSTOM API EXCEPTION
class WhistleAPIException(APIException):
    """
    To import:
        from web.drf import exceptions

    To raise:
        from rest_framework import status

        raise exceptions.WhistleAPIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request=request,
            msg='text of error',
        )
    """

    def __init__(self, status_code, request, msg=None, write_log=True):
        """
        :param status_code: HTTP status code
        :param request: view's request
        :param msg: error description
        :param write_log: if true a log is written in /var/log/django/whistle-api_exceptions.log
        """
        self.logger = logging.getLogger('api_exceptions')
        self.status_code = status_code
        self.request = request
        if type(self.request) == Request:
            # if request is DRF-request then self.request = DJANGO-request
            self.request = self.request._request
        self.http_method = request.method

        super(WhistleAPIException, self).__init__(msg)
        if write_log:
            log_string = """{detail}\nurl: {url}\nmethod: {method}\nuser: {user}\ndata: {data}\n""".format(
                detail=self.detail,
                url=request.get_full_path(),
                method=getattr(request, 'method', ''),
                user=getattr(request, 'user', ''),
                data=getattr(request, 'data', ''),
            )
            self.logger.error(log_string)

    def get_repr_str(self):
        repr_str = u''
        if self.http_method:
            repr_str += '{} '.format(self.http_method.upper())
        repr_str += u'{} {}'.format(self.status_code, self.default_detail)
        return repr_str

    def __str__(self):
        return repr(self.get_repr_str())

    def __repr__(self):
        return repr(self.get_repr_str())


# CUSTOM EXCEPTIONS
class YourCustomAPIException(WhistleAPIException):
    """
    To import:
        from web.drf import exceptions

    To raise:
        raise exceptions.YourCustomAPIException('text of error')

    To capture:
        try:
            [code]
        except exceptions.YourCustomAPIException as e:
            [code]
    """
    pass


class UserAPIDoesNotExist(WhistleAPIException):
    pass


class PreferenceAPIDoesNotExist(WhistleAPIException):
    pass


class TrackingAPIPermissionDenied(WhistleAPIException):
    pass


class ProfileAPIException(WhistleAPIException):
    pass


class ProfileAPIDoesNotExist(ProfileAPIException):
    pass


class ProfileAPIAlreadyExists(ProfileAPIException):
    pass


class ProfileAPIDoesNotMatch(ProfileAPIException):
    pass


class MainProfileAPIDoesNotExist(ProfileAPIException):
    pass


class CompanyAPIException(WhistleAPIException):
    pass


class CompanyAPIDoesNotExist(CompanyAPIException):
    pass


class ProjectCloneAPIPermissionDenied(WhistleAPIException):
    pass


class ProjectAPIDoesNotExist(WhistleAPIException):
    pass


class ProjectMemberAddAPIPermissionDenied(WhistleAPIException):
    pass


class TeamAPIDoesNotExist(WhistleAPIException):
    pass


class TaskAPIDoesNotExist(WhistleAPIException):
    pass

class PostAPIDoesNotExist(WhistleAPIException):
    pass

class CertificationAPIDoesNotExist(WhistleAPIException):
    pass


class OfferAPIDoesNotExist(WhistleAPIException):
    pass


class BomAPIDoesNotExist(WhistleAPIException):
    pass


class BomRowAPIDoesNotExist(WhistleAPIException):
    pass


class QuotationAPIDoesNotExist(WhistleAPIException):
    pass


class QuotationRowAPIDoesNotExist(WhistleAPIException):
    pass


class DocumentAPIDoesNotExist(WhistleAPIException):
    pass


class PhotoAPIDoesNotExist(WhistleAPIException):
    pass


class VideoAPIDoesNotExist(WhistleAPIException):
    pass


class FavouriteAPIDoesNotExist(WhistleAPIException):
    pass


class TaskActivityAPIDoesNotExist(WhistleAPIException):
    pass


class TaskActivityAddAPIPermissionDenied(WhistleAPIException):
    pass


class TaskActivityEditAPIPermissionDenied(WhistleAPIException):
    pass


class MessageAPIDoesNotExist(WhistleAPIException):
    pass


class TalkAPIDoesNotExist(WhistleAPIException):
    pass


class NotificationAPIDoesNotExist(WhistleAPIException):
    pass
