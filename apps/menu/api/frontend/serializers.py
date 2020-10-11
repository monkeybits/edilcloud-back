# -*- coding: utf-8 -*-

from rest_framework import serializers

from ... import models


class MenuSerializer(
        serializers.ModelSerializer):
    class Meta:
        model = models.Menu
        exclude = (
            'date_create', 'date_last_modify', 'creator',
            'last_modifier',
        )
