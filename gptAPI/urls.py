from django.urls import path
from . import views

app_name = 'gptAPI'

urlpatterns = [
    # ex: /api/gpt/call/
    path('call/', views.call_gpt_api, name='call_gpt_api'),
]
