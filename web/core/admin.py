# -*- coding: utf-8 -*-


class UserAdminMixin(object):
    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'creator_id') and not change:
            obj.creator_id = request.user.id
        if hasattr(obj, 'last_modifier_id'):
            obj.last_modifier_id = request.user.id
        super(UserAdminMixin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if hasattr(instance, 'creator_id') and instance.creator_id is None:
                instance.creator_id = request.user.id
            if hasattr(instance, 'last_modifier_id'):
                instance.last_modifier_id = request.user.id
        super(UserAdminMixin, self).save_formset(request, form, formset, change)
