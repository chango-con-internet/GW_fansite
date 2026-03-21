from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Medalla, LogroUsuario

CATEGORIAS = [
    ('posts', '📝 Posts'),
    ('likes', '❤️ Likes'),
    ('comentarios', '💬 Comentarios'),
    ('tiempo', '⏰ Tiempo en la comunidad'),
    ('especial', '⭐ Especiales'),
]

def logros_usuario(request, username):
    from logros.utils import verificar_logros
    user = get_object_or_404(User, username=username)
    # Verificar logros automáticos
    verificar_logros(user)
    logros = LogroUsuario.objects.filter(usuario=user).select_related('medalla')
    todas = Medalla.objects.all()
    logros_ids = list(logros.values_list('medalla_id', flat=True))
    return render(request, 'logros/logros.html', {
        'user_perfil': user,
        'logros': logros,
        'todas': todas,
        'logros_ids': logros_ids,
        'categorias': CATEGORIAS,
    })

@login_required
def otorgar_medalla(request, username, medalla_id):
    if not request.user.is_staff:
        return redirect('/')
    user = get_object_or_404(User, username=username)
    medalla = get_object_or_404(Medalla, pk=medalla_id, tipo='manual')
    LogroUsuario.objects.get_or_create(usuario=user, medalla=medalla)
    return redirect(f'/logros/{username}/')

@login_required
def quitar_medalla(request, username, medalla_id):
    if not request.user.is_staff:
        return redirect('/')
    user = get_object_or_404(User, username=username)
    LogroUsuario.objects.filter(usuario=user, medalla_id=medalla_id).delete()
    return redirect(f'/logros/{username}/')