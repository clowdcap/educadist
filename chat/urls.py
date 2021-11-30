from django.urls import path
from . import views

app_name = 'chat'

urlpatterns=[
    path('sala/<int:curso_id>/', views.chat_curso, name='sala_chat'),
]
