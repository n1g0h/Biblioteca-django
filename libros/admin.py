
from django.contrib import admin
from .models import Libro, PerfilUsuario, Prestamo, Multa, Reserva

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ISBN', 'cantidad_disponible', 'precio')
    search_fields = ('titulo', 'autor', 'ISBN')
    list_filter = ('cantidad_disponible',)

admin.site.register(PerfilUsuario)
admin.site.register(Prestamo)
admin.site.register(Multa)
admin.site.register(Reserva)

