from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()

    def __str__(self):
        return self.nombre
    
class UserActionLog(models.Model):
    # Acciones
    ACCIONES = [
        ('CREATE', 'Creó'),
        ('UPDATE', 'Actualizó'),
        ('DELETE', 'Eliminó'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=10, choices=ACCIONES)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"