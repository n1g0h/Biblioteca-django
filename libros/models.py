# Create your models here.

from django.db import models

class Libro(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    autor = models.CharField(max_length=100)
    fecha_publicacion = models.IntegerField()
    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', '🟢 Disponible'
        DANADO = 'DANADO','🟡 Dañado'
        NO_DISPONIBLE = 'NO_DISPONIBLE', '🔴 Prestado'

    disponibilidad = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE
    )
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ['titulo']