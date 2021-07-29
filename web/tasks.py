from __future__ import absolute_import, unicode_literals

import datetime
import os

from asgiref.sync import async_to_sync
from celery import task
from channels.layers import get_channel_layer
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.project.models import Project
from web import settings
from web.settings import MEDIA_ROOT, PROJECT_PATH, BASE_DIR, STATIC_ROOT, DEFAULT_FROM_EMAIL, API_SEJDA_PDF_GENERATOR, \
    NEW_ENTRY_SENDER, GSPREAD_USERS_URL
#from weasyprint import HTML, CSS, default_url_fetcher
import requests

def event_triger(msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'report_report_channel',
        {
            'type': 'report_message',
            'message': msg
        }
    )

@task()
def archived_projects_reminder():
    print('archived_projects_reminder')
    # projects = Project.objects.filter(status=0)
    # print(projects)
    # for project in projects:
    #     delta = datetime.datetime.now() - project.date_last_modify
    #     print('delta is: ' + str(delta.days))
    #     if delta.days == 0 or delta.days == 1:
    #         project.send_reminder_email(remaining_days=30)
    #     if delta.days == 10:
    #         project.send_reminder_email(remaining_days=20)
    #     if delta.days == 20:
    #         project.send_reminder_email(remaining_days=10)
    #     if delta.days == 25:
    #         project.send_reminder_email(remaining_days=5)
    #     if delta.days == 28:
    #         project.send_reminder_email(remaining_days=2)
    #     if delta.days == 29:
    #         project.send_reminder_email(remaining_days=1)
    #     if delta.days == 30:
    #         project.send_reminder_email(remaining_days=0)
    #     if delta.days > 30:
    #         project.delete()

@task()
def generate_pdf_report(html_message, data, domain_url):
    url = 'https://api.sejda.com/v2/html-pdf'
    r = requests.post(url, json={
        'htmlCode': html_message,
        'viewportWidth': 1200,
        'pageSize': 'A4',
        'pageOrientation': 'portrait'
    }, headers={
        'Authorization': 'Token: {}'.format(API_SEJDA_PDF_GENERATOR)
    })
    url_report = '/media/reports/' + 'Report progetto {}.pdf'.format(data['project_name'])
    f = open(BASE_DIR + url_report, 'wb')
    f.write(r.content)
    f.close()

    event_triger(
        {
            'message': {
                "url": domain_url + url_report,
                "name": "Report progetto {}".format(data['project_name']),
                "extension": ".pdf",
                "dest": {
                    "id": data['pk']
                },
            }
        }
    )
    # from django.core.mail import EmailMultiAlternatives
    # data_template = {
    #     'profile_name': "{} {}".format(data['first_name'], data['last_name']),
    #     'project_name': data['project_name'],
    # }
    # report_template = render_to_string('email/report_email.html', data_template)
    # email = EmailMultiAlternatives(
    #     subject='Edilcloud.io Report PDF - Progetto {}'.format(data['project_name']),
    #     body='ciao questo è un report',
    #     to=[data['email']],
    #     from_email=DEFAULT_FROM_EMAIL,
    # )
    # email.attach_alternative(report_template, "text/html")
    # email.attach(filename='Report progetto {}.pdf'.format(data['project_name']), content=r.content)
    # email.send()


@task()
def update_gspread_users(data):
    email = data['email']
    full_name = data['full_name']
    role = data['role']
    new_data = [email, full_name, role]

    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    gc = gspread.service_account(filename='edilcloud_api.json')
    gsheet = gc.open_by_url(GSPREAD_USERS_URL)
    mydata = gsheet.sheet1.get_all_records()
    print(mydata)
    wsheet = gsheet.worksheet("Foglio1")
    wsheet.append_row(new_data)

    send_mail(
        subject="Nuovo utente aggiunto a Google Sheets",
        message="Buongiorno,\n un nuovo utente si è registrato. E' stato aggiunto al google sheets.\n\n Altrimenti accedi a questo link:\n {}".format(GSPREAD_USERS_URL),
        recipient_list=NEW_ENTRY_SENDER,
        from_email=DEFAULT_FROM_EMAIL
    )