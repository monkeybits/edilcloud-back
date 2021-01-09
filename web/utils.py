import os
import configparser

import emoji
import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException

from web.drf import exceptions as django_api_exception

config = configparser.ConfigParser()
config.read(os.path.join(settings.PROJECT_PATH, 'messages.ini'))

def get_media_size(current_profile, validated_data):
    total_size = 0

    # existing files
    all_company_photo = current_profile.list_photos()
    for photo in all_company_photo:
        total_size += photo.photo.size
    all_company_video = current_profile.list_videos()
    for video in all_company_video:
        total_size += video.video.size
    all_company_document = current_profile.list_documents()
    for document in all_company_document:
        total_size += document.document.size

    # new file
    if 'photo' in validated_data:
        total_size += validated_data['photo'].size
    if 'video' in validated_data:
        total_size += validated_data['video'].size
    if 'document' in validated_data:
        total_size += validated_data['document'].size

    return round(total_size/float(1<<17), 2)

def info_plan(customer):
    customer = stripe.Customer.retrieve(customer)
    product_id = customer.subscriptions.data[0].plan.product
    product = stripe.Product.retrieve(product_id)
    return product

def permissions_plan(customer):
    permissions = {}
    plan = info_plan(customer)
    enable_gantt = plan.metadata.ENABLE_GANTT
    report_type = plan.metadata.REPORT_TYPE
    max_profiles = plan.metadata.MAX_PROFILES
    max_projects = plan.metadata.MAX_PROJECTS
    max_size = plan.metadata.MAX_SIZE
    permissions.update({'report_type': report_type})
    permissions.update({'max_profiles': max_profiles})
    permissions.update({'max_projects': max_projects})
    permissions.update({'max_size': max_size})
    if enable_gantt == 'True':
        permissions.update({'enable_gantt': True})
    else:
        permissions.update({'enable_gantt': False})

    return permissions

def check_limitation_plan(customer, rule, total_count):
    detail_error = "Il limite massimo è stato raggiunto, fai upgrade del tuo piano."
    customer = stripe.Customer.retrieve(customer)
    product_id = customer.subscriptions.data[0].plan.product
    product = stripe.Product.retrieve(product_id)
    if rule == 'profile':
        limit = int(product.metadata.MAX_PROFILES)
        detail_error = "Il limite massimo di personale è stato raggiunto, fai upgrade del tuo piano."
    elif rule == 'project':
        limit = int(product.metadata.MAX_PROJECTS)
        detail_error = "Il limite massimo di progetti è stato raggiunto, fai upgrade del tuo piano."
    elif rule == 'size':
        limit = int(product.metadata.MAX_SIZE) # in MegaByte
        detail_error = "Il limite massimo di file manager è stato raggiunto, fai upgrade del tuo piano."
    else:
        limit = 0
    if total_count < limit:
        return True
    else:
        raise APIException(code=status.HTTP_403_FORBIDDEN,
                           detail=detail_error
                           )

def build_array_message(emot, sentences):
    full_sentence = ""
    full_emoji = ""
    # if emot is not None:
    #     full_emoji = emoji.emojize(':{}:'.format(emot)) + " "
    if emot is None:
        full_emoji = ''
    else:
        full_emoji = emot
    for sentence in sentences:
        full_sentence += str(sentence) + " "
    return full_emoji + full_sentence