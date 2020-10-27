# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# import apps.ws.routing

# application = ProtocolTypeRouter({
#     # (http->django views is added by default)
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             apps.ws.routing.websocket_urlpatterns
#         )
#     ),
# })
from channels.routing import route
from apps.ws.consumers import connect, disconnect, receive, chat_message

channel_routing = [
    route("websocket.connect", connect),
    route("websocket.receive", receive),
    route("websocket.disconnect", disconnect),
    route("chat-messages", chat_message),
]