# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import signal
import sys
import datetime

from django.core.management.base import BaseCommand

from apps.notify import models as notify_models


class Command(BaseCommand):
    _tempdir = '/tmp'
    _lock_time = 1000
    _script = os.path.basename(__file__).split('.')[0]

    def add_arguments(self, parser):
        # email limit per process
        parser.add_argument('-l', '--limit', dest='limit', default=100,
                    help='Limit Messages'),

        # it doesn't send emails
        parser.add_argument('-d', '--dry-run', dest='dry_run', default=False,
                    help="Send step is bypassed"),

    def get_lock_file(self):
        return os.path.join(self._tempdir, self._script + '.lock')

    def lock(self):
        open(self.get_lock_file(), 'w').close()

    def unlock(self):
        os.unlink(self.get_lock_file())

    def _cleanup_lock(self):
        if os.path.exists(self.get_lock_file()):
            created = datetime.datetime.fromtimestamp(
                os.path.getctime(self.get_lock_file()))
            seconds = (datetime.datetime.now() - created).seconds
            if seconds > self._lock_time:
                self.unlock()

    def is_run(self):
        self._cleanup_lock()
        return os.path.exists(self.get_lock_file())

    def check_is_running(self):
        if self.is_run():
            sys.stdout.write('Already running\n')
            sys.exit(-1)

    def signal_handler(self, signal, frame):
        self.unlock()

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        limit = int(options.get('limit'))

        self.check_is_running()
        self.lock()
        try:
            notify_recipients = notify_models.NotificationRecipient.objects.filter(
                    is_email=True, is_email_sent=False
                ).order_by('-id')[:limit]
            for notify_recipient in notify_recipients:
                if not dry_run:
                    notify_recipient.send_notify_email()
        except Exception as e:
            print(e)
        finally:
            self.unlock()


handler = Command()
signal.signal(signal.SIGINT, handler.signal_handler)
