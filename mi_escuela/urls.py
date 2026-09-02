
from django.contrib import admin
from django.urls import path
from libros.views import listar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('libros/', listar, name='listar'),
]

