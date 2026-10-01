from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F, ExpressionWrapper, FloatField
from django.utils import timezone
from .models import Libro, Prestamo, Multa


def listar(request):
    query = request.GET.get('q', '')
    if query:
        libros = Libro.objects.filter(titulo__icontains=query)
    else:
        libros = Libro.objects.all()

    return render(request, 'listar.html', {
        'libros': libros,
        'query': query
    })


@login_required
def dashboard_usuario(request):
    usuario = request.user
    hoy = timezone.now().date()

    prestamos_activos = Prestamo.objects.filter(
        usuario=usuario,
        estado__in=['ACTIVO', 'ATRASADO']
    ).select_related('libro')

    proximas_devoluciones = prestamos_activos.filter(
        fecha_devolucion_esperada__gte=hoy
    ).order_by('fecha_devolucion_esperada')

    multas_pendientes = Multa.objects.filter(
        prestamo__usuario=usuario,
        pagado=False
    ).select_related('prestamo', 'prestamo__libro')

    context = {
        'prestamos_activos': prestamos_activos,
        'proximas_devoluciones': proximas_devoluciones,
        'multas_pendientes': multas_pendientes,
        'total_multas': sum(m.monto for m in multas_pendientes),
    }

    return render(request, 'dashboard_usuario.html', context)


@staff_member_required
def reporte_general(request):
    libros_mas_prestados = Libro.objects.annotate(
        total_prestamos=Count('prestamo')
    ).order_by('-total_prestamos')[:5]

    libros_disponibilidad = Libro.objects.annotate(
        porcentaje_disponible=ExpressionWrapper(
            (F('cantidad_disponible') * 100.0) /
            F('cantidad_total'),
            output_field=FloatField()
        )
    )

    resumen_inventario = Libro.objects.aggregate(
        total=Sum('cantidad_total'),
        disponibles=Sum('cantidad_disponible')
    )

    context = {
        'libros_mas_prestados': libros_mas_prestados,
        'libros_disponibilidad': libros_disponibilidad,
        'resumen_inventario': resumen_inventario,
    }

    return render(request, 'reporte_general.html', context)