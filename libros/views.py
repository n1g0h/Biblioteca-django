# Create your views here.

from django.shortcuts import render
from .models import Libro

def listar(request):
    query = request.GET.get('q','')
    if query:
        libros = Libro.objects.filter(titulo__icontains=query)

    else:
        libros = Libro.objects.all()

    return render(request,'listar.html',{
        'libros': libros,
        'query': query
    })


