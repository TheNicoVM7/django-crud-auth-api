from django.contrib import admin
from .models import UserActionLog

# Register your models here.
admin.site.site_header = "Mi Portafolio"
admin.site.site_title = "Portal de Administración"
admin.site.index_title = "Bienvenido al Gestor de Contenido"

@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'descripcion')
    list_filter = ('accion', 'usuario')
    readonly_fields = ('fecha', 'usuario', 'accion', 'descripcion') # Para que no se puedan alterar