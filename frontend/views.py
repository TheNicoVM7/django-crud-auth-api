import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

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
        messages.warning(request, 'Producto eliminado correctamente')
    else:
        messages.error(request, 'Error al eliminar producto')

    return redirect('lista_productos')