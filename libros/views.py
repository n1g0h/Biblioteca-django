from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, F, ExpressionWrapper, FloatField, Q
from django.utils import timezone

from .forms import RegistroUsuarioForm, EmailAuthenticationForm
from .models import Libro, Prestamo, Multa, PerfilUsuario, Reserva, Compra


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('dashboard_usuario')

    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_usuario')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'login.html', {'form': form})


def cerrar_sesion(request):
    logout(request)
    return redirect('login')


def catalogo(request):
    query = request.GET.get('q', '')
    libros = Libro.objects.all()

    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(ISBN__icontains=query)
        )

    context = {
        'libros': libros,
        'query': query
    }
    return render(request, 'catalogo.html', context)


def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()

            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            if 'dni' in form.cleaned_data:
                perfil.dni = form.cleaned_data.get('dni')
            if 'telefono' in form.cleaned_data:
                perfil.telefono = form.cleaned_data.get('telefono', '')
            perfil.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard_usuario')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registro.html', {'form': form})


@login_required
def dashboard_usuario(request):
    usuario = request.user
    hoy = timezone.now().date()

    prestamos_activos = Prestamo.objects.filter(
        usuario=usuario,
        estado__in=['ACTIVO', 'ATRASADO']
    ).select_related('libro')

    multas_pendientes = Multa.objects.filter(
        prestamo__usuario=usuario,
        pagado=False
    ).select_related('prestamo', 'prestamo__libro')

    reservas_activas = Reserva.objects.filter(
        usuario=usuario,
        estado='PENDIENTE'
    ).select_related('libro')

    compras_realizadas = Compra.objects.filter(
        usuario=usuario
    ).select_related('libro').order_by('-fecha_compra')

    context = {
        'prestamos_activos': prestamos_activos,
        'multas_pendientes': multas_pendientes,
        'reservas_activas': reservas_activas,
        'compras_realizadas': compras_realizadas,
        'total_multas': sum(m.monto for m in multas_pendientes),
    }

    return render(request, 'dashboard_usuario.html', context)


@login_required
def reservar_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    reserva_existente = Reserva.objects.filter(usuario=request.user, libro=libro, estado='PENDIENTE').exists()
    
    if reserva_existente:
        messages.warning(request, f"Ya tienes una reserva pendiente para '{libro.titulo}'.")
    else:
        Reserva.objects.create(usuario=request.user, libro=libro, estado='PENDIENTE')
        messages.success(request, f"Has reservado '{libro.titulo}' exitosamente.")

    return redirect('catalogo')


@login_required
def comprar_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if libro.cantidad_disponible > 0:
        # Descuento en el catálogo
        libro.cantidad_disponible -= 1
        if libro.cantidad_total > 0:
            libro.cantidad_total -= 1
        libro.save()

        # Registrar la compra
        Compra.objects.create(
            usuario=request.user,
            libro=libro,
            precio_pagado=libro.precio
        )

        messages.success(request, f"¡Compraste exitosamente '{libro.titulo}' por ${libro.precio}!")
    else:
        messages.error(request, f"No hay unidades disponibles para comprar '{libro.titulo}'.")

    return redirect('catalogo')


@login_required
def devolver_prestamo(request, prestamo_id):
    """Acción para registrar la devolución de un préstamo"""
    prestamo = get_object_or_404(Prestamo, id=prestamo_id, usuario=request.user)
    
    if prestamo.estado != 'DEVUELTO':
        prestamo.estado = 'DEVUELTO'
        prestamo.fecha_devolucion_real = timezone.now().date()
        prestamo.save()

        # Devolver el stock al catálogo
        libro = prestamo.libro
        libro.cantidad_disponible += 1
        libro.save()

        messages.success(request, f"Has devuelto el libro '{libro.titulo}'.")

    return redirect('dashboard_usuario')


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