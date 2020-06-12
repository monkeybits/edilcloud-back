# coding: utf-8

import datetime
import logging
import random
from datetime import timedelta
from random import choice
from string import ascii_lowercase
from random import randrange

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.profile import models as profile_models

logger = logging.getLogger('file')
User = get_user_model()

NUM_COMPANIES = 100
NUM_OWNERS = 100
MAX_PROJECT_X_OWNERS = 20
MAX_SHARED_PROJECTS = 20
MAX_TASKS_X_PROJECT = 20
MAX_PROJECTS = 200

NUM_PROJECTS = 20
NUM_TASKS = 20
NUM_INTERNAL_PROJECTS = 20
NUM_SHARED_PROJECTS = 20
NUM_PROJECT_TASKS = 20
NUM_PROJECT_SHARE = 20
NUM_PROJECT_TEAMS = 100
NUM_PROJECT_ACTIVITIES = 40
tags = ['Python', 'Django', 'C++', 'Ruby', 'Java', 'Go', 'dotnet', 'Scala', 'Swift', 'Julia', 'Rust']
ACTIVITY_STATUS = ['to-do', 'progress', 'completed']


def get_random_string():
    return ''.join(choice(ascii_lowercase) for i in range(12))


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


class FakeProject(object):
    how_many = NUM_PROJECTS

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]

        for owner in owners:
            for num in range(1, MAX_PROJECT_X_OWNERS):
                try:
                    project = owner.create_project({
                        'name': "Project " + "_" + get_random_string(),
                        'description': "Project " + "_" + get_random_string(),
                        'referent': owner,
                        'date_start': datetime.datetime.now(),
                        'date_end': datetime.datetime.now() + timedelta(days=120),
                        'tags': random.sample(tags, 2),
                    })
                    logger.info('{}-{}) Project: {}'.format(
                        num, self.__class__.__name__,
                        project.id
                    ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(
                        num, self.__class__.__name__, e
                    ))


# class FakeInternalProject(object):
#     how_many = NUM_INTERNAL_PROJECTS
#
#     def generate(self):
#         owners = profile_models.OwnerProfile.objects.all()[0:NUM_OWNERS]
#
#         for owner in owners:
#             for num in range(random.randint(1, MAX_PROJECT_X_OWNERS)):
#                 try:
#                     project = owner.create_project({
#                         'typology': settings.PROJECT_PROJECT_INTERNAL,
#                         'name': "Internal Project " + str(num) + "_" + owner.company.name,
#                         'description': owner.company.name + " Internal Project " + str(num) + " Description",
#                         'date_start': datetime.datetime.now(),
#                         'date_end': datetime.datetime.now() + timedelta(days=30),
#                         'tags': random.sample(tags, 2),
#                     })
#                     logger.info('{}-{}) Project: {}'.format(
#                         num, self.__class__.__name__,
#                         project.id
#                     ))
#                 except Exception as e:
#                     logger.error('{}-{}) {}'.format(
#                         num, self.__class__.__name__, e
#                     ))
#
#
# class FakeSharedProject(object):
#     how_many = NUM_SHARED_PROJECTS
#
#     def generate(self):
#         owners = profile_models.OwnerProfile.objects.all()[0:NUM_OWNERS]
#
#         for owner in owners:
#             for num in range(random.randint(1, MAX_PROJECT_X_OWNERS)):
#                 try:
#                     project = owner.create_project({
#                         'typology': settings.PROJECT_PROJECT_SHARED,
#                         'name': "Shared Project " + str(num) + "_" + owner.company.name,
#                         'description': owner.company.name + " Shared Project " + str(num) + " Description",
#                         'date_start': datetime.datetime.now(),
#                         'date_end': datetime.datetime.now() + timedelta(days=30),
#                         'tags': random.sample(tags, 2),
#                     })
#                     logger.info('{}-{}) Project: {}'.format(
#                         num, self.__class__.__name__,
#                         project.id
#                     ))
#                 except Exception as e:
#                     logger.error('{}-{}) {}'.format(
#                         num, self.__class__.__name__, e
#                     ))


class FakeProjectInternalTask(object):
    how_many = NUM_PROJECT_TASKS
    # return active random companies
    companies = profile_models.Company.objects.active().order_by('?')[:NUM_COMPANIES]

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]

        for owner in owners:
            projects = owner.company.projects.all().order_by('?')[0:MAX_PROJECTS]
            for project in projects:
                for num in range(1, MAX_TASKS_X_PROJECT):
                    try:
                        date_start = random_date(project.date_start, project.date_end)
                        date_end = random_date(project.date_start, project.date_end)
                        task = owner.create_task({
                            'name': "Task " + str(num),
                            'project': project,
                            'date_start': date_end if date_start >= date_end else date_start,
                            'date_end': date_start if date_start >= date_end else date_end,
                            'assigned_company': project.company,
                        })
                        logger.info('{}-{}) Project: {} - InternalTask: {}'.format(
                            num, self.__class__.__name__,
                            project.id, task.id
                        ))
                    except Exception as e:
                        logger.error('{}-{}) {}'.format(num, self.__class__.__name__, e))


