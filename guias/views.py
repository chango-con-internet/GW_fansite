from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Guia

def lista_guias(request):
    guias = Guia.objects.filter(aprobada=True).order_by('-fecha')
    return render(request, 'guias/lista.html', {'guias': guias})

def detalle_guia(request, pk):
    guia = get_object_or_404(Guia, pk=pk)
    return render(request, 'guias/detalle.html', {'guia': guia})

@login_required
def crear_guia(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        contenido = request.POST.get('contenido')
        nivel = request.POST.get('nivel', 'principiante')
        categoria = request.POST.get('categoria', 'estrategia')
        # Admins aprueban automáticamente
        aprobada = request.user.is_staff
        Guia.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            contenido=contenido,
            nivel=nivel,
            categoria=categoria,
            autor=request.user,
            aprobada=aprobada
        )
        if aprobada:
            return redirect('/guias/')
        else:
            return redirect('/guias/?pendiente=1')
    return render(request, 'guias/crear_guia.html')

@login_required
def eliminar_guia(request, pk):
    guia = get_object_or_404(Guia, pk=pk)
    if guia.autor == request.user or request.user.is_staff:
        guia.delete()
    return redirect('/guias/')

@login_required
def aprobar_guia(request, pk):
    if not request.user.is_staff:
        return redirect('/guias/')
    guia = get_object_or_404(Guia, pk=pk)
    guia.aprobada = True
    guia.save()
    return redirect('/guias/pendientes/')

@login_required
def guias_pendientes(request):
    if not request.user.is_staff:
        return redirect('/guias/')
    pendientes = Guia.objects.filter(aprobada=False).order_by('-fecha')
    return render(request, 'guias/pendientes.html', {'pendientes': pendientes})