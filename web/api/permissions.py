# -*- coding: utf-8 -*-

from rest_framework import permissions

from web.api.views import JWTPayloadMixin


class GenericListPermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': [
            '%(app_label)s.list_%(model_name)s',
            '%(app_label)s.list_own_%(model_name)s',
        ],
        'OPTIONS': [],
    }


class GenericDetailPermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': [
            '%(app_label)s.detail_%(model_name)s',
            '%(app_label)s.detail_own_%(model_name)s',
        ],
        'OPTIONS': [],
    }


class GenericDisablePermission(permissions.DjangoModelPermissions):
    perms_map = {
        'PUT': ['%(app_label)s.disable_%(model_name)s'],
        'OPTIONS': [],
    }


class ThuxModelPermissions(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': [
            '%(app_label)s.list_%(model_name)s',
        ],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class RoleAccessPermission(JWTPayloadMixin, permissions.BasePermission):
    message = "You do not have role permission to perform this action."

    def get_extra_payload_or_404(self):
        try:
            payload = self.get_payload()
            return payload['extra']
        except:
            return None

    def has_permission(self, request, view):
        self.request = request
        permission_roles = getattr(view, 'permission_roles', ())

        if not self.request.user.is_authenticated:
            return False

        payload = self.get_extra_payload_or_404()
        if payload and payload['profile']['role'] in permission_roles:
            return True
        return False


class IsAuthenticatedAndOwnerPermission(permissions.BasePermission):
    """
    This class is completely different to RoleAccessPermission.
    Because, here we don't deal with the tracker and moreover,
    we would verifies only obj owner with request user.
    PS: Main profile selection doesn't track, since main profile
    doesn't belong to any company.
    """
    message = 'You must be the owner to perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
