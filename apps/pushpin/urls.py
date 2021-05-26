from django.conf.urls import url, include
from . import views
import django_eventstream

urlpatterns = [
    url('', views.home),
    url('<room_id>', views.home),
    url('rooms/<room_id>/messages/', views.messages),
    url('rooms/<room_id>/events/', include(django_eventstream.urls), {
        'format-channels': ['room-{room_id}']
    }),

    # older endpoint allowing client to select channel. not recommended
    url('/events/', include(django_eventstream.urls)),
]