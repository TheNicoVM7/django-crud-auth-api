from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username} 👋')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión 👌')
            return redirect('login')
        else:
            messages.error(request, 'Corrige los errores del formulario')

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})