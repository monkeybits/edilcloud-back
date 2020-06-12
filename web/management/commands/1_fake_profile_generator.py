# coding: utf-8

import datetime
import logging

from faker import Factory
from random import randint, sample, choice

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.profile import models
from apps.product.models import Category


logger = logging.getLogger('file')
User = get_user_model()

NUM_USERS = 100
NUM_MAIN_PROFILES = 100
MAX_COMPANY_FOR_OWNER = 3
MAX_CATEGORY_FOR_COMPANY = 4
MAX_NEW_OWNERS = 3
MAX_NEW_DELEGATES = 2
MAX_NEW_INVITATIONS = 30
MAX_NEW_OWNER_PHANTOMS = 2
MAX_NEW_DELEGATE_PHANTOMS = 2
MAX_NEW_LEVEL_1_PHANTOMS = 10
MAX_NEW_LEVEL_2_PHANTOMS = 15
MAX_NEW_FAVOURITES = 10
MAX_NEW_PARTNERSHIPS = 30
MAX_NEW_GUESTS = 10
positions = ['Manager', 'Asst Manager', 'Asst General Manager', 'IT security', 'Senior Technician']
LANGUAGE = ['it', 'en']


class FakeBase(object):
    model = None
    how_many = 0

    def __init__(self, opts=None):
        self.opts = opts
        self.fake = Factory.create('it-IT')

    def generate(self):
        for num in range(self.how_many):
            try:
                obj = self.model.objects.create(**self.get_map())
                logger.info('{}) {}: {}'.format(num, self.model, obj.id))
            except Exception as e:
                logger.error('{}) {}: {}'.format(num, self.model, e))

    def get_map(self):
        return {}


class FakeUser(FakeBase):
    model = User
    how_many = NUM_USERS

    def generate(self):
        for num in range(self.how_many):
            try:
                username = self.fake.profile()['username']
                obj = self.model.objects.create(
                    username=username,
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    email=self.fake.profile()['mail']
                )
                obj.set_password(username)
                obj.save()
                logger.info('{}) User: {}'.format(num, obj.id))
            except Exception as e:
                logger.error('{}) User: {}'.format(num, e))


class FakeMainProfile(FakeBase):
    """
    Create Main Profiles
    """
    model = models.MainProfile
    how_many = NUM_MAIN_PROFILES

    def generate(self):
        users = User.objects.all().order_by('?')[0:NUM_USERS]
        num = None
        for num, user in enumerate(users):
            try:
                data = {
                    'first_name': self.fake.first_name(),
                    'last_name': self.fake.last_name(),
                    'language': choice(LANGUAGE),
                    'phone': self.fake.phone_number(),
                    'fax': self.fake.phone_number(),
                    'mobile': self.fake.phone_number()
                }
                profile = user.create_main_profile(data)
                logger.info('{}) MainProfile: {}'.format(num, profile.id))
            except Exception as e:
                logger.error('{}) MainProfile: {}'.format(num, e))


