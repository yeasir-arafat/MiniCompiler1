from django.urls import path
from . import views

urlpatterns = [
    path('', views.code_editor, name='code_editor'),
    path('execute_code/', views.execute_code, name='execute_code'),
    path('send_input/', views.send_input, name='send_input'),
]