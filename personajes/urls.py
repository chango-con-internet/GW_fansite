from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_personajes, name='lista_personajes'),
    path('<int:pk>/', views.detalle_personaje, name='detalle_personaje'),
]