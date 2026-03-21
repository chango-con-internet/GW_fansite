from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/<str:username>/', views.perfil_view, name='perfil'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('notificaciones/count/', views.notificaciones_count, name='notificaciones_count'),
    path('notificaciones/latest/', views.notificaciones_latest, name='notificaciones_latest'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('verificar/<str:username>/', views.verificar_usuario, name='verificar_usuario'),
    path('seguir/<str:username>/', views.seguir_usuario, name='seguir_usuario'),
    path('mensajes/', views.mensajes, name='mensajes'),
    path('mensajes/count/', views.mensajes_count, name='mensajes_count'),
    path('mensajes/<str:username>/nuevos/', views.mensajes_nuevos, name='mensajes_nuevos'),
    path('mensajes/<str:username>/', views.conversacion, name='conversacion'),
    path('clasificacion/', views.tabla_clasificacion, name='clasificacion'),
    path('tienda/', views.tienda_semillas, name='tienda'),
    path('tienda/comprar/<str:item_id>/', views.comprar_cosmético, name='comprar'),
]