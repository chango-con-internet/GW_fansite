from django.shortcuts import render, get_object_or_404
from .models import Personaje

def lista_personajes(request):
    personajes = Personaje.objects.all()
    return render(request, 'personajes/lista.html', {'personajes': personajes})

def detalle_personaje(request, pk):
    personaje = get_object_or_404(Personaje, pk=pk)
    return render(request, 'personajes/detalle.html', {'personaje': personaje})