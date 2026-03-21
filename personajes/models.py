from django.db import models

class Personaje(models.Model):
    FACCIONES = [
        ('planta', 'Planta'),
        ('zombie', 'Zombie'),
    ]
    ROLES = [
        ('ataque', 'Ataque'),
        ('soporte', 'Soporte'),
        ('defensa', 'Defensa'),
        ('control', 'Control'),
    ]
    JUEGOS = [
        ('gw1', 'Garden Warfare 1'),
        ('gw2', 'Garden Warfare 2'),
        ('ambos', 'GW1 y GW2'),
    ]

    nombre = models.CharField(max_length=100)
    faccion = models.CharField(max_length=10, choices=FACCIONES)
    rol = models.CharField(max_length=10, choices=ROLES)
    juego = models.CharField(max_length=10, choices=JUEGOS)
    descripcion = models.TextField()
    dificultad = models.IntegerField(default=1)
    imagen = models.ImageField(upload_to='personajes/', blank=True, null=True)  # ← nueva

    def __str__(self):
        return self.nombre