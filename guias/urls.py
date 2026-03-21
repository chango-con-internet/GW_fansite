from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_guias, name='lista_guias'),
    path('<int:pk>/', views.detalle_guia, name='detalle_guia'),
    path('crear/', views.crear_guia, name='crear_guia'),
    path('<int:pk>/eliminar/', views.eliminar_guia, name='eliminar_guia'),
    path('<int:pk>/aprobar/', views.aprobar_guia, name='aprobar_guia'),
    path('pendientes/', views.guias_pendientes, name='guias_pendientes'),
]