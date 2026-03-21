from django.db import models
from django.contrib.auth.models import User

class Guia(models.Model):
    NIVELES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]
    CATEGORIAS = [
        ('estrategia', 'Estrategia'),
        ('personaje', 'Personaje'),
        ('modo', 'Modo de juego'),
        ('secretos', 'Secretos'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    contenido = models.TextField()
    nivel = models.CharField(max_length=20, choices=NIVELES)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='guias', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo