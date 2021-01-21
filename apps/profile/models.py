# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import datetime
import os
import pathlib
import calendar
from itertools import chain

import djstripe
import stripe
from django.db import transaction
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, Count
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.utils import translation
from django.utils.encoding import python_2_unicode_compatible
from django.utils.http import int_to_base36
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from web.drf import exceptions as django_api_exception

from . import managers
# Todo: May be, use the following format: from apps.app import models as app_models
from apps.document.models import Document
from apps.media.models import Photo, Video, Folder
from apps.message.models import Talk, Message, MessageFileAssignment, MessageProfileAssignment
from apps.project.models import Project, Team, Task, Activity, \
    Post, Comment, TaskPostAssignment, MediaAssignment
from apps.quotation.models import Bom, BomRow, Offer, Certification, Quotation, QuotationRow, FavouriteOffer, \
    BoughtOffer, BomArchive, QuotationArchive
from apps.user.api.frontend.views.mixin import UserMixin, TokenGenerator as UserTokenGenerator
from web import exceptions as django_exception
from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel
from web.functions import zerofill
from web.token import TokenGenerator
from web.api.views import get_first_last_dates_of_month_and_year

User = get_user_model()


def get_upload_photo_path(instance, filename):
    media_dir = slugify(instance.last_name[0:2])
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.last_name), ext)
    return os.path.join(u"profile", u"photo", u"{0}".format(media_dir), filename)


def get_upload_logo_path(instance, filename):
    media_dir = slugify(instance.name[0:2])
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(instance.slug, ext)
    return os.path.join(u"company", u"logo", u"{0}".format(media_dir), filename)


def tracking_info_default():
    return {"tracking": True}


def profile_info_default():
    return {"profile": True}


def profile_preference_info_default():
    return settings.PROFILE_PREFERENCE_INFO_DEFAULT


def profile_preference_notification_default():
    return settings.PROFILE_PREFERENCE_NOTIFICATION_DEFAULT


def create_main_profile(self, validated_data):
    photo = None
    if 'photo' in validated_data:
        photo = validated_data['photo']
        validated_data.pop('photo')

    profile = Profile.objects.create(
        creator=self,
        last_modifier=self,
        user=self,
        email=self.email,
        company_invitation_date=datetime.datetime.now(),
        profile_invitation_date=datetime.datetime.now(),
        **validated_data
    )
    if photo:
        profile.photo.save('photo', photo)

    # Link Profiles (Phantom)
    check_profiles = Profile.objects.filter(
        email=self.email, user__isnull=True
    )
    if len(check_profiles) > 0:
        check_profiles.update(user=self)
        profile.is_invited = True
        profile.save()

    return profile


def get_main_profile(self):
    main_profiles = self.profiles.mains()
    if main_profiles:
        return main_profiles[0]
    raise django_exception.MainProfileDoesNotExist(_('Main Profile doesn\'t exit'))


def get_main_profile_by_email(email):
    return MainProfile.objects.filter(email=email)


def get_profiles(self):
    return self.profiles.all()


def get_request_profiles(self):
    return self.profiles.profile_invitation_request()


def get_waiting_profiles(self):
    return self.profiles.profile_invitation_waiting()


def get_approve_profiles(self):
    return self.profiles.profile_invitation_approve()


def get_refuse_profiles(self):
    return self.profiles.profile_invitation_refuse()


def get_all_profiles(self):
    return Profile.objects.exclude_mains()


def get_profile_by_id(self, profile_id, profile_status=1):
    """
    :param profile_id: id profile
    :param profile_status: status profile
    :return: profile instance if it is exists
    """
    profile = self.profiles.get(status=profile_status, id=profile_id)
    translation.activate(self.get_main_profile().language)
    return profile

def get_user_by_id(self, user_id):
    """
    :param user_id: id user
    :return: user instance if it is exists
    """
    return User.objects.get(id=user_id)


def send_account_verification_email(self, to_email=None, language_code=None):
    from_mail = settings.REGISTRATION_FROM_EMAIL
    if not to_email:
        to_email = self.email or self.user.email
    if not language_code:
        language_code = 'en'

    subject = 'Edilcloud Account Activation'
    if language_code == 'it':
        subject = 'Attivazione account Edilcloud'

    account_activation_token = UserTokenGenerator()
    context = {
        'logo_url': os.path.join(
            settings.PROTOCOL + '://',
            settings.BASE_URL,
            'assets/images/logos/fuse.svg'
        ),
        "first_name": self.username,
        "endpoint": os.path.join(
            settings.PROTOCOL+"://", settings.BASE_URL,
            'user-account-activation', urlsafe_base64_encode(force_bytes(self.id)),
            account_activation_token.make_token(self)
        ) + os.sep,
        "protocol": settings.PROTOCOL,
        "base_url": settings.BASE_URL
    }
    subject = "Edilcloud Account Activation"

    # Text message
    text_message = render_to_string('user/user/registration/account_{}.txt'.format(language_code), context)

    # Html message
    html_message = render_to_string('user/user/registration/account_{}.html'.format(language_code), context)
    send_mail(
        subject=subject,
        message=text_message,
        html_message=html_message,
        recipient_list=[to_email],
        from_email=from_mail,
        auth_user=from_mail,
        auth_password=settings.REGISTRATION_EMAIL_HOST_PASSWORD
    )


User.add_to_class('create_main_profile', create_main_profile)
User.add_to_class('get_main_profile', get_main_profile)
User.add_to_class('get_profiles', get_profiles)
User.add_to_class('get_request_profiles', get_request_profiles)
User.add_to_class('get_approve_profiles', get_approve_profiles)
User.add_to_class('get_refuse_profiles', get_refuse_profiles)
User.add_to_class('get_waiting_profiles', get_waiting_profiles)
User.add_to_class('get_all_profiles', get_all_profiles)
User.add_to_class('get_profile_by_id', get_profile_by_id)
User.add_to_class('get_user_by_id', get_user_by_id)
User.add_to_class('send_account_verification_email', send_account_verification_email)


@python_2_unicode_compatible
class Company(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.CompanyManager()
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_("name"),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_('slug'),
    )
    brand = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("brand"),
    )
    is_supplier = models.BooleanField(
        default=False,
        verbose_name=_('is supplier')
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )
    ssn = models.CharField(
        max_length=16,
        blank=True,
        db_index=True,
        verbose_name=_("ssn"),
    )
    vat_number = models.CharField(
        max_length=14,
        blank=True,
        db_index=True,
        verbose_name=_("vat number"),
    )
    url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("url"),
    )
    email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name=_("email"),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("phone"),
    )
    phone2 = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("phone2"),
    )
    fax = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("fax"),
    )
    logo = models.ImageField(
        blank=True,
        upload_to=get_upload_logo_path,
        verbose_name=_('logo'),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_("note"),
    )
    talks = GenericRelation(
        'message.Talk',
        blank=True, null=True,
        related_query_name='companies'
    )
    documents = GenericRelation(
        'document.Document',
        blank=True, null=True,
        related_query_name='companies'
    )
    photos = GenericRelation(
        'media.Photo',
        blank=True, null=True,
        related_query_name='companies'
    )
    videos = GenericRelation(
        'media.Video',
        blank=True, null=True,
        related_query_name='companies'
    )
    folders = GenericRelation(
        'media.Folder',
        blank=True, null=True,
        related_query_name='companies'
    )
    category = JSONField(
        default={},
        blank=True, null=True,
        verbose_name=_('category'),
        help_text=_('Company Categories'),
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("color")
    )
    customer = models.CharField(
        default='',
        max_length=255,
        blank=True
    )
    subscription = models.CharField(
        default='',
        max_length=255,
        blank=True
    )
    trial_used = models.BooleanField(
        default=False,
        verbose_name=_('has already used trial plan')
    )

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ('ordering', 'name',)
        permissions = (
            ("list_company", "can list company"),
            ("detail_company", "can detail company"),
            ("disable_company", "can disable company"),
        )
        get_latest_by = "date_create"

    def __str__(self):
        return self.name

    @classmethod
    def get_companies(cls):
        return cls.objects.filter(status=1)

    def get_invited_staff(self):
        # TODO
        pass

    def get_request_staff(self):
        # TODO
        pass

    def get_staff(self):
        return self.profiles.all()

    def get_active_staff(self):
        return self.get_staff().filter(
            status=1, profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True
        )

    def get_active_public_staff(self):
        return self.get_staff().filter(
            status=1, profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True, is_shared=True
        )

    def get_active_showroom_staff(self):
        return self.get_staff().filter(
            status=1, profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True, is_in_showroom=True
        )

    def list_contacts(self):
        return self.get_owners().union(self.get_active_public_staff()).distinct()

    def get_owners(self):
        return self.get_staff().filter(role=settings.OWNER)

    def get_active_owners(self):
        return self.get_active_staff().filter(role=settings.OWNER)

    def get_owners_and_delegates(self):
        return self.profiles.filter(role__in=[settings.OWNER, settings.DELEGATE])

    def get_delegates(self):
        return self.profiles.filter(role=settings.DELEGATE)

    def get_managers(self):
        return self.profiles.filter(role=settings.LEVEL_1)

    def get_workers(self):
        return self.profiles.filter(role=settings.LEVEL_2)

    def get_photos(self):
        return self.photos.filter(status=1)

    def get_videos(self):
        return self.videos.filter(status=1)

    def get_offers(self):
        return self.offers.filter(status=1)

    def get_active_offers(self):
        return self.offers.filter(status=1, deadline__gte=datetime.date.today())

    def get_certifications(self):
        return self.certifications.filter(status=1)

    def get_projects(self):
        return self.projects.all()

    def get_internal_projects(self):
        return self.projects.filter(typology=settings.PROJECT_PROJECT_INTERNAL)

    def get_shared_projects(self):
        return self.projects.filter(typology=settings.PROJECT_PROJECT_SHARED)

    def get_talks(self):
        return self.talks.all()

    def get_tracking(self):
        return self.tracking.get()

    def get_company_profiles(self):
        """
        We are nowhere using this function. May be, we can remove
        """
        return self.profiles.filter(
            status=1,
            user__isnull=False,
            company__isnull=False,
            role__isnull=False,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True
        )

    def list_partnerships(self):
        """
        Get all associated company partnerships
        """
        return self.request_partnerships.filter(
            approval_date__isnull=False, refuse_date__isnull=True,
            invitation_date__isnull=False
        )

    def list_favourites(self):
        return self.favourites.all()

    def list_public_company_photos(self):
        """
        Get all public company photos
        """
        return Photo.objects.filter(companies=self, is_public=True)

    def list_public_company_videos(self):
        """
        Get all public company photos
        """
        return Video.objects.filter(companies=self, is_public=True)

    @property
    def get_profiles_count(self):
        return self.profiles.count()

    get_profiles_count.fget.short_description = _('Profiles (All)')

    @property
    def get_owner_profiles_count(self):
        return self.profiles.owners().count()

    get_owner_profiles_count.fget.short_description = _('Owners')

    @property
    def get_delegate_profiles_count(self):
        return self.profiles.delegates().count()

    get_delegate_profiles_count.fget.short_description = _('Delegates')

    @property
    def get_level1_profiles_count(self):
        return self.profiles.level_1s().count()

    get_level1_profiles_count.fget.short_description = _('Level1')

    @property
    def get_level2_profiles_count(self):
        return self.profiles.level_2s().count()

    get_level2_profiles_count.fget.short_description = _('Level2')

    @property
    def get_internal_projects_count(self):
        return self.projects.internal_projects().count()

    get_internal_projects_count.fget.short_description = _('Internal Projects')

    @property
    def get_shared_projects_count(self):
        return self.projects.shared_projects().count()

    get_shared_projects_count.fget.short_description = _('Shared Projects')

    @property
    def get_offers_count(self):
        return self.offers.count()

    get_offers_count.fget.short_description = _('Offers')

    @property
    def get_certifications_count(self):
        return self.certifications.count()

    get_certifications_count.fget.short_description = _('Certifications')

    @property
    def get_boms_count(self):
        return self.boms.count()

    get_boms_count.fget.short_description = _('Boms')

    @property
    def get_quotations_count(self):
        return self.quotations.count()

    get_quotations_count.fget.short_description = _('Quotations')

    @property
    def get_projects_count(self):
        return self.projects.count()

    @property
    def get_messages_count(self):
        # Todo: Optimize the following code
        total_messages = 0
        for talk in self.talks.all():
            total_messages += talk.get_messages_count
        return total_messages

    @property
    def get_tags_count(self):
        # Todo: Optimize the following code
        total_tags = 0
        for project in self.projects.all():
            total_tags += project.get_tags_count

        for bom in self.boms.all():
            total_tags += bom.get_tags_count

        for quotation in self.quotations.all():
            total_tags += quotation.get_tags_count

        for offer in self.offers.all():
            total_tags += offer.get_tags_count

        return total_tags

    @property
    def get_followers_count(self):
        return self.followers.count()

    @property
    def get_staff_count(self):
        return self.profiles.count()

    @property
    def get_partnerships_count(self):
        return self.created_partnerships.filter(
            invitation_date__isnull=False,
            approval_date__isnull=False
        ).count()

    @property
    def get_is_sponsor(self):
        if self.sponsor.exclude(status=0):
            return True
        return False


