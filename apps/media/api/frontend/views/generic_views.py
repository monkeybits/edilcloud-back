# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import views, permissions, status
from django.utils.translation import ugettext_lazy as _

from apps.media import models
from web.api.views import DownloadViewMixin
from web.drf import exceptions as django_api_exception


class PublicVideoDownloadView(
        DownloadViewMixin, views.APIView):
    """
    Download a document
    """
    permission_classes = (permissions.AllowAny,)
    file_field_name = 'video'

    def get_object(self):
        try:
            video_id = (self.kwargs.get('pk', None))
            video = models.Video.objects.get(id=video_id, is_public=True)
            return video
        except ObjectDoesNotExist as err:
            raise django_api_exception.VideoAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )
