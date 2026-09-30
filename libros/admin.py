from django.contrib import admin
from .models import Libro, PerfilUsuario, Prestamo, Multa, Reserva

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'cantidad_disponible')
    search_fields = ('titulo', 'autor', 'ISBN', 'categoria')
    list_filter = ('categoria', 'cantidad_disponible')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'dni', 'telefono', 'fecha_afiliacion', 'estado')
    search_fields = ('user__username', 'dni', 'telefono')
    list_filter = ('estado',)


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
            prestamo.registrar_devolucion()


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ('prestamo', 'monto', 'motivo', 'pagado', 'fecha_creacion')
    search_fields = ('prestamo__usuario__username', 'motivo')
    list_filter = ('pagado', 'fecha_creacion')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'fecha_reserva', 'estado')
    search_fields = ('usuario__username', 'libro__titulo')
    list_filter = ('estado', 'fecha_reserva')
    raw_id_fields = ('usuario', 'libro')

