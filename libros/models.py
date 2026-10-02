from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=20, unique=True)
    categoria = models.CharField(max_length=100, default='General')
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.titulo


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Reserva(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Reserva de {self.libro.titulo} por {self.usuario.username}"


class Prestamo(models.Model):
    ESTADOS = (
        ('ACTIVO', 'Activo'),
        ('DEVUELTO', 'Devuelto'),
        ('ATRASADO', 'Atrasado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_prestamo = models.DateField(default=timezone.now)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')

    def __str__(self):
        return f"Préstamo: {self.libro.titulo} - {self.usuario.username}"


class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra: {self.libro.titulo} por {self.usuario.username}"


class Multa(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Multa ${self.monto} - {self.prestamo.usuario.username}"
