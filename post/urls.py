
from django.urls import path
from . import views


urlpatterns = [
    path('post/createpost/', views.post_to_selected_platforms, name = 'post_to_selected_platforms'),
    path('insight/', views.insight, name = 'insight'),
]

