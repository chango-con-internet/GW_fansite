from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Post(models.Model):
    CATEGORIAS = [
        ('general', '💬 General'),
        ('estrategia', '⚔️ Estrategia'),
        ('builds', '🔧 Builds'),
        ('humor', '😄 Humor'),
        ('noticias', '📰 Noticias'),
    ]
    FACCIONES = [
        ('planta', '🌱 Plantas'),
        ('zombie', '🧟 Zombies'),
        ('ambos', '⚔️ Ambos'),
    ]
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    imagen = CloudinaryField('image', blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='general')
    faccion = models.CharField(max_length=10, choices=FACCIONES, default='ambos')
    likes = models.ManyToManyField(User, related_name='posts_liked', blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)
    fue_editado = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

    def total_likes(self):
        return self.likes.count()

    def total_comentarios(self):
        return self.comentarios.count()

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comentarios_liked', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='respuestas'
    )

    def __str__(self):
        return f'{self.autor.username} en {self.post.titulo}'