@python_2_unicode_compatible
class Profile(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.ProfileManager()
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='profiles',
        verbose_name=_('user')
    )
    company = models.ForeignKey(
        'company',
        blank=True, null=True,
        related_name='profiles',
        verbose_name=_('company'),
        on_delete=models.DO_NOTHING
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name=_("last name"),
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name=_("first name"),
    )
    language = models.CharField(
        max_length=2,
        choices=settings.PROFILE_PROFILE_LANGUAGE_CHOICES,
    )
    position = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_("position"),
    )
    role = models.CharField(
        max_length=1,
        blank=True, null=True,
        choices=settings.PROFILE_PROFILE_ROLE_CHOICES,
        verbose_name=_('role'),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_('email'),
    )
    phone = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('phone'),
    )
    fax = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('fax')
    )
    mobile = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('mobile'),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_('note'),
    )
    photo = models.ImageField(
        blank=True,
        upload_to=get_upload_photo_path,
        verbose_name=_('image'),
    )
    talks = GenericRelation(
        'message.Talk',
        blank=True, null=True,
        related_query_name='profiles'
    )
    documents = GenericRelation(
        'document.Document',
        blank=True, null=True,
        related_query_name='profiles'
    )
    company_invitation_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('company invitation date'),
    )
    profile_invitation_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('profile invitation date'),
    )
    invitation_refuse_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('invitation refuse date'),
    )
    info = JSONField(
        default=profile_info_default,
        blank=True, null=True,
        verbose_name=_('info'),
        help_text=_('More information about profile'),
    )
    is_shared = models.BooleanField(
        default=False,
        verbose_name=_('is shared')
    )
    is_invited = models.BooleanField(
        default=False,
        verbose_name=_('is invited')
    )
    is_in_showroom = models.BooleanField(
        default=False,
        verbose_name=_('is in showroom')
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_('is superuser')
    )
    can_access_chat = models.BooleanField(
        default=True,
        verbose_name=_('can access chat')
    )
    can_access_files = models.BooleanField(
        default=True,
        verbose_name=_('can access files')
    )
    __original_instance = None

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ('ordering', 'last_name', 'first_name',)
        permissions = (
            ("list_profile", "can list profile"),
            ("detail_profile", "can detail profile"),
            ("disable_profile", "can disable profile"),
        )
        unique_together = (
            ('company', 'email'),
        )

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        if self.is_main:
            self.__class__ = MainProfile
        elif self.is_owner:
            self.__class__ = OwnerProfile
        elif self.is_delegate:
            self.__class__ = DelegateProfile
        elif self.is_level_1:
            self.__class__ = Level1Profile
        elif self.is_level_2:
            self.__class__ = Level2Profile

        self.__original_instance = copy.deepcopy(self.__dict__)

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)

    def get_role(self):
        if self.role == settings.OWNER:
            return "Owner"
        elif self.role == settings.DELEGATE:
            return "Delegate"
        elif self.role == settings.LEVEL_1:
            return "Manager"
        elif self.role == settings.LEVEL_2:
            return "Worker"
        return self.role

    def save(self, *args, **kwargs):
        if self.user:
            same_profiles = Profile.objects.filter(user=self.user, company=self.company)
            # if self.company:
            #     same_profiles = Profile.objects.filter(user=self.user, company=self.company)
            if self.id:
                same_profiles = same_profiles.exclude(id=self.id)
            if same_profiles:
                raise django_exception.ProfileAlreadyExists(_('Profile already exists'))
        if not self.id:
            new_obj = True
        else:
            new_obj = False
        super(Profile, self).save(user=self.user,*args, **kwargs)
        if new_obj:
            self.create_preference()

    # ------ PROFILE PREFERENCE ------

    def create_preference(self, info_preference_json=None):
        preference = Preference(
            creator=self.user or self.creator,
            last_modifier=self.user or self.last_modifier,
            profile=self
        )
        if info_preference_json:
            preference.info = info_preference_json
        preference.save(user=self.user)

    def get_preference(self):
        return self.preference

    def get_count_closed_preference(self):
        return sum(len(value['closed']) for key, value in self.preference.info['results'].items())

    def create_task_post(self, post_dict):
        from ..project.signals import post_notification
        task = Task.objects.get(id=post_dict['task'])
        post_dict.pop('task')
        post_worker = Post(
            task=task,
            **post_dict
        )
        post_worker.save()
        post_notification(post_worker._meta.model, post_worker, {'created': post_worker.created_date})
        return post_worker

    def create_activity_post(self, post_dict):
        from ..project.signals import post_notification

        activity = Activity.objects.get(id=post_dict['activity'])
        post_dict.pop('activity')
        post_worker = Post(
            sub_task=activity,
            **post_dict
        )
        post_worker.save()
        post_notification(post_worker._meta.model, post_worker, {'created': post_worker.created_date})
        return post_worker

    def create_post_comment(self, comment_dict):
        post = Post.objects.get(id=comment_dict['post'])
        comment_dict.pop('post')
        comment_worker = Comment(
            post=post,
            **comment_dict
        )
        comment_worker.save()
        return comment_worker

    def share_post(self, post_dict):
        post = Post.objects.get(id=post_dict['post'])
        try:
            task = post.sub_task.task
        except:
            task = post.task
        post_dict.pop('post')
        task_post_ass = TaskPostAssignment(
            post=post,
            task=task,
            **post_dict
        )
        task_post_ass.save()
        return task_post_ass

    def list_activity_posts(self, activity):
        """
        Get all posts of a specific activity
        """
        activity_obj = Activity.objects.get(id=activity)
        return activity_obj.post_set.all()

    def list_task_own_posts(self, task):
        """
        Get all posts of a specific activity
        """
        task_obj = Task.objects.get(id=task)
        return task_obj.post_set.all()

    def remove_post(self, post):
        post = Post.objects.get(id=post.id)
        post.delete()

    def remove_comment(self, comment):
        comment = Comment.objects.get(id=comment.id)
        comment.delete()

    def remove_attachment(self, attachment):
        attachment = MediaAssignment.objects.get(id=attachment.id)
        attachment.delete()

    def list_task_posts(self, task):
        """
        Get all posts of a specific activity
        """
        all_posts = []
        task_obj = Task.objects.get(id=task)
        taskpost_assigments = task_obj.taskpostassignment_set.all()
        for taskpost_ass in taskpost_assigments:
            all_posts.append(taskpost_ass.post)
        return all_posts

    def list_post_comments(self, post):
        """
        Get all comments of a specific post
        """
        post_obj = Post.objects.get(id=post)
        return post_obj.comment_set.filter(parent__isnull=True)

    def list_comment_replies(self, comment):
        """
        Get all comments of a specific post
        """
        comments = Comment.objects.filter(parent=comment)
        return comments

    def edit_preference(self, preference_dict):
        """
        Update profile preference
        """
        if self.get_preference().id == preference_dict['id']:
            preference = self.get_preference()
            preference.__dict__.update(**preference_dict)
            preference.save()
            return preference
        raise django_exception.OwnerProfilePermissionDenied(_('You can\'t edit others preference'))

    def edit_profile(self, profile_dict):
        """
        Updates main profile
        :return: profile obj
        """
        # PS: We could add object level permission in two different ways.
        # 1. If condition (Doesn't return any exception) i.e. if MyModel(id=1) == MyModel(id=1):
        # 2. The below codebase
        profile = Profile.objects.filter(id=self.id).get(id=profile_dict['id'])
        profile.__dict__.update(**profile_dict)
        profile.save()
        return profile

    # ------ PROFILE CLONE ------

    def clone(self):
        """
        Create a new instance profile
        :return: instace profile
        """
        profile = Profile()
        profile.creator = self.user
        profile.last_modifier = self.user
        profile.user = self.user
        profile.last_name = self.last_name
        profile.first_name = self.first_name
        profile.role = self.role
        profile.language = self.language
        profile.email = self.email
        profile.phone = self.phone
        profile.fax = self.fax
        profile.mobile = self.mobile
        profile.photo = self.photo
        profile.info = self.info
        profile.company_invitation_date = None
        profile.profile_invitation_date = None
        profile.invitation_refuse_date = None
        return profile

    # ------ PROFILE PROPERTIES ------

    # CODE FOR TOKEN REGISTRATION
    def id_to_base_36(self):
        return int_to_base36(self.id)

    uidb36 = property(id_to_base_36)

    def get_code_for_token(self):
        """
        Returns code used for token
        """
        return u"{}{}".format(
            zerofill(self.id, 10),
            self.date_last_modify
        )

    code_for_token = property(get_code_for_token)

    def get_token(self):
        """
        Return profile token string
        """
        token_generator = TokenGenerator()
        return token_generator.make_token(self.code_for_token)

    token = property(get_token)

    def check_token(self, token, duration=30):
        """
        Verify profile token
        """
        token_generator = TokenGenerator()
        if not token_generator.check_token(self.code_for_token, token):
            return False
        if duration and datetime.datetime.now() > self.date_last_modify + datetime.timedelta(days=duration):
            return False
        return True

    def get_accept_url(self):
        return reverse('api_frontend_profile:tracker_profile_accept_invite', args=[self.uidb36, self.token])

    def get_refuse_url(self):
        return reverse('api_frontend_profile:tracker_profile_refuse_invite', args=[self.uidb36, self.token])

    def send_invite_email(self, to_email=None, language_code=None):
        from_mail = settings.PROFILE_PROFILE_NO_REPLY_EMAIL
        if not to_email:
            to_email = self.email or self.user.email
        if not language_code:
            language_code = self.language if self.language else 'en'
        accept_url = self.get_accept_url()
        refuse_url = self.get_refuse_url()

        endpoint = os.path.join(settings.PROTOCOL + ':/', settings.BASE_URL, 'apps/companies')
        context = {
            'logo_url': os.path.join(
                settings.PROTOCOL + '://',
                settings.BASE_URL,
                'assets/images/logos/fuse.svg'
            ),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company,
            "endpoint": endpoint
        }

        if language_code == 'en':
            subject = "Edilcloud Company {} Profile Activation".format(self.company)
        else:
            subject = "Attivazione nuovo profilo Edilcloud per l'impresa {}".format(self.company)
        # Text message
        text_message = render_to_string('profile/profile/email/profile_{}.txt'.format(language_code), context)

        # Html message
        html_message = render_to_string('profile/profile/email/profile_{}.html'.format(language_code), context)
        try:
            msg = send_mail(
                subject=subject,
                message=text_message,
                html_message=html_message,
                recipient_list=[to_email],
                from_email=from_mail,
            )
            return True, msg
        except Exception as e:
            return False, e

    def get_invites(self):
        return self.invites.filter(
            invitation_date__isnull=False,
            profile_invitation_date__isnull=True
        )

    def get_favourites(self):
        return self.favourites.all()


    def get_invitation_status(self):
        if self.company_invitation_date and not self.profile_invitation_date and not self.invitation_refuse_date:
            return settings.PROFILE_PROFILE_INVITATION_STATUS_PENDING
        if self.profile_invitation_date and not self.invitation_refuse_date:
            return settings.PROFILE_PROFILE_INVITATION_STATUS_APPROVED
        if self.invitation_refuse_date:
            return settings.PROFILE_PROFILE_INVITATION_STATUS_DENIED

    def get_main_profile(self):
        if self.user:
            return self.user.get_main_profile()
        return None

    @property
    def is_main(self):
        if (
            self.user
            and not self.company
            and not self.role
            and self.profile_invitation_date
        ):
            return True
        return False

    @property
    def is_owner(self):
        if (
            self.company
            and self.role == settings.OWNER
            and self.profile_invitation_date
        ):
            return True
        return False

    @property
    def is_delegate(self):
        if (
            self.company
            and self.role == settings.DELEGATE
            and self.profile_invitation_date
        ):
            return True
        return False

    @property
    def is_level_1(self):
        if (
            self.company
            and self.role == settings.LEVEL_1
            and self.profile_invitation_date
        ):
            return True
        return False

    @property
    def is_level_2(self):
        if (
            self.company
            and self.role == settings.LEVEL_2
            and self.profile_invitation_date
        ):
            return True
        return False


@python_2_unicode_compatible
class Preference(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='preference',
        verbose_name=_('profile')
    )
    info = JSONField(
        default=profile_preference_info_default,
        verbose_name=_('info'),
        help_text=_('More information about profile preference'),
    )
    notification = JSONField(
        default=profile_preference_notification_default,
        verbose_name=_('notification'),
        help_text=_('More information about profile notification'),
    )

    class Meta:
        verbose_name = _('preference')
        verbose_name_plural = _('preferences')
        permissions = (
            ("list_preference", "can list preference"),
            ("detail_preference", "can detail preference"),
            ("disable_preference", "can disable preference"),
        )

    def __str__(self):
        return "{}".format(self.profile)


