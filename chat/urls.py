from django.urls import path
from chat.views import create_chat, send_message, delete_message, handle_room,show_json_chat, show_json_message
from chat.views import create_chat_flutter, handle_room_flutter, send_message_flutter, get_messages_flutter, delete_message_flutter
app_name = 'chat'

urlpatterns = [
    path('create-chat', create_chat, name='create_chat'),
    path('handle-room/<int:selected_user_id>', handle_room, name='handle_room'),
    path('send-message/<uuid:chat_id>/', send_message, name='send_message'),
    path('delete-message/<uuid:message_id>', delete_message, name='delete_message'), 
    path('json-chat/', show_json_chat, name='show_json_chat'),
    path('json-message/', show_json_message, name='show_json_message'),
    path('create-chat-flutter/', create_chat_flutter, name='create_chat_flutter'),
    path('handle-room-flutter/', handle_room_flutter, name='handle_room_flutter'),
    path('send-message-flutter/', send_message_flutter, name='send_message_flutter'),
    path('get-messages-flutter/<str:chat_id>/', get_messages_flutter, name='get_messages_flutter'),
    path('delete-message-flutter/<uuid:message_id>/', delete_message_flutter, name='delete_message_flutter'),


]