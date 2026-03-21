from django.db import models

class Imagen(models.Model):
    JUEGOS = [
        ('gw1', 'Garden Warfare 1'),
        ('gw2', 'Garden Warfare 2'),
        ('ambos', 'GW1 y GW2'),
    ]
    CATEGORIAS = [
        ('personaje', 'Personaje'),
        ('mapa', 'Mapa'),
        ('gameplay', 'Gameplay'),
        ('arte', 'Arte'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='galeria/')
    juego = models.CharField(max_length=10, choices=JUEGOS)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo