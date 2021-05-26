# chat/views.py
from django.shortcuts import render

from web.settings import BASE_DIR


def index(request):
    return render(request, BASE_DIR + '/apps/ws/templates/index.html')

def room(request, room_name):
    print(room_name)
    if room_name == 'notify_channel':
        return render(request, BASE_DIR + '/apps/ws/templates/notify.html', {
            'room_name': room_name
        })
    if room_name == 'report_channel':
        return render(request, BASE_DIR + '/apps/ws/templates/report.html', {
            'room_name': room_name
        })
    return render(request, BASE_DIR + '/apps/ws/templates/room.html', {
        'room_name': room_name
    })