# -*- coding: utf-8 -*-

import datetime
import random

from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import serializers, status

import apps.message.api.frontend.serializers
from apps.message.models import MessageProfileAssignment
from ... import models
from web.drf import exceptions as django_api_exception
from web import exceptions as django_exception
from web.api.views import JWTPayloadMixin, daterange, get_first_last_dates_of_month_and_year
from web.api.serializers import DynamicFieldsModelSerializer

User = get_user_model()


class UserSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.user_response_include_fields
        return super(UserSerializer, self).get_field_names(*args, **kwargs)


class PreferenceSerializer(
        serializers.ModelSerializer):
    class Meta:
        model = models.Preference
        fields = '__all__'


class PreferenceEditSerializer(
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Preference
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        preference = self.profile.edit_preference(validated_data)
        return preference

class TalkSerializer(
        DynamicFieldsModelSerializer):
    content_type_name = serializers.ReadOnlyField(source="get_content_type_model")
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Talk
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])


    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.talk_response_include_fields
        return super(TalkSerializer, self).get_field_names(*args, **kwargs)

    def get_unread_count(self, obj):
        view = self.get_view
        if view:
            self.request = view.request
            payload = view.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            # if obj.content_type.name == 'project':
            #     project_id = obj.object_id
            # else:
            #     company_id = obj.object_id
            counter = MessageProfileAssignment.objects.filter(profile=self.profile, read=False, message__talk=obj).count()
            return counter
        return 0

class CompanySerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    projects_count = serializers.ReadOnlyField(source='get_projects_count')
    messages_count = serializers.ReadOnlyField(source='get_messages_count')
    tags_count = serializers.ReadOnlyField(source='get_tags_count')
    followers_count = serializers.ReadOnlyField(source='get_followers_count')
    staff_count = serializers.ReadOnlyField(source='get_staff_count')
    partnerships_count = serializers.ReadOnlyField(source='get_partnerships_count')
    is_sponsor = serializers.ReadOnlyField(source='get_is_sponsor')
    followed = serializers.SerializerMethodField(read_only=True)
    partnership = serializers.SerializerMethodField(read_only=True)
    can_access_files = serializers.SerializerMethodField(read_only=True)
    can_access_chat = serializers.SerializerMethodField(read_only=True)
    color_project = serializers.SerializerMethodField()
    talks = TalkSerializer(many=True)
    last_message_created = serializers.SerializerMethodField()

    class Meta:
        model = models.Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.company_response_include_fields
        return super(CompanySerializer, self).get_field_names(*args, **kwargs)

    def get_last_message_created(self, obj):
        talk = obj.talks.last()
        try:
            if talk:
                return talk.messages.all().last().date_create
        except Exception:
            pass
        return None

    def get_color_project(self, obj):
        obj_color = obj.projectcompanycolorassignment_set.all().filter(project=self.context['view'].kwargs['pk'])
        if obj_color:
            return obj_color[0].color
        else:
            return None
    def get_can_access_files(self, obj):
        payload = self.get_payload()
        # Todo: Under review
        try:
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if self.profile:
                return self.profile.can_access_files
            else:
                return 0
        except:
            return 0

    def get_can_access_chat(self, obj):
        payload = self.get_payload()
        # Todo: Under review
        try:
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if self.profile:
                return self.profile.can_access_chat
            else:
                return 0
        except:
            return 0

    def get_followed(self, obj):
        payload = self.get_payload()
        # Todo: Under review
        try:
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if self.profile:
                follows = obj.request_favourites.filter(company=self.profile.company)
                if follows:
                    status = follows.filter(approval_date__isnull=False, refuse_date__isnull=True)
                    if status:
                        return 1
                    is_waiting = follows.filter(approval_date__isnull=True, refuse_date__isnull=True)
                    if is_waiting:
                        return 2
                return 0
        except:
            return 0

    def get_partnership(self, obj):
        payload = self.get_payload()
        # Todo: Under review
        try:
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if self.profile:
                partnerships = self.profile.company.request_partnerships.filter(inviting_company=obj)
                if partnerships:
                    status = partnerships.filter(approval_date__isnull=False, refuse_date__isnull=True)
                    if status:
                        return 1
                    is_waiting = partnerships.filter(approval_date__isnull=True, refuse_date__isnull=True)
                    if is_waiting:
                        return 2
                return 0
        except:
            return 0

