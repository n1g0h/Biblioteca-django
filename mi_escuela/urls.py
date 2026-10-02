from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from libros import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),

    # Catálogo y Operaciones
    path('catalogo/', views.catalogo, name='catalogo'),
    path('reservar/<int:libro_id>/', views.reservar_libro, name='reservar_libro'),
    path('comprar/<int:libro_id>/', views.comprar_libro, name='comprar_libro'),

    # Autenticación y Registro
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Vistas principales
    path('dashboard/', views.dashboard_usuario, name='dashboard_usuario'),
    path('reportes/', views.reporte_general, name='reporte_general'),

    path('admin/', admin.site.urls),
]

