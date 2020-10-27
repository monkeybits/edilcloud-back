# chat/views.py
from django.shortcuts import render

from web.settings import BASE_DIR


def index(request):
    return render(request, BASE_DIR + '/apps/ws/templates/index.html')

def room(request, room_name):
    print(room_name)
    return render(request, BASE_DIR + '/apps/ws/templates/room.html', {
        'room_name': room_name
    })