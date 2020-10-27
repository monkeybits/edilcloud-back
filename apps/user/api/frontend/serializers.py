# -*- coding: utf-8 -*-

import datetime as dt
from calendar import timegm
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework import serializers

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import VerificationBaseSerializer, JSONWebTokenSerializer

User = get_user_model()

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


class TokenRefreshAPISerializer(
        VerificationBaseSerializer):
    """
    Refresh an access token.
    """

    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        profile_id = self.context['profile_id']

        try:
            role = user.get_profile_by_id(profile_id).role
            company_obj = user.get_profile_by_id(profile_id).company
            company = company_obj.id if company_obj else company_obj
        except:
            msg = _('You are the owner of the profile')
            raise serializers.ValidationError(msg)

        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')
        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, dt.timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _('Refresh has expired.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('orig_iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_payload['orig_iat'] = orig_iat
        new_payload['extra'] = {
            'profile':
                {
                    'id': profile_id,
                    'role': role,
                    'company': company,
                }
        }

        return {
            'token': jwt_encode_handler(new_payload),
            'user': user
        }


class RegisterSerializer(
        serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=50,
        min_length=2,
        required=True
    )
    email = serializers.EmailField(
        required=True
    )
    password1 = serializers.CharField(
        write_only=True
    )
    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def check_email_address_exists(self, email):
        user = User.objects.filter(email__iexact=email).exists()
        return user

    def check_username_exists(self, username):
        user = User.objects.filter(username__iexact=username).exists()
        return user

    def validate_email(self, email):
        if email and self.check_email_address_exists(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."))
        return email

    def validate_username(self, username):
        if username and self.check_username_exists(username):
            raise serializers.ValidationError(
                _("A user is already registered with this username."))
        return username

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', ''),
            'is_active': False
        }

    def create(self, validated_data):
        user = User.objects.create(**self.get_cleaned_data())
        password = validated_data.get('password1', '')
        user.set_password(password)
        user.save()
        return user


class CustomLoginJWTSerializer(
        JSONWebTokenSerializer):
    username_field = 'username_or_email'

    def validate(self, attrs):
        password = attrs.get("password")
        user_obj = User.objects.filter(
            email=attrs.get("username_or_email")
        ).first() or User.objects.filter(
            username=attrs.get("username_or_email")
        ).first()
        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': password
            }
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = _('User account is disabled.')
                        raise serializers.ValidationError(msg)

                    payload = jwt_payload_handler(user)
                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user
                    }
                else:
                    msg = _('Unable to log in with provided credentials.')
                    raise serializers.ValidationError(msg)

            else:
                msg = _('Must include "{username_field}" and "password".')
                msg = msg.format(username_field=self.username_field)
                raise serializers.ValidationError(msg)

        else:
            msg = _('Account with this email/username does not exists')
            raise serializers.ValidationError(msg)