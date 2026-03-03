from django.urls import path
from .views import lista_productos, crear_producto, editar_producto, eliminar_producto, ver_logs, admin_dashboard, exportar_pdf, gestion_usuarios

urlpatterns = [
    path('productos/', lista_productos, name='lista_productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),
    path('productos/editar/<int:id>/', editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', eliminar_producto, name='eliminar_producto'),
    path('logs/', ver_logs, name='ver_logs'),
    path('panel-admin/', admin_dashboard, name='admin_dashboard'),
    path('exportar-pdf/', exportar_pdf, name='exportar_pdf'),
    path('usuarios/', gestion_usuarios, name='gestion_usuarios'),
]