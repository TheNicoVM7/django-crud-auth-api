from django.http import HttpResponse
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from core.models import Producto, UserActionLog
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


API_URL = 'http://127.0.0.1:8000/api/productos/'

@login_required(login_url='login')
def lista_productos(request):
    response = requests.get(API_URL)
    productos_lista = response.json()

    paginator = Paginator(productos_lista, 5)  # 8 productos por página
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)

    return render(request, 'frontend/productos.html', {
        'productos': productos
    })

@login_required(login_url='login')
def crear_producto(request):
    if request.method == 'POST':
        data = {
            'nombre': request.POST['nombre'],
            'precio': request.POST['precio']
        }

        response = requests.post(API_URL, json=data)

        if response.status_code == 201:
            # Registramos el log
            UserActionLog.objects.create(
                usuario=request.user,
                accion='CREATE',
                descripcion=f"Creó el producto: {request.POST['nombre']} con precio ${request.POST['precio']}"
            )
            messages.success(request, 'Producto creado correctamente')
            return redirect('lista_productos')
        
        messages.error(request, 'Error al crear producto')

        return render(request, 'frontend/crear.html')

    return render(request, 'frontend/crear.html')

@login_required(login_url='login')
def editar_producto(request, id):
    url = f'{API_URL}{id}/'

    if request.method == 'POST':
        data = {
            'nombre': request.POST['nombre'],
            'precio': request.POST['precio']
        }

        response = requests.put(url, json=data)

        if response.status_code == 200:
            UserActionLog.objects.create(
                usuario=request.user,
                accion='UPDATE',
                descripcion=f"Actualizó el producto con ID: {id}"
            )
            messages.info(request, 'Producto actualizado correctamente')
            return redirect('lista_productos')
        
        messages.error(request, 'Error al actualizar producto')

        return render(request, 'frontend/editar.html')

    producto = requests.get(url).json()

    return render(request, 'frontend/editar.html', {
        'p': producto
    })

@login_required(login_url='login')
def eliminar_producto(request, id):
    url = f'{API_URL}{id}/'
    response = requests.delete(url)

    if response.status_code == 204:
        UserActionLog.objects.create(
        usuario=request.user,
        accion='DELETE',
        descripcion=f"Eliminó el producto con ID: {id}"
    )
        messages.warning(request, 'Producto eliminado correctamente')
    else:
        messages.error(request, 'Error al eliminar producto')

    return redirect('lista_productos')

@user_passes_test(lambda u: u.is_staff)
def ver_logs(request):
    query = request.GET.get('q') # Captura el nombre de usuario o descripción
    accion_filtro = request.GET.get('accion') # Captura el tipo de acción (CREATE, UPDATE, DELETE)

    logs_lista = UserActionLog.objects.all().order_by('-fecha')

    # Aplicar filtros si existen
    if query:
        logs_lista = logs_lista.filter(
            Q(usuario__username__icontains=query) | 
            Q(descripcion__icontains=query)
        )
    
    if accion_filtro:
        logs_lista = logs_lista.filter(accion=accion_filtro)

    # Paginación
    paginator = Paginator(logs_lista, 10)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)

    return render(request, 'frontend/logs.html', {
        'logs': logs,
        'query': query,
        'accion_filtro': accion_filtro
    })

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_productos = Producto.objects.count()
    total_usuarios = User.objects.count()
    
    # Lógica para la gráfica: Productos creados en los últimos 7 días
    hoy = timezone.now().date()
    fechas = [(hoy - timedelta(days=i)) for i in range(6, -1, -1)]
    
    # Contamos los logs de tipo 'CREATE' por cada día
    datos_grafica = []
    labels_grafica = []
    
    for fecha in fechas:
        conteo = UserActionLog.objects.filter(
            accion='CREATE', 
            fecha__date=fecha
        ).count()
        datos_grafica.append(conteo)
        labels_grafica.append(fecha.strftime('%d/%m'))

    context = {
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'labels_grafica': labels_grafica,
        'datos_grafica': datos_grafica,
    }
    return render(request, 'frontend/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def exportar_pdf(request):
    # Configuramos la respuesta como un PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_admin.pdf"'

    # Creamos el lienzo (canvas)
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Reporte de Gestión")

    # --- Diseño del PDF ---
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, "REPORTE DE GESTIÓN - PANEL DE CONTROL")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    p.line(100, 720, 500, 720) # Línea divisoria

    # Datos
    total_p = Producto.objects.count()
    total_u = User.objects.count()
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 680, "Resumen General:")
    
    p.setFont("Helvetica", 12)
    p.drawString(120, 650, f"• Total de productos en stock: {total_p}")
    p.drawString(120, 630, f"• Total de usuarios registrados: {total_u}")

    # Pie de página
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(100, 50, "Este documento es un reporte automático generado por el sistema de administración.")

    # Cerramos el PDF
    p.showPage()
    p.save()
    return response

@user_passes_test(lambda u: u.is_staff)
def gestion_usuarios(request):
    usuarios_list = User.objects.all().order_by('-date_joined')
    
    # Paginación (10 usuarios por página)
    paginator = Paginator(usuarios_list, 10)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)
    
    return render(request, 'frontend/gestion_usuarios.html', {'usuarios': usuarios})