class PartnershipSerializer(
        DynamicFieldsModelSerializer):
    guest_company = CompanySerializer()
    inviting_company = CompanySerializer()

    class Meta:
        model = models.Partnership
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.partnership_response_include_fields
        return super(PartnershipSerializer, self).get_field_names(*args, **kwargs)


class PartnershipAddSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    guest_company = CompanySerializer()

    class Meta:
        model = models.Partnership
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def to_internal_value(self, data):
        data = {
            'guest_company': models.Company.objects.get(
                id=self.request.parser_context['kwargs']['pk']
            )
        }
        return data

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.partnership_request_include_fields
        return super(PartnershipAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            partnership = self.profile.create_partnership(validated_data['guest_company'])
            return partnership
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class PartnershipAcceptSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):
    guest_company = CompanySerializer()

    class Meta:
        model = models.Partnership
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def to_internal_value(self, data):
        data = {
            'guest_company': models.Company.objects.get(
                id=self.request.parser_context['kwargs']['pk']
            )
        }
        return data

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.partnership_request_include_fields
        return super(PartnershipAcceptSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        try:
            partnership = self.profile.accept_partnership(validated_data['guest_company'])
            return partnership
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class PartnershipRefuseSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):
    guest_company = CompanySerializer()

    class Meta:
        model = models.Partnership
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def to_internal_value(self, data):
        data = {
            'guest_company': models.Company.objects.get(
                id=self.request.parser_context['kwargs']['pk']
            )
        }
        return data

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.partnership_request_include_fields
        return super(PartnershipRefuseSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        try:
            partnership = self.profile.refuse_partnership(validated_data['guest_company'])
            return partnership
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class CompanyAddSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.company_request_include_fields
        return super(CompanyAddSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'ssn' not in attrs and 'vat_number' not in attrs:
            raise serializers.ValidationError({
                'ssn': _('Please provide either SSN or Vat Number'),
                'vat_number':  _('Please provide either SSN or Vat Number')
            })
        return attrs

    def create(self, validated_data):
        try:
            main_profile = self.request.user.get_main_profile()
            company, profile = main_profile.create_company(validated_data)
            return company
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class CompanyEditSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.company_request_include_fields
        return super(CompanyEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        company = self.profile.edit_company(validated_data)
        return company


class CompanyEnableSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.company_request_include_fields
        return super(CompanyEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        company = self.profile.enable_company()
        return company


class CompanyDisableSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.company_request_include_fields
        return super(CompanyDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        company = self.profile.disable_company()
        return company


class ProfileSerializer(
        DynamicFieldsModelSerializer):
    role = serializers.ReadOnlyField(source="get_role")
    company = CompanySerializer()
    user = UserSerializer()
    is_main = serializers.SerializerMethodField()
    talk_count = serializers.SerializerMethodField()
    is_external = serializers.SerializerMethodField()

    class Meta:
        model = models.Profile
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_response_include_fields
        return super(ProfileSerializer, self).get_field_names(*args, **kwargs)

    def get_is_main(self, obj):
        return obj.is_main

    def get_talk_count(self, obj):
        return obj.talks.count()

    def get_is_external(self, obj):
        payload = self.context['view'].get_payload()
        profile = self.context['request'].user.get_profile_by_id(payload['extra']['profile']['id'])
        if obj in profile.company.profiles.company_invitation_approve():
            return False
        else:
            return True


class MainProfileAddSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(MainProfileAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            profile = self.request.user.create_main_profile(validated_data)
            return profile
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ProfileInvitationAddSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileInvitationAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            # main_profile = self.request.user.get_main_profile()
            # company_profile = main_profile.create_company_profile(validated_data)
            # return company_profile
            user = validated_data['company'].profiles.order_by('date_create').first().user
            main_profile = user.get_main_profile()
            company_profile = main_profile.create_company_profile(validated_data)
            return company_profile
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ProfileAddSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            generic_profile = self.profile
            if not 'user' in validated_data:
                if not 'email' in validated_data:
                    # Phantom creation
                    profile = generic_profile.create_phantom(validated_data)
                else:
                    main_profile = models.get_main_profile_by_email(validated_data['email'])
                    if not main_profile:
                        profile = generic_profile.create_phantom(validated_data)
                    else:
                        if validated_data['role'] == settings.OWNER:
                            profile = generic_profile.create_owner(main_profile[0], validated_data)
                        elif validated_data['role'] == settings.DELEGATE:
                            profile = generic_profile.create_delegate(main_profile[0], validated_data)
                        elif validated_data['role'] == settings.LEVEL_1:
                            profile = generic_profile.create_level1(main_profile[0], validated_data)
                        elif validated_data['role'] == settings.LEVEL_2:
                            profile = generic_profile.create_level2(main_profile[0], validated_data)

            else:
                # request_user = self.request.user.get_user_by_id(validated_data['user'])
                request_user_profile = validated_data['user'].get_main_profile()

                if validated_data['role'] == settings.OWNER:
                    profile = generic_profile.create_owner(request_user_profile, validated_data)
                elif validated_data['role'] == settings.DELEGATE:
                    profile = generic_profile.create_delegate(request_user_profile, validated_data)
                elif validated_data['role'] == settings.LEVEL_1:
                    profile = generic_profile.create_level1(request_user_profile, validated_data)
                elif validated_data['role'] == settings.LEVEL_2:
                    profile = generic_profile.create_level2(request_user_profile, validated_data)
            return profile
        except Exception as err:
            raise django_api_exception.ProfileAPIAlreadyExists(
                str(status.HTTP_500_INTERNAL_SERVER_ERROR), self.request,
                _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ProfileEditSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            if payload['extra']:
                self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        try:
            try:
                generic_profile = self.request.user.get_profile_by_id(instance.id)
            except:
                generic_profile = instance

            validated_data['id'] = instance.id
            profile = generic_profile.edit_profile(validated_data)
            return profile
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                str(status.HTTP_500_INTERNAL_SERVER_ERROR), self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ProfileEnableSerializer(
    JWTPayloadMixin,
    DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            staff_list = profile.list_approve_profiles_inactive()
            profile_to_enable = staff_list.filter(id=instance.id)
            if profile_to_enable:
                profile = profile_to_enable[0].enable_profile()
            return profile
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ProfileDisableSerializer(
    JWTPayloadMixin,
    DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            staff_list = profile.list_approve_profiles()
            profile_to_disable = staff_list.filter(id=instance.id)
            if profile_to_disable:
                profile = profile_to_disable[0].disable_profile()
            return profile
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ProfileAcceptInvitationEditSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileAcceptInvitationEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        # instance.user = self.request.user.pk
        if instance.company_invitation_date:
            instance.profile_invitation_date = datetime.datetime.now()
        elif instance.profile_invitation_date:
            instance.company_invitation_date = datetime.datetime.now()
        instance.save()
        return instance


class ProfileReAcceptInvitationEditSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileReAcceptInvitationEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        # instance.user = self.request.user.pk
        if instance.invitation_refuse_date:
            instance.invitation_refuse_date = None
            if instance.company_invitation_date:
                instance.profile_invitation_date = datetime.datetime.now()
            elif instance.profile_invitation_date:
                instance.company_invitation_date = datetime.datetime.now()
            instance.save()
        return instance


class ProfileChangeShowroomVisibilitySerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileChangeShowroomVisibilitySerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        if instance.is_in_showroom:
            instance.is_in_showroom = False
        else:
            instance.is_in_showroom = True
        instance.save()
        return instance


class ProfileChangeComunicaVisibilitySerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileChangeComunicaVisibilitySerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        if instance.is_shared:
            instance.is_shared = False
        else:
            instance.is_shared = True
        instance.save()
        return instance


class ProfileRefuseInvitationEditSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.profile_request_include_fields
        return super(ProfileRefuseInvitationEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        # instance.user = self.request.user.pk
        instance.invitation_refuse_date = datetime.datetime.now()
        instance.save()
        # instance.get_token()
        return instance


class ProfileStatusSerializer(
        serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = '__all__'


class ProfileActivitySerializer(
        DynamicFieldsModelSerializer):
    # to fix circular import

    company = CompanySerializer()
    days_for_gantt = serializers.SerializerMethodField(source='get_days_for_gantt')

    class Meta:
        model = models.Profile
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            if 'month' in view.kwargs: self.month =  view.kwargs['month']
            if 'year' in view.kwargs: self.year =  view.kwargs['year']
            return view.profile_response_include_fields
        return super(ProfileActivitySerializer, self).get_field_names(*args, **kwargs)

    def get_is_main(self, obj):
        return obj.is_main

    def get_days_for_gantt(self, obj):
        # Todo: Under Review
        days = {}
        date_from, date_to = get_first_last_dates_of_month_and_year(self.month, self.year)
        start_date, end_date = (date_from, date_to)
        query = (
            Q(datetime_start__gte=date_from, datetime_start__lte=date_to)
            | Q(datetime_start__lt=date_from, datetime_end__gte=date_from)
        )

        for activity in obj.activities.filter(query).distinct():
            if activity.datetime_start.month == date_from.month: start_date = activity.datetime_start
            if activity.datetime_end.month == date_from.month: end_date = activity.datetime_end

            if isinstance(start_date, datetime.datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.date()
                
            for dt in daterange(start_date, end_date):
                if not dt.day in days.keys():
                    days[dt.day] = {}
                if not activity.task.project.id in days[dt.day].keys():
                    days[dt.day][activity.task.project.id] = []
                days[dt.day][activity.task.project.id].append({'activity': activity.title, 'project': activity.task.project.name})
        return days


class FavouriteSerializer(
        DynamicFieldsModelSerializer):
    company = CompanySerializer()
    company_followed = CompanySerializer()

    class Meta:
        model = models.Favourite
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.favourite_response_include_fields
        return super(FavouriteSerializer, self).get_field_names(*args, **kwargs)


class FavouriteAcceptSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):

    class Meta:
        model = models.Favourite
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.favourite_request_include_fields
        return super(FavouriteAcceptSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        try:
            favourite = self.profile.accept_follower(validated_data['company'])
            return favourite
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class SetFavouriteSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):

    class Meta:
        model = models.Favourite
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.favourite_request_include_fields
        return super(SetFavouriteSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            favourite = self.profile.follow_company(validated_data['company'])
            return favourite
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class SponsorSerializer(
    DynamicFieldsModelSerializer):

    company = CompanySerializer()

    class Meta:
        model = models.Sponsor
        fields = '__all__'


class SponsorAddSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):

    class Meta:
        model = models.Sponsor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def to_internal_value(self, data):
        if 'pk' in self.request.parser_context['kwargs'].keys():
            company = models.Company.objects.get(id=self.request.parser_context['kwargs']['pk'])
        else:
            company = models.Company.objects.get(id=self.profile.company.id)
        data['company'] = company
        data['status'] = 2
        return data

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.sponsor_request_include_fields
        return super(SponsorAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            if 'pk' in self.request.parser_context['kwargs'].keys():
                main_profile = self.profile.get_main_profile()
                sponsor = main_profile.create_sponsor_request(validated_data)
            else:
                sponsor = self.profile.create_sponsor_request(validated_data)
            return sponsor
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class SponsorEditSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):

    class Meta:
        model = models.Sponsor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.sponsor_request_include_fields
        return super(SponsorEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        main_profile = self.profile.get_main_profile()
        sponsor = main_profile.edit_sponsor(validated_data)
        return sponsor