class FakeProjectSharedTask(object):
    how_many = NUM_PROJECT_TASKS
    # return active random companies
    companies = profile_models.Company.objects.active().order_by('?')[:NUM_COMPANIES]

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]

        for owner in owners:
            projects = owner.company.projects.all().order_by('?')[0:MAX_PROJECTS]
            for project in projects:
                current_company_id = [project.company.id]
                all_company_ids = self.companies.values_list('id', flat=True)
                assigned_company_id = set(current_company_id).symmetric_difference(all_company_ids)

                for num in range(random.randint(1, MAX_TASKS_X_PROJECT)):
                    try:
                        assigned_company = profile_models.Company.objects.get(pk=random.choice(tuple(assigned_company_id)))
                        date_start = random_date(project.date_start, project.date_end)
                        date_end = random_date(project.date_start, project.date_end)
                        task = owner.create_task({
                            'name': "Task " + str(num),
                            'project': project,
                            'date_start': date_end if date_start >= date_end else date_start,
                            'date_end': date_start if date_start >= date_end else date_end,
                            'assigned_company': assigned_company,
                        })
                        logger.info('{}-{}) Project: {} - SharedTask: {}'.format(
                            num, self.__class__.__name__,
                            project.id, task.id
                        ))
                    except Exception as e:
                        logger.error('{}-{}) {}'.format(num, self.__class__.__name__, e))


class FakeProjectTaskShare(object):
    how_many = NUM_PROJECT_SHARE

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]
        for owner in owners:
            projects = owner.company.projects.all().order_by('?')[0:MAX_PROJECTS]
            for num, project in enumerate(projects):
                try:
                    for task in project.tasks.exclude(assigned_company=project.company):
                        # Share the project task
                        owner.share_task(task)
                        logger.info('{}-{}) ProjectTaskShare: {}'.format(
                            num, self.__class__.__name__,
                            task.id
                        ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(num, self.__class__.__name__, e))


class FakeProjectTeam(object):
    how_many = NUM_PROJECT_TEAMS

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]
        for owner in owners:
            company_profile_ids = owner.company.profiles.active().values_list('id', flat=True)
            for project in owner.company.projects.all().order_by('?')[0:NUM_PROJECTS]:
                project_profile_ids = project.profiles.all().values_list('id', flat=True)
                profile_id = set(company_profile_ids).symmetric_difference(project_profile_ids)
                for num in range(1, self.how_many):
                    try:
                        if profile_id:
                            profile =  owner.get_profile(random.choice(tuple(profile_id)))
                            team = owner.create_member({
                                'project': project,
                                'profile': profile,
                                'role': 'w',
                            })
                            logger.info('{}-{}) Project: {} - Team: {}'.format(
                                num, self.__class__.__name__,
                                project.id, team.id if team else None
                            ))
                    except Exception as e:
                        logger.error('{}-{}) {}'.format(num, self.__class__.__name__, e))


