from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Post, Comentario
from usuarios.models import Perfil, Notificacion

def feed(request):
    posts_list = Post.objects.all().order_by('-fecha')
    categoria = request.GET.get('categoria', '')
    faccion = request.GET.get('faccion', '')
    if categoria:
        posts_list = posts_list.filter(categoria=categoria)
    if faccion:
        posts_list = posts_list.filter(faccion=faccion)
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    return render(request, 'foro/feed.html', {
        'posts': posts,
        'categoria': categoria,
        'faccion': faccion,
    })

@login_required
def crear_post(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria = request.POST.get('categoria', 'general')
        faccion = request.POST.get('faccion', 'ambos')
        imagen = request.FILES.get('imagen')
        post = Post.objects.create(
            autor=request.user,
            titulo=titulo,
            contenido=contenido,
            categoria=categoria,
            faccion=faccion,
            imagen=imagen
        )
        try:
            perfil = request.user.perfil
            perfil.actualizar_rango()
            # 🌱 Semillas por publicar post
            perfil.ganar_semillas(5, 'Publicaste un post')
            # Verificar logros
            from logros.utils import verificar_logros
            verificar_logros(request.user)
        except:
            pass
        return redirect('detalle_post', pk=post.pk)
    return render(request, 'foro/crear_post.html')

def detalle_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comentarios = post.comentarios.all().order_by('fecha')
    if request.method == 'POST' and request.user.is_authenticated:
        contenido = request.POST.get('contenido')
        if contenido:
            Comentario.objects.create(post=post, autor=request.user, contenido=contenido)
            if post.autor != request.user:
                Notificacion.objects.create(
                    destinatario=post.autor,
                    remitente=request.user,
                    tipo='comentario',
                    post=post
                )
            # 🌱 Semillas por comentar
            try:
                request.user.perfil.ganar_semillas(1, 'Comentaste un post')
                from logros.utils import verificar_logros
                verificar_logros(request.user)
            except:
                pass
        return redirect('detalle_post', pk=pk)
    return render(request, 'foro/detalle_post.html', {'post': post, 'comentarios': comentarios})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
        # Quitar semillas al autor si se quita el like
        try:
            if post.autor != request.user:
                post.autor.perfil.semillas = max(0, post.autor.perfil.semillas - 2)
                post.autor.perfil.save()
        except:
            pass
    else:
        post.likes.add(request.user)
        liked = True
        if post.autor != request.user:
            Notificacion.objects.get_or_create(
                destinatario=post.autor,
                remitente=request.user,
                tipo='like',
                post=post
            )
            # 🌱 Semillas al autor por recibir like
            try:
                post.autor.perfil.ganar_semillas(2, f'{request.user.username} le dio like a tu post')
            except:
                pass
    return JsonResponse({'liked': liked, 'total': post.total_likes()})

@login_required
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.autor == request.user:
        post.delete()
    return redirect('/')

@login_required
def editar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.autor != request.user:
        return redirect('/foro/')
    if request.method == 'POST':
        post.titulo = request.POST.get('titulo')
        post.contenido = request.POST.get('contenido')
        post.categoria = request.POST.get('categoria', post.categoria)
        post.faccion = request.POST.get('faccion', post.faccion)
        if request.FILES.get('imagen'):
            post.imagen = request.FILES.get('imagen')
        post.fue_editado = True
        post.save()
        return redirect('detalle_post', pk=post.pk)
    return render(request, 'foro/editar_post.html', {'post': post})