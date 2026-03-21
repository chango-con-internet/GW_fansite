from .models import Medalla, LogroUsuario
from django.utils import timezone

def verificar_logros(user):
    from foro.models import Post, Comentario

    posts = Post.objects.filter(autor=user).count()
    likes = sum(p.total_likes() for p in Post.objects.filter(autor=user))
    comentarios = Comentario.objects.filter(autor=user).count()
    dias = (timezone.now() - user.date_joined).days

    medallas_auto = Medalla.objects.filter(tipo='automatica')

    for medalla in medallas_auto:
        ya_tiene = LogroUsuario.objects.filter(usuario=user, medalla=medalla).exists()
        if ya_tiene:
            continue

        cumple = True
        if medalla.requisito_posts > 0 and posts < medalla.requisito_posts:
            cumple = False
        if medalla.requisito_likes > 0 and likes < medalla.requisito_likes:
            cumple = False
        if medalla.requisito_comentarios > 0 and comentarios < medalla.requisito_comentarios:
            cumple = False
        if medalla.requisito_dias > 0 and dias < medalla.requisito_dias:
            cumple = False

        if cumple:
            LogroUsuario.objects.create(usuario=user, medalla=medalla)
            # 🌱 Semillas por logro desbloqueado
            try:
                user.perfil.ganar_semillas(10, f'Lograste: {medalla.nombre}')
            except:
                pass