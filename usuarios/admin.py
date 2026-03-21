from django.contrib import admin
from .models import Perfil
from .models import Perfil, Notificacion
admin.site.register(Notificacion)
admin.site.register(Perfil)