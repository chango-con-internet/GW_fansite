from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.logros_usuario, name='logros'),
    path('<str:username>/otorgar/<int:medalla_id>/', views.otorgar_medalla, name='otorgar_medalla'),
    path('<str:username>/quitar/<int:medalla_id>/', views.quitar_medalla, name='quitar_medalla'),
]