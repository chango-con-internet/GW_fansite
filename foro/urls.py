from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('crear/', views.crear_post, name='crear_post'),
    path('post/<int:pk>/', views.detalle_post, name='detalle_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/eliminar/', views.eliminar_post, name='eliminar_post'),
    path('post/<int:pk>/editar/', views.editar_post, name='editar_post'),
]