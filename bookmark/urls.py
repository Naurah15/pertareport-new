from django.urls import path
from bookmark.views import remove_bookmark, bookmarked_products, add_bookmark, add_bookmark_flutter, remove_bookmark_flutter, bookmarked_products_flutter

app_name = 'bookmark'

urlpatterns = [
    path('bookmark/remove/<int:product_id>/', remove_bookmark, name='remove_bookmark'),
    path('bookmark/add/<int:product_id>/', add_bookmark, name='add_bookmark'),
    path('bookmarked-products/', bookmarked_products, name='bookmarked_products'),
    path('add_flutter/<int:product_id>/', add_bookmark_flutter, name='add_bookmark_flutter'),
    path('remove_flutter/<int:product_id>/', remove_bookmark_flutter, name='remove_bookmark_flutter'),
    path('bookmarked-products_flutter/', bookmarked_products_flutter, name='bookmarked_products_flutter'),
]