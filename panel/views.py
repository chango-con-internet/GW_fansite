from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from foro.models import Post, Comentario
from usuarios.models import Perfil
from guias.models import Guia
from personajes.models import Personaje

def es_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(es_admin, login_url='/usuarios/login/')
def dashboard(request):
    from usuarios.models import Mensaje
    total_usuarios = User.objects.count()
    total_posts = Post.objects.count()
    total_comentarios = Comentario.objects.count()
    total_guias = Guia.objects.count()
    total_personajes = Personaje.objects.count()
    total_mensajes = Mensaje.objects.count()

    hace_7_dias = timezone.now() - timedelta(days=7)
    posts_semana = Post.objects.filter(fecha__gte=hace_7_dias).count()
    usuarios_semana = User.objects.filter(date_joined__gte=hace_7_dias).count()

    posts_recientes = Post.objects.all().order_by('-fecha')[:5]
    usuarios_recientes = User.objects.all().order_by('-date_joined')[:5]

    plantas = Perfil.objects.filter(faccion='planta').count()
    zombies = Perfil.objects.filter(faccion='zombie').count()
    neutrales = Perfil.objects.filter(faccion='neutral').count()


    guias_pendientes_count = Guia.objects.filter(aprobada=False).count()
    usuarios_verificados = Perfil.objects.filter(verificado=True).count()

    rangos = {
        '🌱 Semilla': Perfil.objects.filter(rango='semilla').count(),
        '🌻 Girasol': Perfil.objects.filter(rango='girasol').count(),
        '⚔️ Guerrero': Perfil.objects.filter(rango='guerrero').count(),
        '🎖️ Comandante': Perfil.objects.filter(rango='comandante').count(),
        '👑 Leyenda': Perfil.objects.filter(rango='leyenda').count(),
    }

    context = {
        'total_usuarios': total_usuarios,
        'total_posts': total_posts,
        'total_comentarios': total_comentarios,
        'total_guias': total_guias,
        'total_personajes': total_personajes,
        'total_mensajes': total_mensajes,
        'posts_semana': posts_semana,
        'usuarios_semana': usuarios_semana,
        'posts_recientes': posts_recientes,
        'usuarios_recientes': usuarios_recientes,
        'plantas': plantas,
        'zombies': zombies,
        'neutrales': neutrales,
        'guias_pendientes_count': guias_pendientes_count,
        'usuarios_verificados': usuarios_verificados,
        'rangos': rangos,
    }
    return render(request, 'panel/dashboard.html', context)

@user_passes_test(es_admin, login_url='/usuarios/login/')
def gestionar_usuarios(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'panel/usuarios.html', {'usuarios': usuarios})

@user_passes_test(es_admin, login_url='/usuarios/login/')
def cambiar_rango(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        nuevo_rango = request.POST.get('rango')
        try:
            perfil = user.perfil
            perfil.rango = nuevo_rango
            perfil.save()
        except:
            pass
    return redirect('panel_usuarios')

@user_passes_test(es_admin, login_url='/usuarios/login/')
def banear_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser:
        user.is_active = not user.is_active
        user.save()
    return redirect('panel_usuarios')

@user_passes_test(es_admin, login_url='/usuarios/login/')
def gestionar_posts(request):
    posts = Post.objects.all().order_by('-fecha')
    return render(request, 'panel/posts.html', {'posts': posts})

@user_passes_test(es_admin, login_url='/usuarios/login/')
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('panel_posts')

@user_passes_test(es_admin, login_url='/usuarios/login/')
def destacar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.destacado = not getattr(post, 'destacado', False)
    post.save()
    return redirect('panel_posts')

@user_passes_test(es_admin, login_url='/usuarios/login/')
def gestionar_contenido(request):
    guias = Guia.objects.all().order_by('-fecha')
    personajes = Personaje.objects.all()
    return render(request, 'panel/contenido.html', {'guias': guias, 'personajes': personajes})

