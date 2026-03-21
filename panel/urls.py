from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='panel_dashboard'),
    path('usuarios/', views.gestionar_usuarios, name='panel_usuarios'),
    path('usuarios/<int:pk>/rango/', views.cambiar_rango, name='panel_rango'),
    path('usuarios/<int:pk>/banear/', views.banear_usuario, name='panel_banear'),
    path('posts/', views.gestionar_posts, name='panel_posts'),
    path('posts/<int:pk>/eliminar/', views.eliminar_post, name='panel_eliminar_post'),
    path('posts/<int:pk>/destacar/', views.destacar_post, name='panel_destacar'),
    path('contenido/', views.gestionar_contenido, name='panel_contenido'),
]