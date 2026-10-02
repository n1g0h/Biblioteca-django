from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Libro, PerfilUsuario, Prestamo, Multa, Reserva, Compra


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'cantidad_disponible', 'cantidad_total', 'precio')
    search_fields = ('titulo', 'autor', 'ISBN', 'categoria')
    list_filter = ('categoria', 'cantidad_disponible')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'dni', 'telefono')
    search_fields = ('user__username', 'dni', 'telefono')


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 
        'libro', 
        'fecha_prestamo', 
        'fecha_devolucion_esperada', 
        'fecha_devolucion_real', 
        'estado'
    )
    search_fields = ('usuario__username', 'libro__titulo')
    list_filter = ('estado', 'fecha_prestamo')
    raw_id_fields = ('usuario', 'libro')
    actions = ['marcar_como_devuelto_action']

    @admin.action(description="Marcar préstamo(s) seleccionado(s) como devuelto(s)")
    def marcar_como_devuelto_action(self, request, queryset):
        for prestamo in queryset:
            prestamo.estado = 'DEVUELTO'
            prestamo.fecha_devolucion_real = timezone.now().date()
            prestamo.save()
            
            # Devolver el stock al catálogo
            libro = prestamo.libro
            libro.cantidad_disponible += 1
            libro.save()


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'fecha_reserva', 'estado')
    search_fields = ('usuario__username', 'libro__titulo')
    list_filter = ('estado', 'fecha_reserva')
    raw_id_fields = ('usuario', 'libro')
    actions = ['convertir_reserva_en_prestamo']

    @admin.action(description="Convertir reserva(s) en préstamo activo (7 días)")
    def convertir_reserva_en_prestamo(self, request, queryset):
        for reserva in queryset.filter(estado='PENDIENTE'):
            Prestamo.objects.create(
                usuario=reserva.usuario,
                libro=reserva.libro,
                fecha_prestamo=timezone.now().date(),
                fecha_devolucion_esperada=timezone.now().date() + timedelta(days=7),
                estado='ACTIVO'
            )
            reserva.estado = 'COMPLETADA'
            reserva.save()


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'precio_pagado', 'fecha_compra')
    search_fields = ('usuario__username', 'libro__titulo')
    list_filter = ('fecha_compra',)
    raw_id_fields = ('usuario', 'libro')


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ('prestamo', 'monto', 'pagado')
    search_fields = ('prestamo__usuario__username',)
    list_filter = ('pagado',)

