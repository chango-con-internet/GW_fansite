from django.db import models
from django.contrib.auth.models import User

class Medalla(models.Model):
    TIPOS = [
        ('automatica', 'Automática'),
        ('manual', 'Manual (Admin)'),
    ]
    CATEGORIAS = [
        ('posts', '📝 Posts'),
        ('likes', '❤️ Likes'),
        ('comentarios', '💬 Comentarios'),
        ('tiempo', '⏰ Tiempo'),
        ('especial', '⭐ Especial'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    emoji = models.CharField(max_length=10)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='automatica')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='especial')
    requisito_posts = models.IntegerField(default=0)
    requisito_likes = models.IntegerField(default=0)
    requisito_comentarios = models.IntegerField(default=0)
    requisito_dias = models.IntegerField(default=0)
    orden = models.IntegerField(default=0)
    color = models.CharField(max_length=20, default='#22c55e')

    def __str__(self):
        return f'{self.emoji} {self.nombre}'

    class Meta:
        ordering = ['orden']


class LogroUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logros')
    medalla = models.ForeignKey(Medalla, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'medalla')
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario.username} — {self.medalla.nombre}'