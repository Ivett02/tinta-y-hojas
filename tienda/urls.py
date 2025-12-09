from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- 1. PÁGINAS PÚBLICAS ---
    path('', views.index, name='index'),
    path('libros/', views.catalogo, name='catalogo'),
    path('libro/<int:libro_id>/', views.detalle_libro, name='detalle_libro'),
    
    path('autores/', views.lista_autores, name='lista_autores'),
    path('autor/<int:autor_id>/', views.detalle_autor, name='detalle_autor'),
    
    path('colecciones/', views.lista_generos, name='lista_generos'),
    path('resenas/', views.resenas, name='resenas'),

    # --- 2. USUARIO Y SESIÓN ---
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mi-cuenta/', views.mi_perfil, name='mi_perfil'),

    # --- 3. CARRITO DE COMPRAS ---
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:libro_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/sumar/<int:item_id>/', views.sumar_cantidad, name='sumar_cantidad'),
    path('carrito/restar/<int:item_id>/', views.restar_cantidad, name='restar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.procesar_pedido, name='procesar_pedido'),
    path('pedido-confirmado/<int:pedido_id>/', views.pedido_exitoso, name='pedido_exitoso'),

    # --- 4. PANEL DE ADMINISTRACIÓN ---
    path('panel-admin/', views.dashboard_admin, name='dashboard_admin'),

    # --- 5. CRUD: LIBROS ---
    path('libro/crear/', views.crear_libro, name='crear_libro'),
    path('libro/editar/<int:libro_id>/', views.editar_libro, name='editar_libro'),
    path('libro/eliminar/<int:libro_id>/', views.eliminar_libro, name='eliminar_libro'),

    # --- 6. CRUD: AUTORES ---
    path('autor/crear/', views.crear_autor, name='crear_autor'),
    path('autor/editar/<int:autor_id>/', views.editar_autor, name='editar_autor'),
    path('autor/eliminar/<int:autor_id>/', views.eliminar_autor, name='eliminar_autor'),

    # --- 7. CRUD: COLECCIONES ---
    path('coleccion/crear/', views.crear_coleccion, name='crear_coleccion'),
    path('coleccion/editar/<int:coleccion_id>/', views.editar_coleccion, name='editar_coleccion'),
    path('coleccion/eliminar/<int:coleccion_id>/', views.eliminar_coleccion, name='eliminar_coleccion'),

    # --- 8. CRUD: PROVEEDORES ---
    path('proveedor/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedor/editar/<int:proveedor_id>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedor/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    # --- 9. CRUD: PEDIDOS (ADMIN) ---
    path('pedido/crear-admin/', views.crear_pedido_admin, name='crear_pedido_admin'),
    path('pedido/estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('pedido/editar-admin/<int:pedido_id>/', views.editar_pedido_completo, name='editar_pedido_completo'),
    path('pedido/detalle/<int:pedido_id>/', views.detalle_pedido_admin, name='detalle_pedido_admin'),
    path('pedido/eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),

    # --- 10. CRUD: USUARIOS (ADMIN) ---
    path('usuario/crear-admin/', views.crear_usuario_admin, name='crear_usuario_admin'),
    path('usuario/editar-admin/<int:user_id>/', views.editar_usuario_admin, name='editar_usuario_admin'),
    path('usuario/perfil/<int:user_id>/', views.ver_perfil_usuario, name='ver_perfil_usuario'),
    path('usuario/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # --- 11. CRUD: RESEÑAS (ADMIN) ---
    path('resena/crear-admin/', views.crear_resena_admin, name='crear_resena_admin'),
    path('resena/editar-admin/<int:resena_id>/', views.editar_resena_admin, name='editar_resena_admin'),
    path('resena/eliminar/<int:resena_id>/', views.eliminar_resena, name='eliminar_resena'),
]

# Configuración para servir imágenes en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)