from django.shortcuts import render
from .models import Imagen

def galeria(request):
    imagenes = Imagen.objects.all().order_by('-fecha')
    return render(request, 'galeria/galeria.html', {'imagenes': imagenes})