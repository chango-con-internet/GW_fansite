from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    FACCIONES = [
        ('planta', '🌱 Plantas'),
        ('zombie', '🧟 Zombies'),
        ('neutral', '⚔️ Neutral'),
    ]
    RANGOS = [
        ('semilla', '🌱 Semilla'),
        ('girasol', '🌻 Girasol'),
        ('guerrero', '⚔️ Guerrero'),
        ('comandante', '🎖️ Comandante'),
        ('leyenda', '👑 Leyenda'),
    ]
    MARCOS = [
        ('none', 'Sin marco'),
        ('dorado', '🎨 Marco Dorado'),
        ('diamante', '💎 Marco Diamante'),
    ]
    COLORES = [
        ('none', 'Normal'),
        ('verde', '🟢 Verde'),
        ('azul', '🔵 Azul'),
        ('rojo', '🔴 Rojo'),
        ('morado', '🟣 Morado'),
        ('dorado', '🟡 Dorado'),
    ]
    FONDOS = [
        ('none', 'Sin fondo'),
        ('galaxia', '🌌 Galaxia'),
        ('fuego', '🔥 Fuego'),
        ('matriz', '💻 Matriz'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, max_length=300)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    faccion = models.CharField(max_length=10, choices=FACCIONES, default='neutral')
    rango = models.CharField(max_length=20, choices=RANGOS, default='semilla')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    verificado = models.BooleanField(default=False)
    semillas = models.IntegerField(default=0)
    ultimo_login_bonus = models.DateField(null=True, blank=True)
    seguidores = models.ManyToManyField(
        'self', symmetrical=False, related_name='siguiendo', blank=True
    )
    # Cosméticos
    marco_avatar = models.CharField(max_length=20, choices=MARCOS, default='none')
    color_nombre = models.CharField(max_length=20, choices=COLORES, default='none')
    fondo_perfil = models.CharField(max_length=20, choices=FONDOS, default='none')
    nombre_animado = models.BooleanField(default=False)
    perfil_elite = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.usuario.username} - {self.rango}'

    def actualizar_rango(self):
        if self.rango in ['leyenda', 'comandante']:
            return
        from foro.models import Post, Comentario
        posts = Post.objects.filter(autor=self.usuario).count()
        likes = sum(p.total_likes() for p in Post.objects.filter(autor=self.usuario))
        if posts >= 50 and likes >= 100:
            self.rango = 'guerrero'
        elif posts >= 15 and likes >= 30:
            self.rango = 'girasol'
        else:
            self.rango = 'semilla'
        self.save()

    def calcular_xp(self):
        from foro.models import Post, Comentario
        posts = Post.objects.filter(autor=self.usuario).count()
        likes = sum(p.total_likes() for p in Post.objects.filter(autor=self.usuario))
        comentarios = Comentario.objects.filter(autor=self.usuario).count()
        bonus_rango = {
            'semilla': 0, 'girasol': 50,
            'guerrero': 150, 'comandante': 400, 'leyenda': 1000,
        }.get(self.rango, 0)
        return (posts * 10) + (likes * 5) + (comentarios * 3) + bonus_rango

    def nivel(self):
        return max(1, self.calcular_xp() // 100)

    def poder_batalla(self):
        return self.calcular_xp()

    def ganar_semillas(self, cantidad, motivo=''):
        self.semillas += cantidad
        self.save()
        HistorialSemillas.objects.create(
            usuario=self.usuario,
            cantidad=cantidad,
            motivo=motivo,
            tipo='ganado'
        )

    def gastar_semillas(self, cantidad, motivo=''):
        if self.semillas < cantidad:
            return False
        self.semillas -= cantidad
        self.save()
        HistorialSemillas.objects.create(
            usuario=self.usuario,
            cantidad=cantidad,
            motivo=motivo,
            tipo='gastado'
        )
        return True

    def get_color_nombre_css(self):
        colores = {
            'verde': '#22c55e',
            'azul': '#60a5fa',
            'rojo': '#ef4444',
            'morado': '#a855f7',
            'dorado': '#FFD700',
        }
        return colores.get(self.color_nombre, '')

    def get_marco_css(self):
        marcos = {
            'dorado': '3px solid #FFD700',
            'diamante': '3px solid #60a5fa',
        }
        return marcos.get(self.marco_avatar, '')


class HistorialSemillas(models.Model):
    TIPOS = [
        ('ganado', '📈 Ganado'),
        ('gastado', '📉 Gastado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_semillas')
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario.username} {self.tipo} {self.cantidad} semillas'


class Notificacion(models.Model):
    TIPOS = [
        ('like', '❤️ Like'),
        ('comentario', '💬 Comentario'),
        ('mencion', '📢 Mención'),
    ]
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones_enviadas')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    post = models.ForeignKey('foro.Post', on_delete=models.CASCADE, null=True, blank=True)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.remitente} → {self.destinatario} ({self.tipo})'

    class Meta:
        ordering = ['-fecha']


class Mensaje(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField(max_length=1000)
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.remitente} → {self.destinatario}'

    class Meta:
        ordering = ['fecha']


@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(usuario=instance)