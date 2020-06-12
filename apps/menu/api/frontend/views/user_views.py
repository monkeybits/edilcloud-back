# -*- coding: utf-8 -*-

from rest_framework import generics

from .. import serializers
from .... import models


class MenuListView(
        generics.ListAPIView):
    """
    Get all enable menu items
    # Todo: filter active parent's, children's etc
    """
    queryset = models.Menu.objects.all()
    serializer_class = serializers.MenuSerializer
