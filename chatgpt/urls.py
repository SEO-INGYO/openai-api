# chatapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get-response/', views.get_response, name='get-response'),
    path('get-session-history', views.get_session_history, name='get-session-history'),
]