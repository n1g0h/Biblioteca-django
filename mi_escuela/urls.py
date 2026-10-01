
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from libros import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'libros/',
        views.listar,
        name='listar'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path(
        'dashboard/',
        views.dashboard_usuario,
        name='dashboard_usuario'
    ),

    path(
        'reportes/',
        views.reporte_general,
        name='reporte_general'
    ),
]


from django.contrib import admin
from django.urls import path
from libros.views import listar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('libros/', listar, name='listar'),
]

