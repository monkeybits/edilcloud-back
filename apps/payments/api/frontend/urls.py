from django.urls import path
from .views.tracker_views import stripe_config, create_checkout_session, home, create_sub, complete, customer_portal, \
    my_webhook_view

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    path('', home, name='subscriptions-home'),
    path('config/', stripe_config),  # new
    path("charge/complete/", complete, name="complete"),  # add
    path("create-sub", create_sub, name="create sub"),  # add
    path('create-checkout-session/', create_checkout_session),  # new
    path('customer-portal/', customer_portal),  # new
    path('webhook-event/', my_webhook_view),  # new
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
