
from django.urls import path
from . import views


urlpatterns = [
    path('', views.signin, name = 'homepage'),
    path('signin/', views.signin, name = 'signin'),
    path('signup/', views.signup, name = 'signup'),
    path('logout/', views.logout, name = 'logout'),
    path('setting/', views.setting, name = 'setting'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
]

