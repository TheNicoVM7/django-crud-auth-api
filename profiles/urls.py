from django.urls import path
from . import views

urlpatterns = [
    path('mi-perfil/', views.edit_profile, name='edit_profile'),
]