# -*- coding: utf-8 -*-

from rest_framework import serializers


class DynamicFieldsModelSerializer(
        serializers.ModelSerializer):
    @property
    def get_view(self):
        try:
            if self.parent:
                view = self.parent.context['view']
            else:
                view = self.context['view']
            return view
        except:
            return None