class FakeProjectActivity(object):
    how_many = NUM_PROJECT_ACTIVITIES

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]
        for owner in owners:
            for project in owner.company.projects.all().order_by('?')[0:NUM_PROJECTS]:
                for task in project.tasks.filter(assigned_company=project.company)[0:NUM_TASKS]:
                    project_profile_ids = project.profiles.all().values_list('id', flat=True)
                    for num in range(1, self.how_many):
                        try:
                            if project_profile_ids:
                                datetime_start = random_date(task.date_start, task.date_end)
                                datetime_end = random_date(task.date_start, task.date_end)
                                profile = owner.get_profile(random.choice(project_profile_ids))
                                activity = owner.create_task_activity({
                                    'task': task,
                                    'profile': profile,
                                    'title': "Activity "+ str(num),
                                    'description': task.name + " description",
                                    'status': random.choice(ACTIVITY_STATUS),
                                    'datetime_start': datetime_end if datetime_start >= datetime_end else datetime_start,
                                    'datetime_end': datetime_start if datetime_start >= datetime_end else datetime_end,
                                })
                                logger.info('{}-{}) Project: {} - Activity: {}'.format(
                                    num, self.__class__.__name__,
                                    project.id, activity.id if activity else None
                                ))
                        except Exception as e:
                            logger.error('{}-{}) {}'.format(num, self.__class__.__name__, e))


class FakeProjectTaskProgress(object):
    # return active random companies
    companies = profile_models.Company.objects.active().order_by('?')[:NUM_COMPANIES]

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all().order_by('?')[0:NUM_OWNERS]

        for owner in owners:
            projects = owner.company.projects.all().order_by('?')[0:MAX_PROJECTS]
            for project in projects:
                for task in project.tasks.all():
                    try:
                        task = owner.edit_task({
                            'project': project,
                            'id': task.id,
                            'progress': random.randint(2, 100)
                        })
                        logger.info('{}) Project: {} - Task: {}'.format(
                            self.__class__.__name__,
                            project.id, task.id
                        ))
                    except Exception as e:
                        logger.error('{}) {}'.format(self.__class__.__name__, e))


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
                'Pass data (all - All classes, pj - Project'
                ', ptsk - ProjectTask'
                ', ps - ProjectShare, ptm - ProjectTeam'
                ', pact - ProjectActivity)'
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

        # ip/all (Executes InternalProject)
        # if options.get('data') in ['ip', 'all']:
        #     fake_internal_project = FakeInternalProject()
        #     fake_internal_project.generate()
        # sp/all  (Executes SharedProject)
        # if options.get('data') in ['sp', 'all']:
        #     fake_shared_project = FakeSharedProject()
        #     fake_shared_project.generate()
        # pj/all (Executes Project)
        if options.get('data') in ['pj', 'all']:
            fake_project = FakeProject()
            fake_project.generate()
        # pitsk/all  (Executes ProjectInternalTask)
        if options.get('data') in ['pitsk', 'all']:
            fake_project_internal_task = FakeProjectInternalTask()
            fake_project_internal_task.generate()
        # pstsk/all  (Executes ProjectSharedTask)
        if options.get('data') in ['pstsk', 'all']:
            fake_project_shared_task = FakeProjectSharedTask()
            fake_project_shared_task.generate()
        # ps/all  (Executes ProjectShare)
        if options.get('data') in ['ps', 'all']:
            fake_project_task_share = FakeProjectTaskShare()
            fake_project_task_share.generate()
        # ptm/all  (Executes ProjectTeam)
        if options.get('data') in ['ptm', 'all']:
            fake_project_team = FakeProjectTeam()
            fake_project_team.generate()
        # pact/all  (Executes ProjectActivity)
        if options.get('data') in ['pact', 'all']:
            fake_project_activity = FakeProjectActivity()
            fake_project_activity.generate()
        # ptsk_prog/all  (Executes FakeProjectTaskProgress)
        if options.get('data') in ['ptsk_prog', 'all']:
            fake_project_task_progress = FakeProjectTaskProgress()
            fake_project_task_progress.generate()
