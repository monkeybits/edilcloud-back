from crontab import CronTab
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

from django.conf import settings

my_cron = CronTab(user=settings.WHISTLE_CRONTAB_USERNAME)
for job in my_cron:
    if job.comment == 'whistle_send_email':
        my_cron.remove(job)
        my_cron.write()

job = my_cron.new(command='cd /home/vamsi/Projects/src/office2017.whistle.it/ && cd . && /home/vamsi/Projects/src/office2017.whistle.it/venv/bin/dj send_email', comment="whistle_send_email")
job.minute.every(1)
my_cron.write()
