from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    ISBN = models.CharField(max_length=13, unique=True)
    cantidad_total = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    cantidad_disponible = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    categoria = models.CharField(max_length=100)
    año = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.titulo


class PerfilUsuario(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    fecha_afiliacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"


class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('DEVUELTO', 'Devuelto'),
        ('ATRASADO', 'Atrasado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')

    def registrar_devolucion(self, fecha_devolucion=None):
        if self.estado == 'DEVUELTO':
            return

        fecha_real = fecha_devolucion or date.today()
        self.fecha_devolucion_real = fecha_real
        self.estado = 'DEVUELTO'
        self.save()

        # 1. Cálculo automático de multas ($100/día)
        if fecha_real > self.fecha_devolucion_esperada:
            dias_atraso = (fecha_real - self.fecha_devolucion_esperada).days
            monto_multa = dias_atraso * 100.00
            
            Multa.objects.create(
                prestamo=self,
                monto=monto_multa,
                motivo=f"Devolución con {dias_atraso} día(s) de atraso ($100/día).",
                pagado=False
            )

        # 2. Reingreso de stock disponible
        self.libro.cantidad_disponible += 1
        self.libro.save()

        # 3. Préstamo en cascada sobre reservas pendientes
        reserva_pendiente = Reserva.objects.filter(
            libro=self.libro, 
            estado='PENDIENTE'
        ).order_by('fecha_reserva').first()

        if reserva_pendiente:
            reserva_pendiente.estado = 'COMPLETADA'
            reserva_pendiente.save()

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo}"


class Multa(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Multa: ${self.monto} - {self.prestamo.usuario.username}"


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_reserva = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f"Reserva de {self.libro.titulo} por {self.usuario.username}"
