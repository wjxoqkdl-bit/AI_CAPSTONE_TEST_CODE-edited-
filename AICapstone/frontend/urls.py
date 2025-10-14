# frontend/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('search/', views.search_page_view, name='search_page'),
    path('run-recommendation/', views.recommendation_result_view, name='run_recommendation'),
    path('load-chat/<int:chat_id>/', views.load_chat_view, name='load_chat'),
]