class FakeCompany(FakeBase):
    model = models.Company
    how_many = MAX_COMPANY_FOR_OWNER

    def generate(self):
        mains = models.MainProfile.objects.all()
        categories = Category.objects.all()
        tot_categories = categories.count()
        description = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut 
        labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut 
        aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
        eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
        mollit anim id est laborum.'''
        for profile in mains:
            # Any profile can create from 0 to MAX_COMPANY_FOR_OWNER companies
            for num in range(randint(0, self.how_many)):
                try:
                    company_categories = {}
                    for num_cat in range(randint(1, MAX_CATEGORY_FOR_COMPANY)):
                        index = randint(0, tot_categories-1)
                        company_categories[categories[index].code] = categories[index].name
                    company, owner = profile.create_company({
                        'name': self.fake.company(),
                        'slug': slugify(self.fake.company()),
                        'description': description,
                        'ssn': self.fake.ssn(),
                        'url': self.fake.url(),
                        'email': self.fake.company_email(),
                        'phone': self.fake.phone_number(),
                        'fax': self.fake.phone_number(),
                        'category': company_categories
                    })
                    logger.info('{}) Company: {} {}'.format(num, company.id, owner.id))
                except Exception as e:
                    logger.error('{}) Company: {}'.format(num, e))
                    continue


class FakeOwner(object):
    """
    Create Owner Profiles w/o send invitation
    """
    how_many = MAX_NEW_OWNERS

    def generate(self):
        mains = models.MainProfile.objects.all()
        owners = models.OwnerProfile.objects.all()
        num_pr = mains.count()

        for first_owner in owners:
            for num in range(randint(1, self.how_many)):
                try:
                    profile = mains[randint(0, num_pr - 1)]
                    new_owner = profile.clone()
                    new_owner.position = choice(positions)
                    new_owner.role = settings.OWNER
                    new_owner.company = first_owner.company
                    new_owner.company_invitation_date = datetime.datetime.now()
                    new_owner.profile_invitation_date = datetime.datetime.now()
                    new_owner.invitation_refuse_date = None
                    new_owner.save()
                    logger.info('{}) Owner: {}'.format(num, new_owner.id))
                except Exception as e:
                    logger.error('{}) Owner: {}'.format(num, e))


class FakeDelegate(object):
    """
    Create Delegate Profiles with accepted invitation
    """
    how_many = MAX_NEW_DELEGATES

    def generate(self):
        mains = models.MainProfile.objects.all()
        owners = models.OwnerProfile.objects.all()
        num_pr = mains.count()

        for first_owner in owners:
            for num in range(randint(1, self.how_many)):
                try:
                    profile = mains[randint(0, num_pr - 1)]
                    new_delegate = profile.clone()
                    new_delegate.position = choice(positions)
                    new_delegate.role = settings.DELEGATE
                    new_delegate.company = first_owner.company
                    new_delegate.company_invitation_date = datetime.datetime.now()
                    new_delegate.profile_invitation_date = datetime.datetime.now()
                    new_delegate.invitation_refuse_date = None
                    new_delegate.save()
                    logger.info('{}) Delegate: {}'.format(num, new_delegate.id))
                except Exception as e:
                    logger.error('{}) Delegate: {}'.format(num, e))


class FakeLevel1(object):
    """
    Create Level 1 Profiles with accepted invitation
    """
    how_many = MAX_NEW_INVITATIONS

    def generate(self):
        mains = models.MainProfile.objects.all()
        owners = models.OwnerProfile.objects.all()
        num_pr = mains.count()

        for first_owner in owners:
            for num in range(randint(1, self.how_many)):
                try:
                    profile = mains[randint(0, num_pr - 1)]
                    new_level_1 = profile.clone()
                    new_level_1.position = choice(positions)
                    new_level_1.role = settings.LEVEL_1
                    new_level_1.company = first_owner.company
                    new_level_1.company_invitation_date = datetime.datetime.now()
                    new_level_1.profile_invitation_date = datetime.datetime.now()
                    new_level_1.invitation_refuse_date = None
                    new_level_1.save()
                    logger.info('{}) Level 1: {}'.format(num, new_level_1.id))
                except Exception as e:
                    logger.error('{}) Level 1: {}'.format(num, e))


class FakeLevel2(object):
    """
    Create Level 2 Profiles with accepted invitation
    """
    how_many = MAX_NEW_INVITATIONS

    def generate(self):
        mains = models.MainProfile.objects.all()
        owners = models.OwnerProfile.objects.all()
        num_pr = mains.count()

        for first_owner in owners:
            for num in range(randint(1, self.how_many)):
                try:
                    profile = mains[randint(0, num_pr - 1)]
                    new_level_2 = profile.clone()
                    new_level_2.position = choice(positions)
                    new_level_2.role = settings.LEVEL_2
                    new_level_2.company = first_owner.company
                    new_level_2.company_invitation_date = datetime.datetime.now()
                    new_level_2.profile_invitation_date = datetime.datetime.now()
                    new_level_2.invitation_refuse_date = None
                    new_level_2.save()
                    logger.info('{}) Level 2: {}'.format(num, new_level_2.id))
                except Exception as e:
                    logger.error('{}) Level 2: {}'.format(num, e))


class FakePhantom(FakeBase):
    def generate(self):
        mains = models.MainProfile.objects.all()
        owners = models.OwnerProfile.objects.all()
        num_pr = mains.count()

        how_many_dict = {
            settings.OWNER: MAX_NEW_OWNER_PHANTOMS,
            settings.DELEGATE: MAX_NEW_DELEGATE_PHANTOMS,
            settings.LEVEL_1: MAX_NEW_LEVEL_1_PHANTOMS,
            settings.LEVEL_2: MAX_NEW_LEVEL_2_PHANTOMS
        }
        for first_owner in owners:
            for role, numbers in how_many_dict.items():
                for num in range(randint(1, numbers)):
                    try:
                        profile = mains[randint(0, num_pr - 1)]
                        phantom = profile.clone()
                        phantom.position = choice(positions)
                        phantom.user = None
                        phantom.role = role
                        phantom.company = first_owner.company
                        phantom.company_invitation_date = datetime.datetime.now()
                        phantom.profile_invitation_date = datetime.datetime.now()
                        phantom.invitation_refuse_date = None
                        phantom.save()
                        logger.info('{}) Phantom: {}'.format(num, phantom.id))
                    except Exception as e:
                        logger.error('{}) Phantom: {}'.format(num, e))


class FakeGuest(FakeBase):
    how_many = MAX_NEW_GUESTS

    def generate(self):
        mains = models.MainProfile.objects.all()
        owners = models.OwnerProfile.objects.authenticated()
        num_pr = mains.count()
        roles = settings.PROFILE_PROFILE_ROLE_CHOICES

        for first_owner in owners:
            for num in range(randint(1, self.how_many)):
                try:
                    profile = mains[randint(0, num_pr - 1)]
                    guest = profile.clone()
                    guest.position = choice(positions)
                    guest.role = sample(roles, 1)[0][0]
                    guest.company = first_owner.company
                    guest.company_invitation_date = datetime.datetime.now()
                    guest.profile_invitation_date = None
                    guest.invitation_refuse_date = None
                    guest.save()
                    logger.info('{}) Guest: {}'.format(num, guest.id))
                except Exception as e:
                    logger.error('{}) Guest: {}'.format(num, e))


class FakeFavourite(FakeBase):
    how_many = MAX_NEW_FAVOURITES

    def generate(self):
        mains = models.MainProfile.objects.all()
        companies = models.Company.objects.all()
        num_companies = companies.count()

        for main in mains:
            for num in range(randint(0, self.how_many)):
                try:
                    company = companies[randint(0, num_companies)]
                    favourite = main.follow_company(company)
                    logger.info('{}) Favourite: {}'.format(num, favourite.id))
                except Exception as e:
                    logger.error('{}) Favourite: {}'.format(num, e))


class FakePartnership(FakeBase):
    how_many = MAX_NEW_PARTNERSHIPS

    def generate(self):
        owners = models.OwnerProfile.objects.authenticated()
        companies = models.Company.objects.all()
        num_companies = companies.count()

        for owner in owners:
            for num in range(randint(0, self.how_many)):
                try:
                    company = companies[randint(0, num_companies)]
                    partnership = owner.create_partnership(company)
                    logger.info('{}) Partnership: {}'.format(num, partnership.id))
                except Exception as e:
                    logger.error('{}) Partnership: {}'.format(num, e))


class Command(BaseCommand):
    """
    Set Products and so on
    """

    def add_arguments(self, parser):
        # -c enables logging using store_true
        parser.add_argument(
            '-c', '--console', action='store_true', default=False,
            help='Debug - write logging to console'
        )
        # -q changes opt --verbose setting to const
        parser.add_argument(
            "-q", "--quiet",
            action="store_const", const=0, dest="verbose"
        )
        # log level
        parser.add_argument(
            '-l', '--debug-level', default='error',
            help='Set debug level (debug, info, warnings) for console',
        )
        # pass data
        parser.add_argument(
            '-d', '--data', default='all',
            help=(
                'Pass data (all - All classes, usr - User'
                ', mnpf - Main Profile, cmpy - Company'
                ', o - Owner, del - Delegate'
                ', lvl1 - Level1, lvl2 - Level2'
                ', phantom - Phantom, guest - Guest'
                ', fav - Favourite, ptp - Partnership)'
            )
        )

    def handle(self, *args, **options):

        level = getattr(logging,  options.get('debug_level').upper())
        logger.setLevel(level)
        if options.get('console'):
            console_handler = logging._handlers['console']
            console_handler.setLevel(level)
            logger.handlers = []
            logger.addHandler(console_handler)

        # usr/all (Executes User)
        if options.get('data') in ['usr', 'all']:
            fake_user = FakeUser()
            fake_user.generate()
        # mnpf/all  (Executes Main Profile)
        if options.get('data') in ['mnpf', 'all']:
            fake_main_profile = FakeMainProfile()
            fake_main_profile.generate()
        # cmpy/all  (Executes Company)
        if options.get('data') in ['cmpy', 'all']:
            fake_company = FakeCompany()
            fake_company.generate()
        # o/all  (Executes Owner - Creates a new company profile)
        if options.get('data') in ['o', 'all']:
            fake_owner = FakeOwner()
            fake_owner.generate()
        # del/all  (Executes Delegate - Creates a new company profile)
        if options.get('data') in ['del', 'all']:
            fake_delegate = FakeDelegate()
            fake_delegate.generate()
        # lvl1/all  (Executes Level1 - Creates a new company profile)
        if options.get('data') in ['lvl1', 'all']:
            fake_level1 = FakeLevel1()
            fake_level1.generate()
        # lvl2/all  (Executes Level2 - Creates a new company profile)
        if options.get('data') in ['lvl2', 'all']:
            fake_level2 = FakeLevel2()
            fake_level2.generate()
        # phantom/all  (Executes Phantom - Creates a new company profile)
        if options.get('data') in ['phantom', 'all']:
            fake_phantom = FakePhantom()
            fake_phantom.generate()
        # guest/all  (Executes Guest)
        # if options.get('data') in ['guest', 'all']:
        #     fake_guest = FakeGuest()
        #     fake_guest.generate()
        # fav/all  (Executes Favourite)
        if options.get('data') in ['fav', 'all']:
            fake_favourite = FakeFavourite()
            fake_favourite.generate()
        # ptp/all  (Executes Partnership)
        if options.get('data') in ['ptp', 'all']:
            fake_partnership = FakePartnership()
            fake_partnership.generate()
