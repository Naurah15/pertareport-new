from django.urls import path
from review.views import delete_review, delete_review_json, show_review, add_review, get_product_reviews_json, add_review_json

app_name = 'review'
urlpatterns = [
    path('product/<int:pk>/', show_review, name='show_review'),
    path('product/<int:pk>/add/', add_review, name='add_review'),
    path('product/<int:pk>/delete/', delete_review, name='delete_review'),



    path('api/product/<int:pk>/reviews/', get_product_reviews_json, name='get_product_reviews_json'),
    path('api/product/<int:pk>/add/', add_review_json, name='add_review_json'),
    path('api/review/<int:pk>/delete/', delete_review_json, name='delete_review_by_id'),

]