@python_2_unicode_compatible
class MainProfile(Profile):

    objects = managers.MainProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('main profile')
        verbose_name_plural = _('main profiles')
        permissions = (
            ("list_mainprofile", "can list main profile"),
            ("detail_mainprofile", "can detail main profile"),
            ("disable_mainprofile", "can disable main profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)

    # ------ PROFILE ------

    def list_mains(self):
        """
        Get all active main profiles in the WHISTLE platform
        """
        return self.__class__.objects.active()

    def create_company_profile(self, profile_dict):
        level2 = Profile(
            creator=self.user,
            last_modifier=self.user,
            role=settings.LEVEL_2,
            profile_invitation_date=datetime.datetime.now(),
            first_name=profile_dict['user'].get_main_profile().first_name,
            last_name=profile_dict['user'].get_main_profile().last_name,
            language=profile_dict['user'].get_main_profile().language,
            **profile_dict
        )
        level2.save()
        #Todo: Email send
        return level2

    def edit_profile(self, profile_dict):
        """
        Updates main profile
        :return: profile obj
        """
        # PS: We could add object level permission in two different ways.
        # 1. If condition (Doesn't return any exception) i.e. if MyModel(id=1) == MyModel(id=1):
        # 2. The below codebase
        profile = Profile.objects.filter(id=self.id).get(id=profile_dict['id'])
        profile.__dict__.update(**profile_dict)
        profile.save()
        return profile

    def enable_profile(self):
        """
        Enable only disabled profile
        :return: profile obj
        """
        if self.status == 0:
            self.status = 1
            self.save()
        return self

    def disable_profile(self):
        """
        Disable only enabled profile
        :return: profile obj
        """
        if self.status == 1:
            self.status = 0
            self.save()
        return self

    # ------ COMPANY ------

    def get_company_count(self):
        return Company.objects.filter(creator=self.user).count()

    def create_company(self, company_dict):
        # todo: active
        # todo: authenticated
        # if self.get_company_count() >= settings.MAX_COMPANIES_PER_USER:
        #     raise django_exception.OwnerProfilePermissionDenied(_('no permission to create other than 10 companies'))

        with transaction.atomic():
            company = Company(
                creator=self.user,
                last_modifier=self.user,
                **company_dict
            )
            company.save()

            # create new company profile
            profile = self.clone()
            profile.role = settings.OWNER
            profile.company = company
            profile.company_invitation_date = datetime.datetime.now()
            profile.profile_invitation_date = datetime.datetime.now()
            profile.invitation_refuse_date = None
            profile.save()

            # create stripe customer
            stripe.api_key = djstripe.settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.create(
                email=profile.email,
                name="{} {} - ({})".format(profile.first_name, profile.last_name, profile.company.name),
                phone=profile.phone
            )
            djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(customer)
            # TODO: ADD OTHER INFO LIKE VAT NUMBER ECC ECC
            # djstripe_customer.tax_id_data.type = 'eu_vat'
            # djstripe_customer.tax_id_data.value = profile.company.vat_number
            # djstripe.models.Customer.sync_from_stripe_data(djstripe_customer)
            company.customer = djstripe_customer.id
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {
                        "price": settings.TRIAL_PLAN
                    }
                ],
                trial_period_days=settings.TRIAL_MAX_DAYS
            )
            company.subscription = subscription.id
            company.save()
        return company, profile

    def list_companies(self):
        """
        Get all companies connected to the user
        """
        # Todo: Check other approach
        return Company.objects.get_companies(
            user=self.user
        )

    def get_active_companies(self):
        """
        Get all active companies connected to the user
        """
        return Company.objects.active().get_companies(
            user=self.user
        )

    def get_inactive_companies(self):
        """
        Get all inactive companies connected to the user
        """
        return Company.objects.inactive().get_companies(
            user=self.user
        )

    # ------ FAVOURITE ------

    def follow_company(self, company):
        favourite = Favourite(
            creator=self.user, last_modifier=self.user,
            profile=self, company=company
        )
        favourite.save()
        return favourite

    def unfollow_company(self, company):
        Favourite.objects.get(profile=self, company=company).delete()

    def list_favourites(self):
        """
        Company followings (MainProfile --> Company)
        :return: Companies
        """
        return self.followings.filter(favourites__approval_date__isnull=False, favourites__refuse_date__isnull=True)

    def list_waiting_favourites(self):
        """
        Company followings (MainProfile --> Company)
        :return: Companies
        """
        return self.favourites.filter(approval_date__isnull=True, refuse_date__isnull=True)

    # ------ SPONSOR ------

    def get_sponsor(self, sponsor_id):
        return Sponsor.objects.get(id=sponsor_id)

    def edit_sponsor(self, sponsor_dict):
        """
        Update company data
        """
        sponsor = Sponsor.objects.get(id=sponsor_dict['id'])
        for attr, value in sponsor_dict.items():
            setattr(sponsor, attr, value)
        sponsor.save()
        return sponsor


