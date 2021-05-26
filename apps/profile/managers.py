# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.db.models import Q


class CompanyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            status=1,
            profiles__isnull=False
        ).distinct()

    def inactive(self):
        return self.filter(
            status=0,
        )

    def get_companies(self, user):
        return self.filter(
            profiles__user=user
        )


class CompanyManager(models.Manager):
    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()

    def get_companies(self, user):
        return self.get_queryset().get_companies(user=user)


class ProfileQuerySet(models.QuerySet):
    # Todo: Review "active" function
    def exclude_mains(self):
        return self.exclude(
            role__isnull=True,
            company__isnull=True,
            position__isnull=True
        )

    def active(self):
        return self.filter(
            status=1,
            user__isnull=False,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def profile_invitation_request(self):
        return self.filter(
            status=1,
            user__isnull=False,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=True,
            invitation_refuse_date__isnull=True,
        )

    def profile_invitation_waiting(self):
        return self.filter(
            status=1,
            user__isnull=False,
            company_invitation_date__isnull=True,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def profile_invitation_approve(self):
        return self.filter(
            status=1,
            user__isnull=False,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        ).order_by('-company')

    def profile_invitation_refuse(self):
        return self.filter(
            status=1,
            user__isnull=False,
            # company_invitation_date__isnull=False,
            # profile_invitation_date__isnull=True,
            invitation_refuse_date__isnull=False,
        )

    def company_invitation_request(self):
        return self.filter(
            status=1,
            user__isnull=True,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def company_invitation_waiting(self):
        return self.filter(
            status=1,
            user__isnull=False,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=True,
            invitation_refuse_date__isnull=True,
        )

    def company_invitation_approve(self):
        return self.filter(
            status=1,
            user__isnull=False,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def company_invitation_approve_and_external(self):
        return self.filter(
            Q(
                status=1,
                # user__isnull=False,
                company_invitation_date__isnull=False,
                profile_invitation_date__isnull=False,
                invitation_refuse_date__isnull=True
            ) | Q(
                role=settings.OWNER
            ) | Q(
                role=settings.DELEGATE
            )
        )

    def company_invitation_approve_inactive(self):
        return self.filter(
            status=0,
            # user__isnull=False,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def company_invitation_refuse(self):
        return self.filter(
            status=1,
            user__isnull=False,
            # company_invitation_date__isnull=True,
            # profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=False,
        )

    def mains(self):
        return self.filter(
            user__isnull=False,
            company__isnull=True,
            role=None,
            profile_invitation_date__isnull=False,
            invitation_refuse_date__isnull=True,
        )

    def phantoms(self):
        return self.filter(
            user__isnull=True,
            company__isnull=False,
            company_invitation_date__isnull=True,
            profile_invitation_date__isnull=True,
            invitation_refuse_date__isnull=True,
        )

    def guests(self):
        return self.filter(
            # status=1,
            company__isnull=False,
            company_invitation_date__isnull=False,
            profile_invitation_date__isnull=True,
            invitation_refuse_date__isnull=True,
        )

    def anonymous(self):
        return self.filter(user__isnull=True)

    def authenticated(self):
        return self.filter(user__isnull=False)

    def owners(self):
        return self.filter(role=settings.OWNER)

    def delegates(self):
        return self.filter(role=settings.DELEGATE)

    def level_1s(self):
        return self.filter(role=settings.LEVEL_1)

    def level_2s(self):
        return self.filter(role=settings.LEVEL_2)


class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    def profile_invitation_request(self):
        return self.get_queryset().profile_invitation_request()

    def profile_invitation_waiting(self):
        return self.get_queryset().profile_invitation_waiting()

    def profile_invitation_approve(self):
        return self.get_queryset().profile_invitation_approve()

    def profile_invitation_refuse(self):
        return self.get_queryset().profile_invitation_refuse()

    def company_invitation_request(self):
        return self.get_queryset().company_invitation_request()

    def company_invitation_waiting(self):
        return self.get_queryset().company_invitation_waiting()

    def company_invitation_approve(self):
        return self.get_queryset().company_invitation_approve()

    def company_invitation_approve_and_external(self):
        return self.get_queryset().company_invitation_approve_and_external()

    def company_invitation_approve_inactive(self):
        return self.get_queryset().company_invitation_approve_inactive()

    def company_invitation_refuse(self):
        return self.get_queryset().company_invitation_refuse()

    def mains(self):
        return self.get_queryset().mains()

    def phantoms(self):
        return self.get_queryset().phantoms()

    def guests(self):
        return self.get_queryset().guests()

    def active(self):
        return self.get_queryset().active()

    def exclude_mains(self):
        return self.get_queryset().active().exclude_mains()

    def anonymous(self):
        return self.get_queryset().anonymous()

    def authenticated(self):
        return self.get_queryset().authenticated()

    def owners(self):
        return self.get_queryset().owners()

    def delegates(self):
        return self.get_queryset().delegates()

    def level_1s(self):
        return self.get_queryset().level_1s()

    def level_2s(self):
        return self.get_queryset().level_2s()


class MainProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).mains()


class PhantomProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).phantoms()


class GuestProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).guests()


class OwnerProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).owners()

    def get_company_profiles(self, company):
        """
        We are nowhere using this function. May be, we can remove
        """
        return self.get_queryset().filter(company=company)


class DelegateProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).delegates()

    def get_company_profiles(self, company):
        """
        We are nowhere using this function. May be, we can remove
        """
        return self.get_queryset().filter(company=company)


class Level1ProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).level_1s()


class Level2ProfileManager(ProfileManager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).level_2s()
