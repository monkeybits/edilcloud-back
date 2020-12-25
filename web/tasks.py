from __future__ import absolute_import, unicode_literals

import datetime
import os

from celery import task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.project.models import Project
from web import settings
from web.settings import MEDIA_ROOT, PROJECT_PATH, BASE_DIR, STATIC_ROOT
#from weasyprint import HTML, CSS, default_url_fetcher

@task()
def archived_projects_reminder():
    print('archived_projects_reminder')
    projects = Project.objects.filter(status=0)
    print(projects)
    for project in projects:
        delta = datetime.datetime.now() - project.date_last_modify
        print('delta is: ' + str(delta.days))
        if delta.days == 0 or delta.days == 1:
            project.send_reminder_email(remaining_days=30)
        if delta.days == 10:
            project.send_reminder_email(remaining_days=20)
        if delta.days == 20:
            project.send_reminder_email(remaining_days=10)
        if delta.days == 25:
            project.send_reminder_email(remaining_days=5)
        if delta.days == 28:
            project.send_reminder_email(remaining_days=2)
        if delta.days == 29:
            project.send_reminder_email(remaining_days=1)
        if delta.days == 30:
            project.send_reminder_email(remaining_days=0)
        if delta.days > 30:
            project.delete()

# @task()
# def generate_pdf_report(html_message, pdf_name, request_path):
#     print(pdf_name)
#     html = HTML(string=html_message, base_url=request_path)
#     html.write_pdf(
#         'Project_report_1.pdf', presentational_hints=True, stylesheets=[
#             CSS(STATIC_ROOT + '/css/typography.css'),
#             CSS(STATIC_ROOT + '/css/bootstrap.min.css'),
#             CSS(STATIC_ROOT + '/css/style.css'),
#             CSS(STATIC_ROOT + '/css/responsive.css'),
#         ])