@python_2_unicode_compatible
class PhantomProfile(Profile):
    objects = managers.PhantomProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('phantom profile')
        verbose_name_plural = _('phantom profiles')
        permissions = (
            ("list_phantomprofile", "can list phantom profile"),
            ("detail_phantomprofile", "can detail phantom profile"),
            ("disable_phantomprofile", "can disable phantom profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)


@python_2_unicode_compatible
class GuestProfile(Profile):
    objects = managers.GuestProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('guest profile')
        verbose_name_plural = _('guest profiles')
        permissions = (
            ("list_guestprofile", "can list guest profile"),
            ("detail_guestprofile", "can detail guest profile"),
            ("disable_guestprofile", "can disable guest profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)


@python_2_unicode_compatible
class OwnerProfile(Profile):
    objects = managers.OwnerProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('owner profile')
        verbose_name_plural = _('owner profiles')
        permissions = (
            ("list_ownerprofile", "can list owner profile"),
            ("detail_ownerprofile", "can detail owner profile"),
            ("disable_ownerprofile", "can disable owner profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)

    # ------ NOTIFICATION ------

    def list_notification_receipient(self):
        return self.notification_recipient.all()

    def get_notification_receipient(self, notification_rcp_id):
        notification_receipient = self.list_notification_receipient().get(
            id=notification_rcp_id
        )
        return notification_receipient

    def edit_notification_receipient(self, notification_rcp):
        notification_receipient = self.list_notification_receipient().get(
            id=notification_rcp.id
        )
        notification_receipient.reading_date = datetime.datetime.now()
        notification_receipient.save()
        return notification_receipient

    def remove_notification_receipient(self, notification_rcp):
        notification_receipient = self.list_notification_receipient().get(
            id=notification_rcp.id
        )
        notification_receipient.status=False
        notification_receipient.save()

    def list_notification_receipient_event(self, type):
        return self.notification_recipient.filter(
            notification__content_type__model=type
        ).order_by('-date_create')

    def list_notification_receipient_count(self):
        return {
            'new': self.list_notification_receipient_new().filter(is_notify=True).count(),
            'read': self.list_notification_receipient_read().filter(is_notify=True).count(),
            'trash': self.list_notification_receipient_trash().filter(is_notify=True).count(),
            'events': self.list_notification_receipient().filter(is_notify=True).values(
                'notification__content_type__model'
            ).annotate(count=Count('notification__content_type__model')).order_by(),
            'events_new': self.list_notification_receipient().filter(
                reading_date__isnull=True, status=True, is_notify=True).values(
                'notification__content_type__model'
            ).annotate(count=Count('notification__content_type__model')).order_by(),
            'preferences': {
                'closed': self.get_count_closed_preference()
            }
        }

    def list_notification_receipient_new(self):
        return self.notification_recipient.filter(
            reading_date__isnull=True, status=True
        ).order_by('-date_create')

    def list_notification_receipient_read(self):
        return self.notification_recipient.filter(
            reading_date__isnull=False, status=True
        ).order_by('-date_create')

    def list_notification_receipient_trash(self):
        return self.notification_recipient.filter(
            status=False
        ).order_by('-date_create')

    # ------ TRACKING ------

    def remove_tracking(self, tracking):
        if self == tracking.profile:
            tracking.delete()
        else:
            raise django_exception.TrackingPermissionDenied(_('You can\'t delete other\'s tracking'))

    # ------ PROFILE ------

    def create_owner(self, profile, profile_dict):
        if profile.is_main:
            owner = profile.clone()
            owner.company = self.company
            owner.__dict__.update(**profile_dict)
            owner.company_invitation_date = datetime.datetime.now()
            owner.save()
            # Send Invitation Email
            owner.send_invite_email()
            return owner
        raise django_exception.OwnerProfilePermissionDenied(_('profile instance must be a MainProfile'))

    def create_delegate(self, profile, profile_dict):
        if profile.is_main:
            delegate = profile.clone()
            # delegate.role = settings.DELEGATE
            delegate.company = self.company
            delegate.__dict__.update(**profile_dict)
            delegate.company_invitation_date = datetime.datetime.now()
            delegate.save()
            # Send Invitation Email
            delegate.send_invite_email()
            return delegate
        raise django_exception.OwnerProfilePermissionDenied(_('profile instance must be a MainProfile'))

    def create_level1(self, profile, profile_dict):
        if profile.is_main:
            level1 = profile.clone()
            # level1.role = settings.LEVEL_1
            level1.company = self.company
            level1.__dict__.update(**profile_dict)
            level1.company_invitation_date = datetime.datetime.now()
            level1.save()
            # Send Invitation Email
            level1.send_invite_email()
            return level1
        raise django_exception.OwnerProfilePermissionDenied(_('profile instance must be a MainProfile'))

    def create_level2(self, profile, profile_dict):
        if profile.is_main:
            level2 = profile.clone()
            # level2.role = settings.LEVEL_2
            level2.company = self.company
            level2.__dict__.update(**profile_dict)
            level2.company_invitation_date = datetime.datetime.now()
            level2.save()
            # Send Invitation Email
            level2.send_invite_email()
            return level2
        raise django_exception.OwnerProfilePermissionDenied(_('profile instance must be a MainProfile'))

    def create_phantom(self, profile_dict):
        phantom = Profile(
            creator=self.user,
            last_modifier=self.user,
            company=self.company,
            company_invitation_date=datetime.datetime.now(),
            profile_invitation_date=datetime.datetime.now(),
            is_invited=True,
            **profile_dict
        )
        phantom.save()
        return phantom

    def list_owners(self):
        """
        Get all OwnerProfiles linked to the company
        """
        return self.company.profiles.owners()

    def list_delegates(self):
        """
        Get all DelegateProfiles linked to the company
        """
        return self.company.profiles.delegates()

    def list_level1s(self):
        """
        Get all Level1Profiles linked to the company
        """
        return self.company.profiles.level_1s()

    def list_level2s(self):
        """
        Get all Level2Profiles linked to the company
        """
        return self.company.profiles.level_2s()

    def list_phantoms(self):
        """
        Get all PhantomProfiles linked to the company
        """
        return self.company.profiles.phantoms()

    def list_guests(self):
        """
        Get all GuestProfiles invited by the company but not yet accepted or rejected
        """
        return self.company.profiles.guests()

    def list_profiles(self):
        """
        Get all company profiles linked to the company
        """
        return self.company.profiles.all()

    def list_request_profiles(self):
        """
        Get all company profiles linked to the company
        """
        return self.company.profiles.company_invitation_request()

    def list_waiting_profiles(self):
        """
        Get all company profiles linked to the company
        """
        complete_staff = []
        waiting_staff = self.company.profiles.company_invitation_waiting().filter(status=1)
        for staff in waiting_staff:
            complete_staff.append(staff)
        requested_staff = self.company.profiles.company_invitation_request().filter(status=1)
        for staff in requested_staff:
            complete_staff.append(staff)
        return complete_staff

    def list_approve_profiles(self):
        """
        Get all company profiles linked to the company
        """
        return self.company.profiles.company_invitation_approve().filter(status=1)

    def list_approve_profiles_and_external(self, is_creator, profile):
        """
        Get all company profiles linked to the company and external owners
        """
        print(is_creator)
        if is_creator or profile.role == 'o' or profile.role == 'd':
            return Profile.objects.filter(
                Q(company__profiles__in=self.company.profiles.company_invitation_approve()) | \
                Q(role='o') | \
                Q(role='d')) \
                .filter(status=1) \
                .distinct()
        else:
            return self.company.profiles.company_invitation_approve()

    def list_refuse_profiles(self):
        """
        Get all company profiles linked to the company
        """
        return self.company.profiles.company_invitation_refuse()

    def list_active_profiles(self):
        """
        Get all company active profiles linked to the company
        """
        return self.company.profiles.all()

    def list_approve_profiles_inactive(self):
        """
        Get all company profiles linked to the company
        """
        return self.company.profiles.company_invitation_approve_inactive()

    def get_profile(self, profile_id):
        profile = self.list_profiles().get(id=profile_id)
        return profile

    def edit_profile(self, profile_dict):
        profile = self.company.profiles.get(id=profile_dict['id'])
        profile.__dict__.update(**profile_dict)
        profile.save()
        return profile

    def enable_profile(self):
        """
        Enable company profile, if it is disabled
        """
        profile = self.list_profiles().get(id=self.id)
        if profile.status == 0:
            profile.status = 1
            profile.save()
        return profile

    def disable_profile(self):
        """
        Disable company profile, if it is enabled
        """
        profile = self.list_profiles().get(id=self.id)
        if profile.status == 1:
            profile.status = 0
            profile.save()
        return profile

    def remove_profile(self, profile):
        """
        Delete a company profile
        """
        profile = self.list_profiles().get(id=profile.id)
        profile.delete()

    # ------ COMPANY ------

    def list_companies(self):
        """
        Get all companies connected to the user
        """
        # Todo: Check other approach
        return Company.objects.get_companies(
            user=self.user
        )

    def get_company(self, company_id):
        """
        Get company
        """
        company = self.list_companies().get(id=company_id)
        return company

    def edit_company(self, company_dict):
        """
        Update company data
        """
        company = self.list_companies().get(id=company_dict['id'])
        company.__dict__.update(**company_dict)
        company.save()
        return company

    def enable_company(self):
        """
        Enable company, if it is disabled
        """
        company = self.list_companies().get(id=self.company.id)
        if company.status == 0:
            company.status = 1
            company.save()
        return company

    def disable_company(self):
        """
        Disable company, if it is enabled
        """
        company = self.list_companies().get(id=self.company.id)
        if company.status == 1:
            company.status = 0
            company.save()
        return company

    def remove_company(self):
        """
        Remove company
        """
        company = self.list_companies().get(id=self.company.id)
        company.delete()

    # ------ PARTNERSHIP ------

    def create_partnership(self, company):
        if self.company.id != company.id:
            partnership = Partnership(
                creator=self.user,
                last_modifier=self.user,
                inviting_company=company,
                guest_company=self.company,
            )
            partnership.save()
            return partnership
        raise django_exception.OwnerProfilePermissionDenied(_('You cannot partnership your company'))

    def list_created_partnerships(self):
        """
        Get all associated company partnerships
        """
        return self.company.created_partnerships.all()

    def list_guest_partnerships(self):
        """
        Get all associated company partnerships
        """
        return self.company.request_partnerships.all()

    def list_request_partnerships(self):
        """
        Get all associated company partnerships (request)
        """
        return self.list_created_partnerships().filter(
            invitation_date__isnull=False,
            approval_date__isnull=True,
            refuse_date__isnull=True
        )

    def list_approve_partnerships(self):
        """
        Get all associated company partnerships (approve)
        """
        list_part = self.company.request_partnerships.all()
        return list_part.filter(
            invitation_date__isnull=False,
            approval_date__isnull=False,
            refuse_date__isnull=True
        ).exclude(inviting_company=self.company)

    def list_refuse_partnerships(self):
        """
        Get all associated company partnerships (refuse)
        """
        return self.list_created_partnerships().filter(
            invitation_date__isnull=False,
            approval_date__isnull=True,
            refuse_date__isnull=False
        )

    def list_waiting_partnerships(self):
        """
        Get all associated company partnerships (waiting)
        """
        return self.list_guest_partnerships().filter(
            invitation_date__isnull=False,
            approval_date__isnull=True,
            refuse_date__isnull=True
        )

    def accept_partnership(self, company):
        partnership = self.list_created_partnerships().get(guest_company=company)
        partnership.approval_date = datetime.datetime.now()
        partnership.save()
        Partnership.objects.get_or_create(
            inviting_company=company,
            guest_company=self.company,
            defaults={
                'creator': self.user,
                'last_modifier': self.user,
                'invitation_date': datetime.datetime.now(),
                'approval_date': datetime.datetime.now()
            }
        )
        return partnership

    def refuse_partnership(self, company):
        partnership = self.list_created_partnerships().get(guest_company=company)
        partnership.refuse_date = datetime.datetime.now()
        partnership.save()
        return partnership

    def remove_partnership(self, partnership):
        """
        Remove an existing partnership
        """
        partnership.delete()

    # ------ PROJECT ------

    def create_project(self, project_dict):
        with transaction.atomic():
            project = Project(
                creator=self.user,
                last_modifier=self.user,
                company=self.company,
                **project_dict
            )
            project.save()

            team = Team(
                creator=self.user,
                last_modifier=self.user,
                profile=self,
                project=project,
                project_invitation_date=datetime.datetime.now(),
                role=settings.OWNER
            )
            team.save()
            content_type = ContentType.objects.get(model='project')
            self.get_or_create_talk({
                'content_type': content_type,
                'content_type_id': content_type.id,
                'object_id': project.id
            })
        return project

    def clone_project(self, project):
        project = self.list_projects().get(id=project.id)
        if project.is_shared_project:
            project.clone()
        else:
            raise django_exception.ProjectClonePermissionDenied(_('Internal Project can\'t be cloned'))

    def list_projects_basic(self):
        return self.company.projects.filter(
            Q(profiles__in=[self.id]) | Q(company=self.company)).distinct()

    def list_projects(self):
        """
        Get all company projects
        """
        if self.role == 'o' or self.role == 'd':
            return Project.objects.filter(Q(company=self.company) | Q(members__profile__in=[self], members__status=1)).distinct()
        else:
            return Project.objects.filter(Q(members__profile__in=[self], members__status=1)).distinct()

    def list_post_alert_all_activities(self):
        activities_list = []
        projects = self.list_projects()
        for project in projects:
            tasks = self.list_tasks(project)
            for task in tasks:
                activities = self.list_task_activities(task)
                for act in activities:
                    activities_list.append(act)
        return Post.objects.filter(alert=True, sub_task__in=activities_list)

    def list_post_alert_all_tasks(self):
        tasks_list = []
        projects = self.list_projects()
        for project in projects:
            tasks = self.list_tasks(project)
            for task in tasks:
                tasks_list.append(task)
        return Post.objects.filter(alert=True, task__in=tasks_list)

    def get_generic_project(self, project_id):
        return Project.objects.get(pk=project_id)

    def get_parent_project(self, project_id):
        """
        Get a company parent project
        """
        project = self.get_generic_project(project_id)
        if project and project.tasks.filter(assigned_company=self.company):
            return project
        else:
            raise django_exception.ProjectClonePermissionDenied(_('You dont have permission'))

    def get_project(self, project_id):
        """
        Get a company project
        """
        project = self.list_projects().get(id=project_id)
        return project

    def edit_project(self, project_dict):
        """
        Update a company project
        """
        project = self.get_project(project_dict['id'])
        project.__dict__.update(**project_dict)
        if 'referent' in project_dict:
            project.referent = project_dict['referent']
        project.save()
        return project

    def enable_project(self, project):
        """
        Enable a company project, if it is disabled
        """
        project = self.get_project(project.id)
        if project.status == 0:
            project.status = 1
            project.save()
        return project

    def disable_project(self, project):
        """
        Disable a company project, if it is enabled
        """
        project = self.get_project(project.id)
        if project.status == 1:
            project.status = 0
            project.save()
        return project

    def remove_project(self, project):
        """
        Delete a company project
        """
        project = self.get_project(project.id)
        if project.creator == self.user:
            project.delete()
        raise django_api_exception.ProfileAPIDoesNotMatch(
            status.HTTP_403_FORBIDDEN, self.request, _('You are not the project owner!')
        )
    # ------ PROJECT TASK ------

    def create_task(self, task_dict):
        task = Task(
            creator=self.user,
            last_modifier=self.user,
            **task_dict
        )
        task.save()
        if task.assigned_company and self.company.id != task.assigned_company.id:
            tasks = task.project.tasks.filter(
                assigned_company=task.assigned_company,
                shared_task__isnull=True
            )
            if tasks and task.get_share_status():
                self.clone_task(task)
        return task

    def share_task(self, task):
        task = self.get_task(task.id)

        tasks = task.project.tasks.filter(
            shared_task__isnull=True,
            assigned_company=task.assigned_company
        )

        with transaction.atomic():
            for task in tasks:
                task.project.clone(task.assigned_company)
                self.clone_task(task)

    def clone_task(self, task):
        # Todo: Add permission wrt company profile
        task.clone()

    def list_internal_tasks(self, project):
        project = self.list_projects().get(id=project.id)
        return project.tasks.filter(project=project, assigned_company=project.company)

    def list_internal_tasks_interval(self, project, month, year):
        tasks = self.list_tasks(project)

        date_from, date_to = get_first_last_dates_of_month_and_year(month, year)

        return tasks.filter(
            Q(date_start__gte=date_from, date_start__lte=date_to)
            | Q(date_start__lt=date_from, date_end__gte=date_from)
        )

    def list_parent_tasks_interval(self, project_id, month, year):
        tasks = self.list_parent_tasks(project_id)

        d_fmt = "{0:>02}.{1:>02}.{2}"
        date_from = datetime.datetime.strptime(
            d_fmt.format(1, month, year), '%d.%m.%Y').date()
        last_day_of_month = calendar.monthrange(int(year), int(month))[1]
        date_to = datetime.datetime.strptime(
            d_fmt.format(last_day_of_month, month, year), '%d.%m.%Y').date()

        return tasks.filter(
            Q(date_start__gte=date_from, date_start__lte=date_to)
            | Q(date_start__lt=date_from, date_end__gte=date_from)
        )

    def list_tasks(self, project):
        """
        Get all company tasks of a company project
        """
        project = self.list_projects().get(id=project.id)
        #return project.tasks.filter(Q(assigned_company=self.company) | Q(project__company_id=self.company.id))
        return project.tasks.all()

    def list_projects_tasks(self, projects):
        """
        Get all company tasks of a company project
        """
        projects_list = []
        for project in projects:
            projects_list.append(project.id)
        return Task.objects.filter(project__id__in=projects_list)

    def list_tasks_and_parent_tasks(self, project):
        my_tasks = self.list_tasks(project)
        if project.shared_project:
            parent_tasks = self.list_parent_tasks(project.shared_project.id)
            return my_tasks.union(parent_tasks.filter(assigned_company=project.company))
        return my_tasks

    def list_parent_tasks(self, project_id):
        """
        Get all company tasks of a company project
        """
        project = self.get_parent_project(project_id)
        return project.tasks.all()

    def all_company_staff_interval(self, month=None, year=None):
        """
        Get all company staffs
        """
        queryset = self.company.profiles.all()

        date_from, date_to = get_first_last_dates_of_month_and_year(month, year)
        if date_from:
            query = (
                Q(activities__datetime_start__gte=date_from, activities__datetime_start__lte=date_to)
                | Q(activities__datetime_start__lt=date_from, activities__datetime_end__gte=date_from)
            )
            queryset = queryset.filter(query).distinct()
        return queryset

    def all_company_projects_interval(self, month=None, year=None):
        """
        Get all company projects
        """
        queryset = self.company.projects.all()

        date_from, date_to = get_first_last_dates_of_month_and_year(month, year)
        if date_from:
            query = (
                Q(date_start__gte=date_from, date_start__lte=date_to)
                | Q(date_start__lt=date_from, date_end__gte=date_from)
            )
            queryset = queryset.filter(query).distinct()

        return queryset

    def all_projects_interval(self, month=None, year=None):
        """
        Get all company projects
        """
        queryset = self.company.projects.filter(profiles=self.id)

        date_from, date_to = get_first_last_dates_of_month_and_year(month, year)
        if date_from:
            query = (
                Q(date_start__gte=date_from, date_start__lte=date_to)
                | Q(date_start__lt=date_from, date_end__gte=date_from)
            )
            queryset = queryset.filter(query).distinct()

        return queryset

    def all_activities_interval(self, month=None, year=None):
        """
        Get all company profile tasks
        """
        # queryset = self.company.assigned_tasks.filter(workers=self)
        queryset = self.activities
        date_from, date_to = get_first_last_dates_of_month_and_year(month, year)
        if date_from:
            query = (
                Q(datetime_start__gte=date_from, datetime_start__lte=date_to)
                | Q(datetime_start__lt=date_from, datetime_end__gte=date_from)
            )
            queryset = queryset.filter(query).distinct()

        return queryset

    def all_internal_tasks(self):
        """
        Get all internal company tasks
        """
        projects_id = self.list_internal_projects().values_list('id', flat=True)
        return Task.objects.filter(project__in=projects_id, assigned_company=self.company)

    def all_shared_tasks(self):
        """
        Get all shared company tasks
        """
        projects_id = self.list_shared_projects().values_list('id', flat=True)
        return Task.objects.filter(project__in=projects_id)

    def get_generic_task(self, task_id):
        return Task.objects.get(pk=task_id)

    def get_task(self, task_id):
        """
        Get a company project
        """
        # Todo: Ameliorate
        project = self.list_projects().get(tasks__id=task_id)
        task = project.tasks.all().get(id=task_id)
        return task

    def get_post(self, post_id):
        """
        Get a company project
        """
        # Todo: Ameliorate
        post = Post.objects.get(id=post_id)
        return post

    def edit_post(self, post_dict):
        """
        Update a company project
        """
        from ..project.signals import post_notification, alert_notification
        post = self.get_post(post_dict['id'])
        if post.alert != post_dict['alert']:
            only_alert = True
        else:
            only_alert = False
        post.__dict__.update(**post_dict)
        if post_dict['alert'] is True:
            try:
                post.sub_task.alert = True
                post.sub_task.save()
            except:
                post.task.alert = True
                post.task.save()
        else:
            try:
                posts = post.sub_task.post_set.exclude(id=post.id)
                find_alerts = posts.filter(alert=True).count()
                if find_alerts == 0:
                    post.sub_task.alert = False
                    post.sub_task.save()
            except:
                posts = post.task.post_set.exclude(id=post.id)
                find_alerts = posts.filter(alert=True).count()
                if find_alerts == 0:
                    post.task.alert = False
                    post.task.save()
        post.save()
        if only_alert:
            alert_notification(post._meta.model, post)
        else:
            post_notification(post._meta.model, post, {'created': None})
        return post

    def get_attachment(self, attachment_id):
        attachment = MediaAssignment.objects.get(id=attachment_id)
        return attachment

    def get_comment(self, comment_id):
        comment = Comment.objects.get(id=comment_id)
        return comment

    def edit_comment(self, comment_dict):
        """
        Update a company project
        """
        comment = self.get_comment(comment_dict['id'])
        comment.__dict__.update(**comment_dict)
        comment.save()
        return comment

    def edit_task(self, task_dict):
        """
        Update a company task
        PS: You can't edit the task once it is cloned.
        """
        # Todo: check the concept
        # PS: For better understanding, we aren't merging the following 2 queries into one.
        project = self.list_projects().get(id=task_dict['project'].id)
        task = self.list_tasks(project).get(id=task_dict['id'])
        # if not task.project.internal_projects.all():
        # if not task.get_share_status():
        #     if task_dict['date_completed'] and (not 'progress'in task_dict):
        #         task_dict['progress'] = 100
        #     task.__dict__.update(**task_dict)
        #     task.save()
        if task_dict['date_completed'] and (not 'progress'in task_dict):
            task_dict['progress'] = 100
        task.__dict__.update(**task_dict)
        task.save()
        if 'progress'in task_dict and task.shared_task:
            self.update_shared_task_progress(task.shared_task)
        return task

    def update_shared_task_progress(self, task):
        task_list = Task.objects.filter(shared_task=task, status=1)
        tot_days = 0;
        completed_day = 0;
        task_days = (task.date_end - task.date_start).days
        for child in task_list:
            prj_days = (child.date_end - child.date_start).days
            completed_pry_days = (child.progress*prj_days)/100
            tot_days += prj_days
            completed_day += completed_pry_days

        parent_completed_days = (completed_day*task_days)/tot_days
        parent_progress = (parent_completed_days*100)/task_days
        task.progress = int(parent_progress)
        task.save()


    def assign_task(self, task_dict):
        """
        Update a company task
        PS: You can't edit the task once it is cloned.
        """
        # Todo: check the concept
        # PS: For better understanding, we aren't merging the following 2 queries into one.
        project = self.list_projects().get(id=task_dict['project'].id)
        task = self.list_tasks(project).filter(id=task_dict['id'])
        task.update(**task_dict)
        task_instance = task[0]
        if task_instance.assigned_company and self.company.id != task_instance.assigned_company.id:
            tasks = task_instance.project.tasks.filter(
                assigned_company=task_instance.assigned_company,
                shared_task__isnull=True
            )
            if tasks and task_instance.get_share_status():
                self.clone_task(task_instance)
        return task_instance

    def enable_task(self, task):
        """
        Enable a company project task, if it is disabled
        """
        task = self.list_tasks(task.project).get(id=task.id)
        if task.status == 0:
            task.status = 1
            task.save()
        return task

    def disable_task(self, task):
        """
        Disable a company project task, if it is enabled
        """
        task = self.list_tasks(task.project).get(id=task.id)
        if task.status == 1:
            task.status = 0
            task.save()
        return task

    def close_task(self, task):
        """
        Close a company task is completed by the company
        """
        task = self.list_tasks(task.project).get(id=task.id)
        task.date_completed = datetime.datetime.now()
        task.save()
        return task

    def open_task(self, task):
        """
        Open a company task has not yet been completed)
        """
        task = self.list_tasks(task.project).get(id=task.id)
        task.date_completed = None
        task.save()
        return task

    def remove_task(self, task):
        """
        Delete a company project task
        """
        task = self.list_tasks(task.project).get(id=task.id)
        task.delete()

    # ------ PROJECT TASK ACTIVITY ------

    def create_task_activity(self, activity_dict):
        task = self.get_task(activity_dict['task'].id)
        # Todo: Put the following logic in a new function
        #act_list = []
        workers = activity_dict.pop('workers')
        task_worker = Activity(
            creator=self.user,
            last_modifier=self.user,
            **activity_dict
        )
        for worker in workers:
            task.project.members.all().get(profile__id=worker.id)
            task_worker.save()
            task_worker.workers.add(worker)
        task_worker.save()

        # for owner in task.project.members.filter(role__in=['o', 'd']):
        #     task_worker.workers.add(owner.profile)
        #     task_worker.save()
        #act_list.append(task_worker)
        return task_worker

    def list_task_internal_activities(self, project_id):
        project = self.get_project(project_id)
        activity_queryset = []
        for task in project.tasks.filter(assigned_company=project.company):
            activity_queryset.append(task.activities.all())
        return list(chain(*activity_queryset))

    def list_task_activities(self, task):
        """
        Get all company activities of a company project task
        """
        task = self.get_task(task.id)
        return task.activities.all().order_by('-date_create')

    def list_project_parent_activities(self, project_id):
        project = self.get_parent_project(project_id)
        activity_queryset = []
        for task in project.tasks.all():
            activity_queryset.append(task.activities.all())
        return list(chain(*activity_queryset))

    def list_project_task_activities(self, project_id):
        project = self.get_project(project_id)
        activity_queryset = []
        for task in project.tasks.all():
            activity_queryset.append(task.activities.all())
        return list(chain(*activity_queryset))

    def get_task_activity(self, activity_id):
        """
        Get a company project task activity
        """
        project = self.list_projects().get(tasks__activities__id=activity_id)
        task = project.tasks.get(activities__id=activity_id)
        activity = self.list_task_activities(task).get(id=activity_id)
        return activity

    def edit_task_activity(self, activity_dict):
        """
        Update a activity of a company project task
        """
        # Todo: Don't update Task, profile
        activity = self.get_task_activity(activity_dict['id'])
        workers = activity_dict.pop('workers')
        activity.__dict__.update(**activity_dict)
        activity.workers.clear()
        for worker in workers:
            activity.task.project.members.all().get(profile__id=worker.id)
            activity.save()
            activity.workers.add(worker)
        activity.save()
        return activity

    def remove_task_activity(self, activity):
        """
        Delete a company project task activity
        """
        activity = self.list_task_activities(activity.task).get(id=activity.id)
        activity.delete()

    # ------ PROJECT MEMBER (STAFF)------

    def create_member(self, member_dict):
        # internal_project = False
        # if (
        #     'project' in member_dict
        #     and member_dict['project']
        # ):
        #     internal_project = member_dict['project'].is_internal_project

        # Raise if shared project wants to add a team member
        # if not internal_project:
        #     raise django_exception.ProjectMemberAddPermissionDenied(_('Shared Project can\'t add a team member'))

        member = Team(
            creator=self.user,
            last_modifier=self.user,
            **member_dict
        )
        member.save()
        return member

    def list_members(self, project_id):
        """
        Get all members of a company project
        """
        project = self.list_projects().get(id=project_id)
        return project.members.all()

    def list_approve_members(self, project_id):
        """
        Get all members of a company project approved
        """
        project = self.list_projects().get(id=project_id)
        return project.members.filter(
            status=1,
            project_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def list_waiting_members(self, project_id):
        """
        Get all members of a company project waiting
        """
        project = self.list_projects().get(id=project_id)
        return project.members.filter(
            status=0,
            project_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def list_refuse_members(self, project_id):
        """
        Get all members of a company project refused
        """
        project = self.list_projects().get(id=project_id)
        return project.members.filter(
            status=0,
            project_invitation_date__isnull=False,
            invitation_refuse_date__isnull=False,
        )

    def list_parent_members(self, project_id):
        """
        Get all members of a company project
        """
        project = self.get_parent_project(project_id)
        return project.members.all()

    def get_member(self, member_id):
        """
        Get a company project member
        """
        # Todo: Ameliorate
        member = Team.objects.get(id=member_id)
        return member

    def edit_member(self, member_dict):
        """
        Update a member of a company project
        """
        # PS: For better understanding, we aren't merging the following 2 queries into one.
        project = self.list_projects().get(id=member_dict['project'].id)
        member = self.list_members(project.id).get(id=member_dict['id'])
        member.__dict__.update(**member_dict)
        member.save()
        return member

    def enable_member(self, member):
        """
        Enable a company project member, if it is disabled
        """
        if member.status == 0:
            member.status = 1
            member.save()
        return member

    def disable_member(self, member):
        """
        Disable a company project member, if it is enabled
        """
        #member = self.list_waiting_members(member.project.id).get(id=member.id)
        if member.status == 1:
            member.status = 0
            member.save()
        else:
            member.status = 0
            member.invitation_refuse_date = datetime.datetime.now()
            member.save()
        return member

    def remove_member(self, member):
        """
        Delete a member of a company project
        """
        # PS: For better understanding, we aren't merging the following 2 queries into one.
        member = self.list_members(member.project.id).get(id=member.id)
        member.delete()

    # ------ BOM ------

    def create_bom(self, bom_dict):
        with transaction.atomic():
            bom_row_dict = bom_dict.pop('bom_rows', [])
            bom_selected_companies = bom_dict.pop('selected_companies', [])

            bom = Bom(
                creator=self.user,
                last_modifier=self.user,
                owner=self.company,
                contact=self,
                **bom_dict
            )
            bom.save()

            for selected_company in bom_selected_companies:
                bom.selected_companies.add(selected_company)

            for bom_rw in bom_row_dict:
                bom_row = BomRow(
                    creator=self.user,
                    last_modifier=self.user,
                    bom=bom,
                    **bom_rw
                )
                bom_row.save()

        return bom

    def list_boms(self):
        """
        Get all company boms
        """
        return self.company.boms.all()

    def list_sent_boms(self):
        """
        Get all company sender boms
        """
        return self.company.boms.filter(is_draft=False)

    def list_draft_boms(self):
        """
        Get all company sender boms
        """
        return self.company.boms.filter(is_draft=True)

    def list_received_boms(self):
        """
        Get all company receiver boms
        """
        if self.company.is_supplier:
            return Bom.objects.filter(
                Q(is_draft=False) & (
                    Q(selected_companies=self.company) | (
                        Q(selected_companies=None) & Q(bom_rows__category__code__in=self.company.category.keys())
                    )
                )
            ).distinct()
        return self.company.selected_boms.all()

    def list_project_boms(self, project_id):
        project = self.get_project(project_id)
        return project.company.boms.all()

    def list_project_sender_boms(self, project_id):
        project = self.get_project(project_id)
        return self.company.boms.filter(project=project, is_draft=False)

    def list_project_draft_boms(self, project_id):
        project = self.get_project(project_id)
        return self.company.boms.filter(project=project, is_draft=True)

    def list_project_receiver_boms(self, project_id):
        project = self.get_project(project_id)
        return self.company.selected_boms.filter(project=project)

    def get_bom(self, bom_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        bom = self.list_boms().get(id=bom_id)
        bom_dict = {
            'bom': bom,
            'bom_rows:': bom.bom_rows.all()
        }
        return bom_dict

    def get_draft_bom(self, bom_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        bom = self.list_draft_boms().get(id=bom_id)
        bom_dict = {
            'bom': bom,
            'bom_rows:': bom.bom_rows.all()
        }
        return bom_dict

    def get_received_bom(self, bom_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        bom = self.list_received_boms().get(id=bom_id)
        bom_dict = {
            'bom': bom,
            'bom_rows:': bom.bom_rows.all()
        }
        return bom_dict

    def get_sent_bom(self, bom_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        bom = self.list_sent_boms().get(id=bom_id)
        bom_dict = {
            'bom': bom,
            'bom_rows:': bom.bom_rows.all()
        }
        return bom_dict

    def edit_bom(self, bom_dict):
        """
        Update a company bom
        """
        bom_selected_companies = bom_dict.pop('selected_companies', [])
        bom = self.list_boms().get(id=bom_dict['id'])
        bom.__dict__.update(**bom_dict)

        if bom_selected_companies:
            bom.selected_companies.clear()

        for selected_company in bom_selected_companies:
            bom.selected_companies.add(selected_company)
        bom.save()
        return bom

    def enable_bom(self, bom):
        """
        Enable a company bom, if it is disabled
        """
        bom = self.list_boms().get(id=bom.id)
        if bom.status == 0:
            bom.status = 1
            bom.save()
        return bom

    def disable_bom(self, bom):
        """
        Disable a company bom, if it is enabled
        """
        bom = self.list_boms().get(id=bom.id)
        if bom.status == 1:
            bom.status = 0
            bom.save()
        return bom

    def remove_bom(self, bom):
        """
        Delete a company bom
        """
        bom = self.list_boms().get(id=bom.id)
        bom.delete()

    def archive_bom(self, bomarchive_dict):
        bom_archive = BomArchive(
            creator=self.user,
            last_modifier=self.user,
            ** bomarchive_dict
        )
        bom_archive.save()
        return bom_archive

    # ------ BOM ROW ------

    def create_bomrow(self, bomrow_dict):
        self.list_boms().get(id=bomrow_dict['bom'].id)
        bomrow = BomRow(
            creator=self.user,
            last_modifier=self.user,
            **bomrow_dict
        )
        bomrow.save()
        return bomrow

    def list_bomrows(self, bom_id):
        """
        Get all company bomrows
        """
        bom = self.list_boms().get(id=bom_id)
        return bom.bom_rows.all()

    def list_draft_bomrows(self, bom_id):
        """
        Get all company bomrows
        """
        bom = self.list_draft_boms().get(id=bom_id)
        return bom.bom_rows.all()

    def list_sent_bomrows(self, bom_id):
        """
        Get all company bomrows
        """
        bom = self.list_sent_boms().get(id=bom_id)
        return bom.bom_rows.all()

    def list_received_bomrows(self, bom_id):
        """
        Get all company bomrows
        """
        bom = self.list_received_boms().get(id=bom_id)
        return bom.bom_rows.all()

    def get_bomrow(self, bomrow_id):
        """
        Get bomrow
        """
        bom = self.list_boms().get(bom_rows__id=bomrow_id)
        bomrow = bom.bom_rows.all().get(id=bomrow_id)
        return bomrow

    def get_draft_bomrow(self, bomrow_id):
        """
        Get bomrow
        """
        bom = self.list_draft_boms().get(bom_rows__id=bomrow_id)
        bomrow = bom.bom_rows.all().get(id=bomrow_id)
        return bomrow

    def get_received_bomrow(self, bomrow_id):
        """
        Get bomrow
        """
        bom = self.list_received_boms().get(bom_rows__id=bomrow_id)
        bomrow = bom.bom_rows.all().get(id=bomrow_id)
        return bomrow

    def get_sent_bomrow(self, bomrow_id):
        """
        Get bomrow
        """
        bom = self.list_sent_boms().get(bom_rows__id=bomrow_id)
        bomrow = bom.bom_rows.all().get(id=bomrow_id)
        return bomrow

    def edit_bomrow(self, bomrow_dict):
        """
        Update a company bomrow
        """
        bomrow = self.list_bomrows(bomrow_dict['bom'].id).get(id=bomrow_dict['id'])
        bomrow.__dict__.update(**bomrow_dict)
        bomrow.save()
        return bomrow

    def enable_bomrow(self, bomrow):
        """
        Enable a company bomrow, if it is disabled
        """
        bomrow = self.list_bomrows(bomrow.bom.id).get(id=bomrow.id)
        if bomrow.status == 0:
            bomrow.status = 1
            bomrow.save()
        return bomrow

    def disable_bomrow(self, bomrow):
        """
        Disable a company bomrow, if it is enabled
        """
        bomrow = self.list_bomrows(bomrow.bom.id).get(id=bomrow.id)
        if bomrow.status == 1:
            bomrow.status = 0
            bomrow.save()
        return bomrow

    def remove_bomrow(self, bomrow):
        """
        Delete a company bomrow
        """
        bomrow = self.list_bomrows(bomrow.bom.id).get(id=bomrow.id)
        bomrow.delete()

    # ------ QUOTATION ------

    def create_quotation(self, quotation_dict):
        # Todo: Add permission
        with transaction.atomic():
            quotation_row_dict = quotation_dict.pop('quotation_rows', [])

            quotation = Quotation(
                creator=self.user,
                last_modifier=self.user,
                owner=self.company,
                contact=self,
                **quotation_dict
            )
            quotation.save()

            for quotation_rw in quotation_row_dict:
                quotation_row = QuotationRow(
                    creator=self.user,
                    last_modifier=self.user,
                    quotation=quotation,
                    **quotation_rw
                )
                quotation_row.save()

        return quotation

    def list_quotations(self):
        """
        Get all company Quotations
        """
        return self.company.quotations.all()

    def list_sent_quotations(self):
        """
        Get all company sender Quotations
        """
        return self.company.quotations.filter(is_draft=False, is_completed=True)

    def list_draft_quotations(self):
        """
        Get all company draft Quotations
        """
        return self.company.quotations.filter(is_draft=True)

    def list_received_quotations(self):
        """
        Get all company receiver Quotations
        """
        return Quotation.objects.filter(
            bom__owner_id=self.company.id,
            bom__is_draft=False,
            is_draft=False,
            is_completed=True
        )

    def list_project_quotations(self, project_id):
        boms = self.list_project_boms(project_id)
        quotation_queryset = []
        for bom in boms:
            quotation_queryset.append(bom.quotations.all())
        return list(chain(*quotation_queryset))

    def list_project_sender_quotations(self, project_id):
        project = self.get_project(project_id)
        return self.company.quotations.filter(bom__project=project, is_draft=False, is_completed=True)

    def list_project_draft_quotations(self, project_id):
        project = self.get_project(project_id)
        return self.company.quotations.filter(bom__project=project, is_draft=True)

    def list_project_receiver_quotations(self, project_id):
        project = self.get_project(project_id)
        return Quotation.objects.filter(
            bom__project=project,
            bom__owner_id=self.company.id,
            bom__is_draft=False,
            is_draft=False,
            is_completed=True
        )
        # quotation_queryset = []
        # for bom in self.list_project_sender_boms(project_id):
        #     selected_companies = list(bom.selected_companies.all().values_list('id', flat=True))
        #     quotation_queryset.append(bom.quotations.filter(owner__in=selected_companies))
        # return list(chain(*quotation_queryset))

    def get_quotation(self, quotation_id):
        """
        Get view header and quotation rows of a specification
        """
        # Todo: Ameliorate
        quotation = self.list_quotations().get(id=quotation_id)
        quotation_dict = {
            'quotation': quotation,
            'quotation_rows:': quotation.quotation_rows.all()
        }
        return quotation_dict

    def get_draft_quotation(self, quotation_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        quotation = self.list_draft_quotations().get(id=quotation_id)
        quotation_dict = {
            'quotation': quotation,
            'quotation_rows:': quotation.quotation_rows.all()
        }
        return quotation_dict

    def get_received_quotation(self, quotation_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        quotation = self.list_received_quotations().get(id=quotation_id)
        quotation_dict = {
            'quotation': quotation,
            'quotation_rows:': quotation.quotation_rows.all()
        }
        return quotation_dict

    def get_sent_quotation(self, quotation_id):
        """
        Get view header and bom rows of a specification
        """
        # Todo: Ameliorate
        quotation = self.list_sent_quotations().get(id=quotation_id)
        quotation_dict = {
            'quotation': quotation,
            'quotation_rows:': quotation.quotation_rows.all()
        }
        return quotation_dict

    def edit_quotation(self, quotation_dict):
        """
        Update a company quotation
        """
        quotation = self.list_quotations().get(id=quotation_dict['id'])
        quotation.__dict__.update(**quotation_dict)
        quotation.save()
        return quotation

    def accept_quotation(self, quotation_dict):
        quotation = self.list_received_quotations().get(id=quotation_dict['id'])
        quotation.is_accepted = True
        quotation.save()
        return quotation

    def enable_quotation(self, quotation):
        """
        Enable a company quotation, if it is disabled
        """
        quotation = self.list_quotations().get(id=quotation.id)
        if quotation.status == 0:
            quotation.status = 1
            quotation.save()
        return quotation

    def disable_quotation(self, quotation):
        """
        Disable a company quotation, if it is enabled
        """
        quotation = self.list_quotations().get(id=quotation.id)
        if quotation.status == 1:
            quotation.status = 0
            quotation.save()
        return quotation

    def remove_quotation(self, quotation):
        """
        Delete a company quotation
        """
        quotation = self.list_quotations().get(id=quotation.id)
        quotation.delete()

    def archive_quotation(self, quotationarchive_dict):
        quotation_archive = QuotationArchive(
            creator=self.user,
            last_modifier=self.user,
            ** quotationarchive_dict
        )
        quotation_archive.save()
        return quotation_archive

    # ------ QUOTATION ROW ------

    def create_quotationrow(self, quotationrow_dict):
        self.list_quotations().get(id=quotationrow_dict['quotation'].id)
        quotationrow = QuotationRow(
            creator=self.user,
            last_modifier=self.user,
            **quotationrow_dict
        )
        quotationrow.save()
        return quotationrow

    def list_quotationrows(self, quotation_id):
        """
        Get all company quotationrows
        """
        quotation = self.list_quotations().get(id=quotation_id)
        return quotation.quotation_rows.all()

    def list_draft_quotationrows(self, quotation_id):
        """
        Get all company draft quotationrows
        """
        quotation = self.list_draft_quotations().get(id=quotation_id)
        return quotation.quotation_rows.all()

    def list_sent_quotationrows(self, quotation_id):
        """
        Get all company sent quotationrows
        """
        quotation = self.list_sent_quotations().get(id=quotation_id)
        return quotation.quotation_rows.all()

    def list_received_quotationrows(self, quotation_id):
        """
        Get all company received quotationrows
        """
        quotation = self.list_received_quotations().get(id=quotation_id)
        return quotation.quotation_rows.all()

    def get_quotationrow(self, quotationrow_id):
        """
        Get quotationrow
        """
        # Todo: Ameliorate
        quotation = self.list_quotations().get(quotation_rows__id=quotationrow_id)
        quotationrow = quotation.quotation_rows.all().get(id=quotationrow_id)
        return quotationrow

    def edit_quotationrow(self, quotationrow_dict):
        """
        Update a company quotationrow
        """
        quotationrow = self.list_quotationrows(quotationrow_dict['quotation'].id).get(id=quotationrow_dict['id'])
        quotationrow.__dict__.update(**quotationrow_dict)
        quotationrow.save()
        return quotationrow

    def enable_quotationrow(self, quotationrow):
        """
        Enable a company quotationrow, if it is disabled
        """
        quotationrow = self.list_quotationrows(quotationrow.quotation.id).get(id=quotationrow.id)
        if quotationrow.status == 0:
            quotationrow.status = 1
            quotationrow.save()
        return quotationrow

    def disable_quotationrow(self, quotationrow):
        """
        Disable a company quotationrow, if it is enabled
        """
        quotationrow = self.list_quotationrows(quotationrow.quotation.id).get(id=quotationrow.id)
        if quotationrow.status == 1:
            quotationrow.status = 0
            quotationrow.save()
        return quotationrow

    def remove_quotationrow(self, quotationrow):
        """
        Delete a company quotationrow
        """
        quotationrow = self.list_quotationrows(quotationrow.quotation.id).get(id=quotationrow.id)
        quotationrow.delete()

    # ------ OFFER ------

    def create_offer(self, offer_dict):
        offer = Offer(
            owner=self.company,
            contact=self,
            creator=self.user,
            last_modifier=self.user,
            **offer_dict
        )
        offer.save()
        return offer

    def list_offers(self):
        """
        Get all company offers
        """
        return self.company.offers.all()

    def list_active_offers(self):
        """
        Get all company offers
        """
        return self.company.offers.filter(status=1, deadline__gte=datetime.date.today())

    def list_received_offers(self):
        """
        Get all received company offers
        """
        return Offer.objects.filter(
            status=1,
            is_draft=False,
            deadline__gte=datetime.date.today()
        ).exclude(owner=self.company).distinct()

    def list_received_favourite_offers(self):
        return self.followings_offers.filter(
            status=1,
            is_draft=False,
            deadline__gte=datetime.date.today()
        ).exclude(owner=self.company).distinct()

    def list_received_required_offers(self):
        return self.buying_offers.filter(
            status=1,
            is_draft=False,
            deadline__gte=datetime.date.today()
        ).exclude(owner=self.company).distinct()

    def list_sent_offers(self):
        return self.list_active_offers().filter(is_draft=False)

    def list_draft_offers(self):
        return self.list_active_offers().filter(is_draft=True)

    def get_offer(self, offer_id):
        """
        Get company offer
        """
        offer = self.list_offers().get(id=offer_id)
        return offer

    def edit_offer(self, offer_dict):
        """
        Update a company offer
        """
        offer = self.list_offers().get(id=offer_dict['id'])
        offer.__dict__.update(**offer_dict)
        offer.save()
        return offer

    def enable_offer(self, offer):
        """
        Enable a company offer, if it is disabled
        """
        offer = self.list_offers().get(id=offer.id)
        if offer.status == 0:
            offer.status = 1
            offer.save()
        return offer

    def disable_offer(self, offer):
        """
        Disable a company offer, if it is enabled
        """
        offer = self.list_offers().get(id=offer.id)
        if offer.status == 1:
            offer.status = 0
            offer.save()
        return offer

    def remove_offer(self, offer):
        """
        Delete a company offer
        """
        offer = self.list_offers().get(id=offer.id)
        offer.delete()

    def follow_offer(self, offer):
        favourite = FavouriteOffer(
            creator=self.user, last_modifier=self.user,
            profile=self, **offer
        )
        favourite.save()
        return favourite

    def unfollow_offer(self, offer):
        FavouriteOffer.objects.get(profile=self, offer=offer).delete()

    def buy_offer(self, offer):
        bought = BoughtOffer(
            creator=self.user, last_modifier=self.user,
            profile=self, **offer
        )
        bought.save()
        return bought

    def cancel_buy_offer(self, offer):
        BoughtOffer.objects.get(profile=self, offer=offer).delete()


    # ------ CERTIFICATION ------

    def create_certification(self, cert_dict):
        certification = Certification(
            owner=self.company,
            contact=self,
            creator=self.user,
            last_modifier=self.user,
            **cert_dict
        )
        certification.save()
        return certification

    def list_certifications(self):
        """
        Get all company certifications
        """
        return self.company.certifications.all()

    def get_certification(self, cert_id):
        """
        Get company certification
        """
        cert = self.list_certifications().get(id=cert_id)
        return cert

    def edit_certification(self, cert_dict):
        """
        Update a company certification
        """
        cert = self.list_certifications().get(id=cert_dict['id'])
        cert.__dict__.update(**cert_dict)
        cert.save()
        return cert

    def enable_certification(self, cert):
        """
        Enable a company certification, if it is disabled
        """
        cert = self.list_certifications().get(id=cert.id)
        if cert.status == 0:
            cert.status = 1
            cert.save()
        return cert

    def disable_certification(self, cert):
        """
        Disable a company certification, if it is enabled
        """
        cert = self.list_certifications().get(id=cert.id)
        if cert.status == 1:
            cert.status = 0
            cert.save()
        return cert

    def remove_certification(self, cert):
        """
        Delete a company certification
        """
        cert = self.list_certifications().get(id=cert.id)
        cert.delete()

    # ------ DOCUMENT ------

    def create_document(self, document_dict):
        additional_path = None
        if document_dict['content_type'].model == 'project':
            self.get_project(document_dict['object_id'])
        elif document_dict['content_type'].model == 'company':
            self.get_company(document_dict['object_id'])
        elif document_dict['content_type'].model == 'profile':
            self.get_profile(document_dict['object_id'])
        elif document_dict['content_type'].model == 'bom':
            self.get_bom(document_dict['object_id'])
        else:
            raise django_exception.OwnerProfilePermissionDenied(_('Please select the correct content type'))
        if 'additional_path' in document_dict:
            additional_path = document_dict.pop('additional_path')
        document = Document(
            creator=self.user,
            last_modifier=self.user,
            **document_dict
        )
        if additional_path:
            document.additional_path = additional_path
        if 'name' in document_dict['document']:
            document.document.save(document_dict['document'].name, document_dict['document'])
        document.save()
        return document

    def list_documents(self):
        """
        Get all documents linked to the company
        """
        return Document.objects.filter(
            Q(companies=self.company) |
            Q(projects__company=self.company) |
            Q(profiles__company=self.company) |
            Q(boms__owner=self.company)
        )

    def list_company_documents(self):
        """
        Get all company documents
        """
        return Document.objects.filter(companies=self.company)

    def list_private_company_documents(self):
        """
        Get all private company documents
        """
        return Document.objects.filter(companies=self.company, is_public=False)

    def list_public_company_documents(self):
        """
        Get all public company documents
        """
        return Document.objects.filter(companies=self.company, is_public=True)

    def list_project_documents(self, project=None):
        """
        Get all project documents linked to the company/project
        """
        query1 = {'projects__company': self.company}
        query2 = {'projects__profiles__id': self.id}
        if project:
            query1.update({'projects__id': project.id})

        return Document.objects.filter(Q(**query1) | Q(**query2))

    def list_project_parent_documents(self, project_id):
        """
        Get all project documents linked to the company/project
        """
        project = self.get_parent_project(project_id)
        return Document.objects.filter(projects__id= project.id)

    def list_profile_documents(self):
        """
        Get all company profile documents linked to the company
        """
        return Document.objects.filter(profiles__company=self.company)

    def list_bom_documents(self):
        """
        Get all bom documents linked to the company
        """
        return Document.objects.filter(boms__owner=self.company)

    def list_sent_bom_documents(self, bom=None):
        """
        Get all sent bom documents linked to the company
        """
        query = {'boms__owner': self.company,
                 'boms__is_draft': False}

        if bom:
            query.update({'boms__id': bom.id})
        return Document.objects.filter(**query)

    def list_draft_bom_documents(self, bom=None):
        """
        Get all draft bom documents linked to the company
        """
        query = {'boms__owner': self.company,
                 'boms__is_draft': True}

        if bom:
            query.update({'boms__id': bom.id})
        return Document.objects.filter(**query)

    def list_received_bom_documents(self, bom=None):
        """
        Get all received bom documents linked to the company
        """
        query = {'boms__selected_companies': self.company,
                 'boms__is_draft': False}

        if bom:
            query.update({'boms__id': bom.id})
        return Document.objects.filter(**query)

    def get_document(self, document_id):
        """
        Get company document
        """
        document = self.list_documents().get(id=document_id)
        return document

    def edit_document(self, document_dict):
        document = self.list_documents().get(id=document_dict['id'])
        if 'document' in document_dict:
            # Deletes the document media
            os.remove(document.document.file.name)

        document.__dict__.update(document_dict)

        if 'document' in document_dict:
            document.document.save(document_dict['document'].name, document_dict['document'])
        document.save()
        return document

    def remove_document(self, document):
        document = self.list_documents().get(id=document.id)
        # Deletes the document media
        os.remove(document.document.file.name)
        # Deletes the document instance
        document.delete()

    # ------ PHOTO ------

    def create_photo(self, photo_dict):
        additional_path = None
        if photo_dict['content_type'].model == 'project':
            self.get_project(photo_dict['object_id'])
        elif photo_dict['content_type'].model == 'company':
            self.get_company(photo_dict['object_id'])
        elif photo_dict['content_type'].model == 'bom':
            self.get_bom(photo_dict['object_id'])
        else:
            raise django_exception.OwnerProfilePermissionDenied(_('Please select the correct content type'))
        if 'additional_path' in photo_dict:
            additional_path = photo_dict.pop('additional_path')
        photo = Photo(
            creator=self.user,
            last_modifier=self.user,
            pub_date=datetime.datetime.now(),
            **photo_dict
        )
        if additional_path:
            photo.additional_path = additional_path

        if 'name' in photo_dict['photo']:
            photo.photo.save(photo_dict['photo'].name, photo_dict['photo'])
        photo.save()
        return photo

    def list_photos(self):
        """
        Get all photos linked to the company
        """
        return Photo.objects.filter(
            Q(companies=self.company) |
            Q(projects__company=self.company) |
            Q(boms__owner=self.company)
        )

    def list_company_photos(self):
        """
        Get all company photos
        """
        return Photo.objects.filter(companies=self.company)

    def list_private_company_photos(self):
        """
        Get all private company photos
        """
        return Photo.objects.filter(companies=self.company, is_public=False)

    def list_public_company_photos(self):
        """
        Get all public company photos
        """
        return Photo.objects.filter(companies=self.company, is_public=True)

    def list_project_photos(self, project=None):
        """
        Get all project photos of the company/project
        """
        query1 = {'projects__company': self.company}
        query2 = {'projects__profiles__id': self.id}
        if project:
            query1.update({'projects__id': project.id})

        return Photo.objects.filter(Q(**query1) | Q(**query2))

    def list_project_folders(self, project=None):
        """
        Get all project folders of the company/project
        """
        query1 = {'projects__company': self.company}
        query2 = {'projects__profiles__id': self.id}
        if project:
            query1.update({'projects__id': project.id})

        return Folder.objects.filter(Q(**query1) | Q(**query2))

    def list_bom_photos(self):
        """
        Get all bom photos of the company
        """
        return Photo.objects.filter(boms__owner=self.company)

    def list_sent_bom_photos(self, bom=None):
        """
        Get all sent bom photos linked to the company
        """
        query = {'boms__owner': self.company,
                 'boms__is_draft': False}

        if bom:
            query.update({'boms__id': bom.id})
        return Photo.objects.filter(**query)

    def list_draft_bom_photos(self, bom=None):
        """
        Get all draft bom documents linked to the company
        """
        query = {'boms__owner': self.company,
                 'boms__is_draft': True}

        if bom:
            query.update({'boms__id': bom.id})
        return Photo.objects.filter(**query)

    def list_received_bom_photos(self, bom=None):
        """
        Get all received bom documents linked to the company
        """
        query = {'boms__selected_companies': self.company,
                 'boms__is_draft': False}

        if bom:
            query.update({'boms__id': bom.id})
        return Photo.objects.filter(**query)

    def get_photo(self, photo_id):
        """
        Get company photo
        """
        photo = self.list_photos().get(id=photo_id)
        return photo

    def edit_photo(self, photo_dict):
        photo = self.list_photos().get(id=photo_dict['id'])
        if 'photo' in photo_dict:
            # Deletes the photo media
            os.remove(photo.photo.file.name)

        photo.__dict__.update(**photo_dict)

        if 'photo' in photo_dict:
            photo.photo.save(photo_dict['photo'].name, photo_dict['photo'])
        photo.save()
        return photo

    def remove_photo(self, photo):
        photo = self.list_photos().get(id=photo.id)
        # Deletes the photo media
        os.remove(photo.photo.file.name)
        # Deletes the photo instance
        photo.delete()

    # ------ VIDEO ------

    def create_video(self, video_dict):
        additional_path = None
        if video_dict['content_type'].model == 'project':
            self.get_project(video_dict['object_id'])
        elif video_dict['content_type'].model == 'company':
            self.get_company(video_dict['object_id'])
        elif video_dict['content_type'].model == 'bom':
            self.get_bom(video_dict['object_id'])
        else:
            raise django_exception.OwnerProfilePermissionDenied(_('Please select the correct content type'))
        if 'additional_path' in video_dict:
            additional_path = video_dict.pop('additional_path')
        video = Video(
            creator=self.user,
            last_modifier=self.user,
            pub_date=datetime.datetime.now(),
            **video_dict
        )
        if additional_path:
            video.additional_path = additional_path
        if 'name' in video_dict['video']:
            video.video.save(video_dict['video'].name, video_dict['video'])
        video.save()
        return video

    def create_folder(self, folder_dict):
        if folder_dict['content_type'].model == 'project':
            self.get_project(folder_dict['object_id'])
        elif folder_dict['content_type'].model == 'company':
            self.get_company(folder_dict['object_id'])
        elif folder_dict['content_type'].model == 'bom':
            self.get_bom(folder_dict['object_id'])
        else:
            raise django_exception.OwnerProfilePermissionDenied(_('Please select the correct content type'))

        if 'parent' in folder_dict and folder_dict['parent']:
            folder_dict['is_root'] = False
        else:
            folder_dict['is_root'] = True


        folder = Folder(
            creator=self.user,
            last_modifier=self.user,
            **folder_dict
        )
        folder.save()
        return folder

    def list_videos(self):
        """
        Get all videos linked to the company
        """
        return Video.objects.filter(
            Q(companies=self.company) |
            Q(projects__company=self.company) |
            Q(boms__owner=self.company)
        )

    def list_folders(self):
        """
        Get all folders linked to the company
        """
        return Folder.objects.filter(
            Q(companies=self.company) |
            Q(projects__company=self.company)
        )
    def list_company_folders(self):
        """
        Get all folders linked to the company
        """
        return Folder.objects.filter(companies=self.company, is_root=True)

    def list_company_videos(self):
        """
        Get all company videos
        """
        return Video.objects.filter(companies=self.company)

    def list_private_company_videos(self):
        """
        Get all private company videos
        """
        return Video.objects.filter(companies=self.company, is_public=False)

    def list_public_company_videos(self):
        """
        Get all public company videos
        """
        return Video.objects.filter(companies=self.company, is_public=True)

    def list_project_videos(self, project=None):
        """
        Get all project videos of the company
        """
        query1 = {'projects__company': self.company}
        query2 = {'projects__profiles__id': self.id}
        if project:
            query1.update({'projects__id': project.id})

        return Video.objects.filter(Q(**query1) | Q(**query2))

    def list_bom_videos(self):
        """
        Get all bom videos of the company
        """
        return Video.objects.filter(boms__owner=self.company)

    def list_sent_bom_videos(self, bom=None):
        """
        Get all sent bom videos linked to the company
        """
        query = {'boms__owner': self.company,
                 'boms__is_draft': False}

        if bom:
            query.update({'boms__id': bom.id})
        return Video.objects.filter(**query)

    def list_draft_bom_videos(self, bom=None):
        """
        Get all draft bom videos linked to the company
        """
        query = {'boms__owner': self.company,
                 'boms__is_draft': True}

        if bom:
            query.update({'boms__id': bom.id})
        return Video.objects.filter(**query)

    def list_received_bom_videos(self, bom=None):
        """
        Get all received bom videos linked to the company
        """
        query = {'boms__selected_companies': self.company,
                 'boms__is_draft': False}

        if bom:
            query.update({'boms__id': bom.id})
        return Video.objects.filter(**query)

    def get_video(self, video_id):
        """
        Get company video
        """
        video = self.list_videos().get(id=video_id)
        return video

    def edit_video(self, video_dict):
        video = self.list_videos().get(id=video_dict['id'])
        if 'video' in video_dict:
            # Deletes the video media
            os.remove(video.video.file.name)

        video.__dict__.update(**video_dict)

        if 'video' in video_dict:
            video.video.save(video_dict['video'].name, video_dict['video'])
        video.save()
        return video

    def remove_video(self, video):
        video = self.list_videos().get(id=video.id)
        # Deletes the video media
        os.remove(video.video.file.name)
        # Deletes the video instance
        video.delete()

    def get_folder(self, folder_id):
        """
        Get company folder
        """
        folder = self.list_folders().get(id=folder_id)
        return folder

    def edit_folder(self, folder_dict):
        folder = self.list_folders().get(id=folder_dict['id'])
        folder.__dict__.update(**folder_dict)
        folder.save()
        return folder

    def remove_folder(self, folder):
        folder = self.list_folders().get(id=folder.id)
        folder.delete()

    # ------ TALK ------

    def get_or_create_talk(self, talk_dict):
        content_type = ContentType.objects.get_for_id(talk_dict['content_type'].id)
        if talk_dict['object_id'] == self.id:
            raise django_exception.MessageAddPermissionDenied(_('You can\'t send the message to yourself'))

        if content_type.model == 'profile':
            query = (
                Q(content_type=content_type)
                & (
                    Q(object_id=self.id)
                    | Q(messages__sender_id=self.id)
                )
                & (
                    Q(object_id=talk_dict['object_id'])
                    | Q(messages__sender_id=talk_dict['object_id'])
                )
            )
        else:
            query = (
                Q(content_type=content_type)
                & Q(object_id=talk_dict['object_id'])
            )

        talk = Talk.objects.filter(query)
        if not talk:
            talk = Talk(
                creator=self.user,
                last_modifier=self.user,
                **talk_dict
            )
            talk.save()
            return talk
        else:
            return talk.first()

    def list_talks(self):
        """
        Get all talks linked to the company
        """
        return Talk.objects.filter(
            Q(companies=self.company) |
            Q(projects__company=self.company) |
            Q(profiles__company=self.company)
        )

    def list_all_talks(self):
        received = self.list_talks()
        sent = Talk.objects.filter(
            messages__sender=self
        )
        return sent.union(received).distinct()

    def list_followed_company_talks(self, main_profile):

        # Talk.objects.filter(
        #     Q(companies=self.company) |
        #     Q(projects__company=self.company) |
        #     Q(profiles__company=self.company)
        # )
        #
        # received = self.list_talks().filter(
        #     messages__sender__is_shared=True,
        #     messages__sender__company__followers=main_profile)
        # sent = Talk.objects.filter(
        #     messages__sender=self
        # ) # TODO
        # return sent.union(received).distinct()
        return self.list_talks()

    def list_company_talks(self):
        """
        Get all company talks
        """
        return Talk.objects.filter(companies=self.company)

    def list_project_talks(self, project=None):
        """
        Get all project talks of the company/project
        """
        query = {'projects__company': self.company}
        if project:
            query.update({'projects__id': project.id})

        return Talk.objects.filter(**query)

    def list_project_messages(self, project=None):
        """
        Get all project messages of the project
        """
        content_type_id = ContentType.objects.get(model='project').id
        query = {'talk__content_type_id': content_type_id, 'talk__object_id': project.id}
        return Message.objects.filter(**query)

    def list_company_messages(self):
        content_type_id = ContentType.objects.get(model='company').id
        return Message.objects.filter(
            talk__content_type_id=content_type_id,
            talk__object_id=self.company.id)

    def list_profile_messages(self):
        content_type_id = ContentType.objects.get(model='profile').id
        query = Q(talk__content_type_id=content_type_id) & (
                    Q(sender=self) | Q(talk__object_id=self.id)
        )
        return Message.objects.filter(query)

    def list_profile_talks(self):
        """
        Get all company profile talks of the company
        """
        return Talk.objects.filter(profiles__company=self.company)

    def list_profile_to_profile_talks(self):
        """
         Get all profile talks of the profile
        """
        content_type_id = ContentType.objects.get(model='profile').id
        return Talk.objects.filter(
            Q(content_type_id=content_type_id) & (
                Q(object_id=self.id) | Q(messages__sender_id=self.id)
            )
        ).distinct()

    def get_talk(self, talk_id):
        talk = self.list_talks().get(id=talk_id)
        return talk

    def remove_talk(self, talk):
        talk = self.list_talks().get(id=talk.id)
        talk.delete()

    # ------ MESSAGE ------

    def create_message(self, message_dict):
        talk_dict = message_dict.pop('talk')
        talk = self.get_or_create_talk(talk_dict[0])

        message = Message(
            creator=self.user,
            last_modifier=self.user,
            sender=self,
            talk=talk,
            status=0,
            body=message_dict['body'][0],
            unique_code=message_dict['unique_code'][0]
        )
        message.save()
        if talk.content_type.name == 'project':
            staffs = []
            project = Project.objects.get(id=talk.object_id)
            teams = project.members.filter(
                status=1,
                project_invitation_date__isnull=False,
                invitation_refuse_date__isnull=True,
            )
            for team in teams:
                staffs.append(team.profile)
        else:
            staffs = self.company.get_active_staff()

        for staff in staffs:
            MessageProfileAssignment.objects.create(
                message=message,
                profile=staff
            )
        return message

    def list_messages(self):
        return self.sent_messages.all()

    def list_sent_messages(self):
        return self.sent_messages.all()

    def list_received_messages(self):
        # Todo: Optimize the code (may be use managers)
        talks = self.list_talks()
        message_queryset = []
        for talk in talks:
            # message_queryset.append(talk.messages.exclude(sender=self))
            message_queryset.append(talk.messages.all())
        return list(chain(*message_queryset))

    def list_profile_received_messages(self):
        # Todo: Optimize the code (may be use managers)
        talks = self.list_profile_talks()
        message_queryset = []
        for talk in talks:
            # message_queryset.append(talk.messages.exclude(sender=self))
            message_queryset.append(talk.messages.all())
        return list(chain(*message_queryset))

    def get_message(self, message_id):
        return self.list_messages().get(pk=message_id)

    def remove_message(self, message):
        message = self.list_messages().get(pk=message.id)
        message.delete()

    # ------ FAVOURITE ------

    def follow_company(self, company):
        favourite = Favourite(
            creator=self.user, last_modifier=self.user,
            company_followed=company, company=self.company
        )
        favourite.save()
        return favourite

    def list_favourites(self):
        """
        Company followings (Profile --> Company)
        :return: Companies
        """
        return self.company.create_favourites.filter(approval_date__isnull=False, refuse_date__isnull=True)

    def list_waiting_favourites(self):
        """
        Company followings (MainProfile --> Company)
        :return: Companies
        """
        return self.company.create_favourites.filter(approval_date__isnull=True, refuse_date__isnull=True)

    def list_received_favourites(self):
        return self.company.request_favourites.filter(
            approval_date__isnull=True,
            refuse_date__isnull=True,
            invitation_date__isnull=False)

    def list_followers(self): # TODO
        """
        Company followers (Company <---- Profile)
        :return: Profiles
        """
        #return self.company.followers.all()

    def accept_follower(self, company):
        follow = self.company.request_favourites.get(company=company)
        follow.approval_date = datetime.datetime.now()
        follow.save()
        follow_req = Favourite.objects.filter(company=self.company, company_followed=company)
        if follow_req:
            follow_req.update(approval_date=datetime.datetime.now(), refuse_date=None)
        else:
            new_follow = Favourite()
            new_follow.company = self.company
            new_follow.company_followed = company
            new_follow.invitation_date = datetime.datetime.now()
            new_follow.approval_date = datetime.datetime.now()
            new_follow.creator = self.user
            new_follow.last_modifier = self.user
            new_follow.save()
        return follow

    def get_favourite(self, favourite_id):
        favourite = self.favourites.all().get(id=favourite_id)
        return favourite.company

    def remove_follower(self, instance):
        favourite = self.company.request_favourites.all().get(id=instance.id)
        favourite.delete()

    def list_favourites_public_contact(self):
        favourites_qs = self.list_favourites()
        company_id_list = [fav.company_followed.id for fav in favourites_qs]
        company_id_list.append(self.company.id)
        return Profile.objects.filter(
            status=1,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
            is_shared=True,
            company__id__in=company_id_list,
        )

    def list_favourites_owners(self):
        favourites_qs = self.list_favourites()
        company_id_list = [fav.company_followed.id for fav in favourites_qs]
        company_id_list.append(self.company.id)
        return Profile.objects.filter(
            status=1,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
            role=settings.OWNER,
            company__id__in=company_id_list,
        )

    # ------ SPONSOR ------

    def create_sponsor_request(self, data):
        sponsor = Sponsor(
            creator=self.user, last_modifier=self.user,
            company=self.company, short_description=data['short_description'],
            status=2
        )
        sponsor.save()
        return sponsor

    def get_active_sponsor_list(self):
        query_categories = Q(tags={})
        for category in self.company.category:
            query_categories |= Q(tags__has_key=category)
        query = Q(status=1) & query_categories
        return Sponsor.objects.filter(query).distinct()



@python_2_unicode_compatible
class DelegateProfile(OwnerProfile):
    objects = managers.DelegateProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('delegate profile')
        verbose_name_plural = _('delegate profiles')
        permissions = (
            ("list_delegateprofile", "can list delegate profile"),
            ("detail_delegateprofile", "can detail delegate profile"),
            ("disable_delegateprofile", "can disable delegate profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)


@python_2_unicode_compatible
class Level1Profile(OwnerProfile):
    objects = managers.Level1ProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('level 1 profile')
        verbose_name_plural = _('level 1 profiles')
        permissions = (
            ("list_level1profile", "can list level 1 profile"),
            ("detail_level1profile", "can detail level 1 profile"),
            ("disable_level1profile", "can disable level 1 profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)

    def __init__(self, *args, **kwargs):
        super(Level1Profile, self).__init__(*args, **kwargs)
        delattr(OwnerProfile, 'edit_notification_receipient')
        delattr(OwnerProfile, 'remove_notification_receipient')
        delattr(OwnerProfile, 'create_owner')
        delattr(OwnerProfile, 'create_delegate')
        delattr(OwnerProfile, 'create_level1')
        delattr(OwnerProfile, 'create_level2')
        delattr(OwnerProfile, 'create_phantom')
        delattr(OwnerProfile, 'edit_profile')
        delattr(OwnerProfile, 'enable_profile')
        delattr(OwnerProfile, 'disable_profile')
        delattr(OwnerProfile, 'remove_profile')
        delattr(OwnerProfile, 'edit_company')
        delattr(OwnerProfile, 'enable_company')
        delattr(OwnerProfile, 'disable_company')
        delattr(OwnerProfile, 'remove_company')
        delattr(OwnerProfile, 'create_partnership')
        delattr(OwnerProfile, 'accept_partnership')
        delattr(OwnerProfile, 'refuse_partnership')
        delattr(OwnerProfile, 'remove_partnership')
        delattr(OwnerProfile, 'create_project')
        delattr(OwnerProfile, 'clone_project')
        delattr(OwnerProfile, 'edit_project')
        delattr(OwnerProfile, 'enable_project')
        delattr(OwnerProfile, 'disable_project')
        delattr(OwnerProfile, 'remove_project')
        delattr(OwnerProfile, 'create_task')
        delattr(OwnerProfile, 'share_task')
        delattr(OwnerProfile, 'clone_task')
        delattr(OwnerProfile, 'edit_task')
        delattr(OwnerProfile, 'update_shared_task_progress')
        delattr(OwnerProfile, 'assign_task')
        delattr(OwnerProfile, 'enable_task')
        delattr(OwnerProfile, 'disable_task')
        delattr(OwnerProfile, 'close_task')
        delattr(OwnerProfile, 'open_task')
        delattr(OwnerProfile, 'remove_task')
        delattr(OwnerProfile, 'create_task_activity')
        delattr(OwnerProfile, 'edit_task_activity')
        delattr(OwnerProfile, 'remove_task_activity')
        delattr(OwnerProfile, 'create_member')
        delattr(OwnerProfile, 'edit_member')
        delattr(OwnerProfile, 'remove_member')
        delattr(OwnerProfile, 'create_bom')
        delattr(OwnerProfile, 'edit_bom')
        delattr(OwnerProfile, 'enable_bom')
        delattr(OwnerProfile, 'disable_bom')
        delattr(OwnerProfile, 'remove_bom')
        delattr(OwnerProfile, 'archive_bom')
        delattr(OwnerProfile, 'create_bomrow')
        delattr(OwnerProfile, 'edit_bomrow')
        delattr(OwnerProfile, 'enable_bomrow')
        delattr(OwnerProfile, 'disable_bomrow')
        delattr(OwnerProfile, 'remove_bomrow')
        delattr(OwnerProfile, 'create_quotation')
        delattr(OwnerProfile, 'edit_quotation')
        delattr(OwnerProfile, 'accept_quotation')
        delattr(OwnerProfile, 'enable_quotation')
        delattr(OwnerProfile, 'disable_quotation')
        delattr(OwnerProfile, 'remove_quotation')
        delattr(OwnerProfile, 'archive_quotation')
        delattr(OwnerProfile, 'create_quotationrow')
        delattr(OwnerProfile, 'edit_quotationrow')
        delattr(OwnerProfile, 'enable_quotationrow')
        delattr(OwnerProfile, 'disable_quotationrow')
        delattr(OwnerProfile, 'remove_quotationrow')
        delattr(OwnerProfile, 'create_offer')
        delattr(OwnerProfile, 'edit_offer')
        delattr(OwnerProfile, 'enable_offer')
        delattr(OwnerProfile, 'disable_offer')
        delattr(OwnerProfile, 'remove_offer')
        delattr(OwnerProfile, 'follow_offer')
        delattr(OwnerProfile, 'unfollow_offer')
        delattr(OwnerProfile, 'buy_offer')
        delattr(OwnerProfile, 'cancel_buy_offer')
        delattr(OwnerProfile, 'create_certification')
        delattr(OwnerProfile, 'edit_certification')
        delattr(OwnerProfile, 'enable_certification')
        delattr(OwnerProfile, 'disable_certification')
        delattr(OwnerProfile, 'remove_certification')
        delattr(OwnerProfile, 'create_document')
        delattr(OwnerProfile, 'edit_document')
        delattr(OwnerProfile, 'remove_document')
        delattr(OwnerProfile, 'create_photo')
        delattr(OwnerProfile, 'edit_photo')
        delattr(OwnerProfile, 'remove_photo')
        delattr(OwnerProfile, 'create_video')
        delattr(OwnerProfile, 'edit_video')
        delattr(OwnerProfile, 'remove_video')
        delattr(OwnerProfile, 'remove_talk')
        delattr(OwnerProfile, 'remove_message')
        delattr(OwnerProfile, 'remove_favourite')
        delattr(OwnerProfile, 'follow_company')
        delattr(OwnerProfile, 'list_received_favourites')
        delattr(OwnerProfile, 'accept_follower')
        delattr(OwnerProfile, 'remove_follower')


@python_2_unicode_compatible
class Level2Profile(Level1Profile):
    objects = managers.Level2ProfileManager()

    class Meta:
        proxy = True
        verbose_name = _('level 2 profile')
        verbose_name_plural = _('level 2 profiles')
        permissions = (
            ("list_level2profile", "can list level 2 profile"),
            ("detail_level2profile", "can detail level 2 profile"),
            ("disable_level2profile", "can disable level 2 profile"),
        )

    def __str__(self):
        return "({}) {} {}".format(self.get_role_display(), self.last_name, self.first_name)


@python_2_unicode_compatible
class Favourite(UserModel, DateModel):
    # profile = models.ForeignKey(
    #     Profile,
    #     on_delete=models.CASCADE,
    #     related_name='favourites',
    #     verbose_name=_('contact'),
    # )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='create_favourites',
        verbose_name=_('company'),
    )
    company_followed = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='request_favourites',
        verbose_name=_('company followed'),
    )
    invitation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('invitation request date'),
    )
    approval_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('invitation approval date'),
    )
    refuse_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('invitation refuse date'),
    )

    class Meta:
        verbose_name = _('favourite')
        verbose_name_plural = _('favourites')
        permissions = (
            ("list_favourite", "can list favourite"),
            ("detail_favourite", "can detail favourite"),
        )
        unique_together = (('company_followed', 'company',),)
        ordering = ['-date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return "{} {}".format(self.company, self.company_followed)


@python_2_unicode_compatible
class Partnership(UserModel, DateModel):
    inviting_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='created_partnerships',
        verbose_name=_('invite company'),
    )
    guest_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='request_partnerships',
        verbose_name=_('request company'),
    )
    invitation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('invitation request date'),
    )
    approval_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('invitation approval date'),
    )
    refuse_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('invitation refuse date'),
    )

    class Meta:
        verbose_name = _('partnership')
        verbose_name_plural = _('partnerships')
        unique_together = (('inviting_company', 'guest_company',),)
        permissions = (
            ("list_partnership", "can list partnership"),
            ("detail_partnership", "can detail partnership"),
        )
        ordering = ['-date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return "{} {}".format(self.inviting_company, self.guest_company)


@python_2_unicode_compatible
class Sponsor(UserModel, DateModel):
    STATUS_CODES = (
        (0, _('disable')),
        (1, _('enable')),
        (2, _('requested')),
    )
    status = models.IntegerField(
        choices=STATUS_CODES,
        default=0,
        verbose_name=_('status'),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='sponsor',
        verbose_name=_('company'),
    )
    short_description = models.CharField(
        max_length=50,
        verbose_name=_('short description')
    )
    expired_date = models.DateField(
        blank=True, null=True,
        verbose_name=_('expired date')
    )
    tags = JSONField(
        default={},
        blank=True, null=True,
        verbose_name=_('tags'),
        help_text=_('Sponsor tags'),
    )

    class Meta:
        verbose_name = _('sponsor')
        verbose_name_plural = _('sponsors')
        permissions = (
            ("list_sponsor", "can list sponsor"),
            ("detail_sponsor", "can detail sponsor"),
            ("disable_sponsor", "can disable sponsor"),
        )

    def __str__(self):
        return "Sponsor: {}".format(self.company)
