# coding: utf-8

import logging
import random

from faker import Factory

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from apps.profile import models as profile_models

logger = logging.getLogger('file')

NUM_OWNERS = 200
MAX_DOCUMENTS_PER_OWNER = 20
MAX_PHOTOS_PER_OWNER = 20
MAX_VIDEOS_PER_OWNER = 20
tags = ['Python', 'Django', 'C++', 'Ruby', 'Java', 'Go', 'dotnet', 'Scala', 'Swift', 'Julia', 'Rust']
document_models = ['company', 'project', 'bom']
photo_models = ['company', 'project', 'bom']
video_models = ['company', 'project', 'bom']


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


class FakeDocuments(FakeBase):
    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[:NUM_OWNERS]
        for owner in owners:
            for num in range(random.randint(0, MAX_DOCUMENTS_PER_OWNER)):
                try:
                    object_id = 0
                    if random.choice(document_models) == 'company':
                        content_type = ContentType.objects.get(model="company")
                        object_id = owner.company.id
                    else:
                        content_type = ContentType.objects.get(model="project")
                        if owner.company.projects.order_by('?').first():
                            object_id = owner.company.projects.order_by('?').first().id

                    if content_type and object_id != 0:
                        document = owner.create_document({
                            'title': owner.company.name + " Document " + str(num),
                            'description': owner.company.name + " Document " + str(num) + " Description",
                            'document': self.fake.file_name(category=None, extension=None),
                            'content_type': content_type,
                            'object_id': object_id,
                        })
                        logger.info('{}-{}) Owner: {} - Document: {} - Content Type: {}'.format(
                            num, self.__class__.__name__,
                            owner.id, document.id, content_type
                        ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(
                        num, self.__class__.__name__, e
                    ))


class FakePhotos(FakeBase):
    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[:NUM_OWNERS]
        for owner in owners:
            for num in range(random.randint(0, MAX_PHOTOS_PER_OWNER)):
                try:
                    object_id = 0
                    if random.choice(photo_models) == 'company':
                        content_type = ContentType.objects.get(model="company")
                        object_id = owner.company.id
                    else:
                        content_type = ContentType.objects.get(model="project")
                        if owner.company.projects.order_by('?').first():
                            object_id = owner.company.projects.order_by('?').first().id

                    if content_type and object_id != 0:
                        photo = owner.create_photo({
                            'title': owner.company.name + " Photo " + str(num),
                            'photo': self.fake.file_name(category=None, extension=None),
                            'tags': random.sample(tags, 2),
                            'content_type': content_type,
                            'object_id': object_id,
                        })
                        logger.info('{}-{}) Owner: {} - Photo: {} - Content Type: {}'.format(
                            num, self.__class__.__name__,
                            owner.id, photo.id, content_type
                        ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(
                        num, self.__class__.__name__, e
                    ))


class FakeVideos(FakeBase):
    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[:NUM_OWNERS]
        for owner in owners:
            for num in range(random.randint(0, MAX_VIDEOS_PER_OWNER)):
                try:
                    object_id = 0
                    if random.choice(video_models) == 'company':
                        content_type = ContentType.objects.get(model="company")
                        object_id = owner.company.id
                    else:
                        content_type = ContentType.objects.get(model="project")
                        if owner.company.projects.order_by('?').first():
                            object_id = owner.company.projects.order_by('?').first().id

                    if content_type and object_id != 0:
                        video = owner.create_video({
                            'title': owner.company.name + " Video " + str(num),
                            'video': self.fake.file_name(category=None, extension=None),
                            'tags': random.sample(tags, 2),
                            'content_type': content_type,
                            'object_id': object_id,
                        })
                        logger.info('{}-{}) Owner: {} - Video: {} - Content Type: {}'.format(
                            num, self.__class__.__name__,
                            owner.id, video.id, content_type
                        ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(
                        num, self.__class__.__name__, e
                    ))


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
                'Pass data (all - All classes, doc - Document'
                ', phto - Photo, vdeo - Video'
            )
        )

    def handle(self, *args, **options):

        level = getattr(logging, options.get('debug_level').upper())
        logger.setLevel(level)
        if options.get('console'):
            console_handler = logging._handlers['console']
            console_handler.setLevel(level)
            logger.handlers = []
            logger.addHandler(console_handler)

        # doc/all (Executes Document)
        if options.get('data') in ['doc', 'all']:
            fake_document = FakeDocuments()
            fake_document.generate()
        # phto/all  (Executes Photo)
        if options.get('data') in ['phto', 'all']:
            fake_photo = FakePhotos()
            fake_photo.generate()
        # vdeo/all  (Executes Video)
        if options.get('data') in ['vdeo', 'all']:
            fake_video = FakeVideos()
            fake_video.generate()
