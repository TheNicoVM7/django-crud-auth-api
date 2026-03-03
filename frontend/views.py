import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from core.models import UserActionLog
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

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