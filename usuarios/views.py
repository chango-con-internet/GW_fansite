from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Perfil, Notificacion, Mensaje

# 🔐 LOGIN
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/panel/')
        return redirect('/foro/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('/panel/')
            return redirect('/foro/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    response = render(request, 'usuarios/login.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    return response

# 📝 REGISTER
def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        faccion = request.POST.get('faccion', 'neutral')
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya existe')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            try:
                perfil = user.perfil
                perfil.faccion = faccion
                perfil.save()
            except:
                Perfil.objects.create(usuario=user, faccion=faccion)
            login(request, user)
            return redirect('/foro/')
    response = render(request, 'usuarios/register.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response['Pragma'] = 'no-cache'
    return response

# 🚪 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/')

# 👤 PERFIL
def perfil_view(request, username):
    user = get_object_or_404(User, username=username)
    perfil = get_object_or_404(Perfil, usuario=user)
    from foro.models import Post
    from logros.models import LogroUsuario
    from logros.utils import verificar_logros
    posts = Post.objects.filter(autor=user).order_by('-fecha')
    total_likes = sum(post.total_likes() for post in posts)
    xp = perfil.calcular_xp()
    nivel = perfil.nivel()
    poder = perfil.poder_batalla()
    verificar_logros(user)
    medallas = LogroUsuario.objects.filter(usuario=user).select_related('medalla').order_by('medalla__orden')
    return render(request, 'usuarios/perfil.html', {
        'perfil': perfil,
        'user_perfil': user,
        'posts': posts,
        'total_likes': total_likes,
        'xp': xp,
        'nivel': nivel,
        'poder': poder,
        'medallas': medallas,
    })

# ✏️ EDITAR PERFIL
@login_required
def editar_perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    if request.method == 'POST':
        perfil.bio = request.POST.get('bio', '')
        perfil.faccion = request.POST.get('faccion', 'neutral')
        avatar = request.FILES.get('avatar')
        if avatar:
            perfil.avatar = avatar
        perfil.save()
        return redirect(f'/usuarios/perfil/{request.user.username}/')
    return render(request, 'usuarios/editar_perfil.html', {'perfil': perfil})

# 🔔 NOTIFICACIONES
@login_required
def notificaciones_view(request):
    notifs = Notificacion.objects.filter(destinatario=request.user)
    notifs.filter(leida=False).update(leida=True)
    return render(request, 'usuarios/notificaciones.html', {'notificaciones': notifs})

@login_required
def notificaciones_count(request):
    count = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
    return JsonResponse({'count': count})

@login_required
def notificaciones_latest(request):
    notif = Notificacion.objects.filter(destinatario=request.user, leida=False).first()
    if notif:
        return JsonResponse({
            'tipo': notif.tipo,
            'remitente': notif.remitente.username,
            'post_titulo': notif.post.titulo if notif.post else '',
        })
    return JsonResponse({'tipo': '', 'remitente': '', 'post_titulo': ''})

# 🔵 VERIFICAR USUARIO
@login_required
def verificar_usuario(request, username):
    if not request.user.is_staff:
        return redirect('/')
    user = get_object_or_404(User, username=username)
    perfil = get_object_or_404(Perfil, usuario=user)
    if user.is_staff:
        return redirect(f'/usuarios/perfil/{username}/')
    perfil.verificado = not perfil.verificado
    perfil.save()
    return redirect(f'/usuarios/perfil/{username}/')

# 👥 SEGUIR USUARIO
@login_required
def seguir_usuario(request, username):
    user_a_seguir = get_object_or_404(User, username=username)
    if user_a_seguir == request.user:
        return redirect(f'/usuarios/perfil/{username}/')
    perfil_actual = request.user.perfil
    perfil_a_seguir = user_a_seguir.perfil
    if perfil_a_seguir in perfil_actual.seguidores.all():
        perfil_actual.seguidores.remove(perfil_a_seguir)
        siguiendo = False
    else:
        perfil_actual.seguidores.add(perfil_a_seguir)
        siguiendo = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'siguiendo': siguiendo, 'total': perfil_a_seguir.siguiendo.count()})
    return redirect(f'/usuarios/perfil/{username}/')

# 💬 MENSAJES
@login_required
def mensajes(request):
    from django.db.models import Q
    conversaciones = User.objects.filter(
        Q(mensajes_enviados__destinatario=request.user) |
        Q(mensajes_recibidos__remitente=request.user)
    ).exclude(id=request.user.id).distinct()
    return render(request, 'usuarios/mensajes.html', {'conversaciones': conversaciones})

@login_required
def conversacion(request, username):
    otro_usuario = get_object_or_404(User, username=username)
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            msg = Mensaje.objects.create(
                remitente=request.user,
                destinatario=otro_usuario,
                contenido=contenido
            )
            Mensaje.objects.filter(
                remitente=otro_usuario, destinatario=request.user, leido=False
            ).update(leido=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                perfil = request.user.perfil
                if perfil.avatar:
                    avatar = f'<img src="{perfil.avatar.url}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">'
                elif perfil.faccion == 'planta':
                    avatar = '🌱'
                elif perfil.faccion == 'zombie':
                    avatar = '🧟'
                else:
                    avatar = '⚔️'
                return JsonResponse({'ok': True, 'id': msg.id, 'fecha': msg.fecha.strftime('%d/%m %H:%M'), 'mi_avatar': avatar})
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return redirect(f'/usuarios/mensajes/{username}/')
    mensajes_conv = Mensaje.objects.filter(
        remitente__in=[request.user, otro_usuario],
        destinatario__in=[request.user, otro_usuario]
    ).order_by('fecha')
    Mensaje.objects.filter(remitente=otro_usuario, destinatario=request.user, leido=False).update(leido=True)
    return render(request, 'usuarios/conversacion.html', {
        'otro_usuario': otro_usuario,
        'mensajes': mensajes_conv,
    })

@login_required
def mensajes_count(request):
    count = Mensaje.objects.filter(destinatario=request.user, leido=False).count()
    return JsonResponse({'count': count})

@login_required
def mensajes_nuevos(request, username):
    otro_usuario = get_object_or_404(User, username=username)
    ultimo_id = int(request.GET.get('ultimo', 0))
    nuevos = Mensaje.objects.filter(
        remitente__in=[request.user, otro_usuario],
        destinatario__in=[request.user, otro_usuario],
        id__gt=ultimo_id
    ).order_by('fecha')
    data = []
    for msg in nuevos:
        perfil = msg.remitente.perfil
        if perfil.avatar:
            emoji = f'<img src="{perfil.avatar.url}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">'
        elif perfil.faccion == 'planta':
            emoji = '🌱'
        elif perfil.faccion == 'zombie':
            emoji = '🧟'
        else:
            emoji = '⚔️'
        data.append({
            'id': msg.id,
            'contenido': msg.contenido,
            'fecha': msg.fecha.strftime('%d/%m %H:%M'),
            'soy_yo': msg.remitente == request.user,
            'avatar_emoji': emoji,
        })
    Mensaje.objects.filter(remitente=otro_usuario, destinatario=request.user, leido=False).update(leido=True)
    return JsonResponse({'mensajes': data})

# 🏆 CLASIFICACION
def tabla_clasificacion(request):
    from foro.models import Post, Comentario
    perfiles = Perfil.objects.select_related('usuario').all()
    ranking = []
    for perfil in perfiles:
        posts = Post.objects.filter(autor=perfil.usuario).count()
        likes = sum(p.total_likes() for p in Post.objects.filter(autor=perfil.usuario))
        comentarios = Comentario.objects.filter(autor=perfil.usuario).count()
        xp = perfil.calcular_xp()
        ranking.append({
            'perfil': perfil,
            'posts': posts,
            'likes': likes,
            'comentarios': comentarios,
            'xp': xp,
            'nivel': perfil.nivel(),
            'poder': perfil.poder_batalla(),
        })
    ranking.sort(key=lambda x: x['poder'], reverse=True)
    return render(request, 'usuarios/clasificacion.html', {'ranking': ranking})
@login_required
def tienda_semillas(request):
    from django.utils import timezone
    import datetime
    perfil = request.user.perfil

    # Login diario bonus
    hoy = timezone.now().date()
    if perfil.ultimo_login_bonus != hoy:
        perfil.ganar_semillas(3, 'Bonus de login diario ☀️')
        perfil.ultimo_login_bonus = hoy
        perfil.save()
        login_bonus = True
    else:
        login_bonus = False

    historial = request.user.historial_semillas.all()[:20]

    TIENDA = [
        {'id': 'marco_dorado', 'nombre': '🎨 Marco Dorado', 'descripcion': 'Marco dorado en tu avatar', 'precio': 50, 'campo': 'marco_avatar', 'valor': 'dorado'},
        {'id': 'color_verde', 'nombre': '🟢 Nombre Verde', 'descripcion': 'Tu nombre en verde brillante', 'precio': 100, 'campo': 'color_nombre', 'valor': 'verde'},
        {'id': 'color_azul', 'nombre': '🔵 Nombre Azul', 'descripcion': 'Tu nombre en azul eléctrico', 'precio': 100, 'campo': 'color_nombre', 'valor': 'azul'},
        {'id': 'color_rojo', 'nombre': '🔴 Nombre Rojo', 'descripcion': 'Tu nombre en rojo fuego', 'precio': 100, 'campo': 'color_nombre', 'valor': 'rojo'},
        {'id': 'color_morado', 'nombre': '🟣 Nombre Morado', 'descripcion': 'Tu nombre en morado oscuro', 'precio': 100, 'campo': 'color_nombre', 'valor': 'morado'},
        {'id': 'color_dorado', 'nombre': '🟡 Nombre Dorado', 'descripcion': 'Tu nombre en dorado real', 'precio': 150, 'campo': 'color_nombre', 'valor': 'dorado'},
        {'id': 'fondo_galaxia', 'nombre': '🌌 Fondo Galaxia', 'descripcion': 'Fondo espacial en tu perfil', 'precio': 150, 'campo': 'fondo_perfil', 'valor': 'galaxia'},
        {'id': 'fondo_fuego', 'nombre': '🔥 Fondo Fuego', 'descripcion': 'Fondo de llamas en tu perfil', 'precio': 150, 'campo': 'fondo_perfil', 'valor': 'fuego'},
        {'id': 'fondo_matriz', 'nombre': '💻 Fondo Matriz', 'descripcion': 'Fondo estilo Matrix en tu perfil', 'precio': 150, 'campo': 'fondo_perfil', 'valor': 'matriz'},
        {'id': 'marco_diamante', 'nombre': '💎 Marco Diamante', 'descripcion': 'El marco más exclusivo', 'precio': 500, 'campo': 'marco_avatar', 'valor': 'diamante'},
        {'id': 'nombre_animado', 'nombre': '✨ Nombre Animado', 'descripcion': 'Tu nombre brilla con animación', 'precio': 800, 'campo': 'nombre_animado', 'valor': True},
        {'id': 'perfil_elite', 'nombre': '🔱 Perfil Élite', 'descripcion': 'Todos los cosméticos premium desbloqueados', 'precio': 2000, 'campo': 'perfil_elite', 'valor': True},
    ]

    return render(request, 'usuarios/tienda.html', {
        'perfil': perfil,
        'tienda': TIENDA,
        'historial': historial,
        'login_bonus': login_bonus,
    })

@login_required
def comprar_cosmético(request, item_id):
    from django.utils import timezone
    perfil = request.user.perfil

    TIENDA = {
        'marco_dorado': {'precio': 50, 'campo': 'marco_avatar', 'valor': 'dorado', 'nombre': 'Marco Dorado'},
        'color_verde': {'precio': 100, 'campo': 'color_nombre', 'valor': 'verde', 'nombre': 'Nombre Verde'},
        'color_azul': {'precio': 100, 'campo': 'color_nombre', 'valor': 'azul', 'nombre': 'Nombre Azul'},
        'color_rojo': {'precio': 100, 'campo': 'color_nombre', 'valor': 'rojo', 'nombre': 'Nombre Rojo'},
        'color_morado': {'precio': 100, 'campo': 'color_nombre', 'valor': 'morado', 'nombre': 'Nombre Morado'},
        'color_dorado': {'precio': 150, 'campo': 'color_nombre', 'valor': 'dorado', 'nombre': 'Nombre Dorado'},
        'fondo_galaxia': {'precio': 150, 'campo': 'fondo_perfil', 'valor': 'galaxia', 'nombre': 'Fondo Galaxia'},
        'fondo_fuego': {'precio': 150, 'campo': 'fondo_perfil', 'valor': 'fuego', 'nombre': 'Fondo Fuego'},
        'fondo_matriz': {'precio': 150, 'campo': 'fondo_perfil', 'valor': 'matriz', 'nombre': 'Fondo Matriz'},
        'marco_diamante': {'precio': 500, 'campo': 'marco_avatar', 'valor': 'diamante', 'nombre': 'Marco Diamante'},
        'nombre_animado': {'precio': 800, 'campo': 'nombre_animado', 'valor': True, 'nombre': 'Nombre Animado'},
        'perfil_elite': {'precio': 2000, 'campo': 'perfil_elite', 'valor': True, 'nombre': 'Perfil Élite'},
    }

    item = TIENDA.get(item_id)
    if not item:
        return redirect('/usuarios/tienda/')

    if perfil.gastar_semillas(item['precio'], f'Compró: {item["nombre"]}'):
        setattr(perfil, item['campo'], item['valor'])
        perfil.save()

    return redirect('/usuarios/tienda/')