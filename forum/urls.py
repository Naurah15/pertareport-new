from django.urls import path
from forum.views import create_forum_entry, show_main, add_comment, delete_forum
from forum.views import add_comment_flutter, create_forum_entry, show_main, add_comment, delete_forum, show_json_forum, delete_forum_flutter, create_forum_flutter, show_json_comment_forum

app_name = 'forum'

urlpatterns = [
    path('show-main', show_main, name='show_main'),
    path('show-main', show_main, name='show_main'),
    path('create-forum-entry/', create_forum_entry, name='create_forum_entry'),
    path('add-comment/<uuid:forum_entry_id>/', add_comment, name='add_comment'),
    path('delete/<uuid:id>', delete_forum, name='delete_forum'),
    path('add-comment/<uuid:forum_entry_id>/', add_comment, name='add_comment'),
    path('delete/<uuid:id>', delete_forum, name='delete_forum'),
    path('get-forum-entries/', show_json_forum, name='get_forum_entries'),
    path('delete-forum-flutter/<uuid:forum_id>/', delete_forum_flutter, name='delete_forum_flutter'),
    path('create-forum-flutter/', create_forum_flutter, name='create_forum_flutter'),
    path('add_comment_flutter/<uuid:forum_id>/', add_comment_flutter, name='add_comment_flutter'),
    path('show-json-comment/<uuid:forum_id>/', show_json_comment_forum, name='show_json_comment')
]