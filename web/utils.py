import os
import configparser

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
