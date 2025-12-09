from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

# IMPORTACIÓN DE TODOS LOS MODELOS
from .models import Libro, Carrito, ItemCarrito, Pedido, ItemPedido, Perfil, Autor, Coleccion, Resena, Proveedor

# IMPORTACIÓN DE TODOS LOS FORMULARIOS
from .forms import (
    LibroForm, AutorForm, ColeccionForm, ResenaForm, RegistroForm, PerfilForm,
    PedidoAdminForm, UsuarioAdminForm, ResenaAdminForm, PedidoCrearForm, ProveedorForm
)

# ==========================================
# 1. VISTAS PÚBLICAS (CLIENTE)
# ==========================================

def index(request):
    recomendados = Libro.objects.filter(es_recomendado=True)[:4]
    novedades = Libro.objects.all().order_by('-id')[:4]
    return render(request, 'tienda/index.html', {
        'recomendados': recomendados,
        'novedades': novedades
    })

def catalogo(request):
    libros = Libro.objects.all()
    colecciones = Coleccion.objects.all()
    
    coleccion_id = request.GET.get('coleccion')
    if coleccion_id:
        libros = libros.filter(coleccion__id=coleccion_id)
        
    if request.GET.get('recomendados'):
        libros = libros.filter(es_recomendado=True)

    return render(request, 'tienda/catalogo.html', {
        'libros': libros, 
        'colecciones': colecciones
    })

def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    resenas = libro.resenas.all().order_by('-fecha')
    
    puede_comentar = False
    ya_comento = False
    
    if request.user.is_authenticated:
        compro_libro = ItemPedido.objects.filter(pedido__usuario=request.user, libro=libro).exists()
        ya_comento = Resena.objects.filter(usuario=request.user, libro=libro).exists()
        if compro_libro and not ya_comento:
            puede_comentar = True

    if request.method == 'POST' and puede_comentar:
        form = ResenaForm(request.POST)
        if form.is_valid():
            nueva_resena = form.save(commit=False)
            nueva_resena.libro = libro
            nueva_resena.usuario = request.user
            nueva_resena.save()
            messages.success(request, "¡Gracias por tu reseña!")
            return redirect('detalle_libro', libro_id=libro.id)
    else:
        form = ResenaForm()

    return render(request, 'tienda/detalle_libro.html', {
        'libro': libro,
        'resenas': resenas,
        'puede_comentar': puede_comentar,
        'ya_comento': ya_comento,
        'form': form
    })



def lista_autores(request):
    autores = Autor.objects.all().order_by('nombre')
    return render(request, 'tienda/autores.html', {'autores': autores})

def detalle_autor(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)
    libros = autor.libros.all()
    return render(request, 'tienda/detalle_autor.html', {'autor': autor, 'libros': libros})

def lista_generos(request):
    colecciones = Coleccion.objects.all()
    return render(request, 'tienda/generos.html', {'colecciones': colecciones})

def resenas(request):
    
    lista_resenas = Resena.objects.all().order_by('-fecha')
    libros = Libro.objects.all().order_by('titulo')
    autores = Autor.objects.all().order_by('nombre')
    colecciones = Coleccion.objects.all().order_by('nombre')

    if request.GET.get('libro'):
        lista_resenas = lista_resenas.filter(libro_id=request.GET.get('libro'))
    if request.GET.get('autor'):
        lista_resenas = lista_resenas.filter(libro__autor_id=request.GET.get('autor'))
    if request.GET.get('coleccion'):
        lista_resenas = lista_resenas.filter(libro__coleccion_id=request.GET.get('coleccion'))

    return render(request, 'tienda/resenas.html', {
        'resenas': lista_resenas,
        'libros': libros,
        'autores': autores,
        'colecciones': colecciones
    })


# ==========================================
# 2. AUTENTICACIÓN Y PERFIL
# ==========================================

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido/a {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Error en el registro.")
    else:
        form = RegistroForm()
    return render(request, 'tienda/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'tienda/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect('index')

@login_required(login_url='login')
def mi_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect('mi_perfil')
    else:
        form = PerfilForm(instance=perfil)
    
    mis_pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    return render(request, 'tienda/mi_perfil.html', {'form': form, 'pedidos': mis_pedidos})


# ==========================================
# 3. CARRITO Y CHECKOUT
# ==========================================

def agregar_al_carrito(request, libro_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para comprar.")
        return redirect('login')

    libro = get_object_or_404(Libro, id=libro_id)
    if libro.stock <= 0:
        messages.error(request, "Producto agotado.")
        return redirect('catalogo')

    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, libro=libro)
    
    if not created:
        item.cantidad += 1
        item.save()
        messages.success(request, f"Se agregó otra unidad de {libro.titulo}.")
    else:
        messages.success(request, f"¡{libro.titulo} agregado al carrito!")
        
    return redirect('catalogo')

@login_required(login_url='login')
def ver_carrito(request):
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        items = carrito.items.all()
    except Carrito.DoesNotExist:
        items = []
        carrito = None
    return render(request, 'tienda/carrito.html', {'carrito': carrito, 'items': items})

@login_required(login_url='login')
def restar_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if item.carrito.usuario == request.user:
        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
        else:
            item.delete()
    return redirect('ver_carrito')

@login_required(login_url='login')
def sumar_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if item.carrito.usuario == request.user:
        if item.cantidad < item.libro.stock:
            item.cantidad += 1
            item.save()
        else:
            messages.warning(request, "No hay más stock disponible.")
    return redirect('ver_carrito')

@login_required(login_url='login')
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if item.carrito.usuario == request.user:
        item.delete()
    return redirect('ver_carrito')

@login_required(login_url='login')
def procesar_pedido(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all()
    
    if not items:
        return redirect('catalogo')

    subtotal = carrito.total
    tasa_impuesto = Decimal('0.16')
    monto_impuestos = subtotal * tasa_impuesto
    total_a_pagar = subtotal + monto_impuestos

    if request.method == 'POST':
        for item in items:
            if item.cantidad > item.libro.stock:
                messages.error(request, f"No hay suficiente stock de {item.libro.titulo}.")
                return redirect('ver_carrito')

        nuevo_pedido = Pedido.objects.create(
            usuario=request.user,
            direccion_envio=request.POST.get('direccion'),
            metodo_pago=request.POST.get('metodo_pago'),
            subtotal=subtotal,
            impuestos=monto_impuestos,
            total_final=total_a_pagar,
            estado='pagado'
        )

        for item in items:
            ItemPedido.objects.create(
                pedido=nuevo_pedido,
                libro=item.libro,
                cantidad=item.cantidad,
                precio_unitario=item.libro.precio
            )
            item.libro.stock -= item.cantidad
            item.libro.save()

        items.delete() 
        return redirect('pedido_exitoso', pedido_id=nuevo_pedido.id)

    return render(request, 'tienda/checkout.html', {
        'subtotal': subtotal, 
        'impuestos': monto_impuestos, 
        'total': total_a_pagar
    })

@login_required(login_url='login')
def pedido_exitoso(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Seguridad: solo el dueño puede ver su recibo
    if pedido.usuario != request.user:
        messages.error(request, "No tienes permiso para ver este pedido.")
        return redirect('index')
    return render(request, 'tienda/pedido_exitoso.html', {'pedido': pedido})


# ==========================================
# 4. PANEL ADMIN Y DASHBOARD
# ==========================================

def es_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(es_admin, login_url='index')
def dashboard_admin(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    usuarios = User.objects.filter(is_superuser=False)
    libros = Libro.objects.all().order_by('titulo')
    autores = Autor.objects.all().order_by('nombre')
    colecciones = Coleccion.objects.all()
    proveedores = Proveedor.objects.all().order_by('empresa')
    
    # Lógica de filtrado de reseñas en el Admin
    resenas = Resena.objects.all().order_by('-fecha')
    if request.GET.get('filtro_libro'):
        resenas = resenas.filter(libro_id=request.GET.get('filtro_libro'))
    if request.GET.get('filtro_autor'):
        resenas = resenas.filter(libro__autor_id=request.GET.get('filtro_autor'))
    if request.GET.get('filtro_coleccion'):
        resenas = resenas.filter(libro__coleccion_id=request.GET.get('filtro_coleccion'))

    return render(request, 'tienda/dashboard.html', {
        'pedidos': pedidos, 
        'usuarios': usuarios,
        'libros': libros,
        'autores': autores,
        'colecciones': colecciones,
        'resenas': resenas,
        'proveedores': proveedores
    })


# ==========================================
# 5. CRUD: PEDIDOS (ADMIN)
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_pedido_admin(request):
    if request.method == 'POST':
        form = PedidoCrearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido creado manualmente.")
            return redirect('dashboard_admin')
    else:
        form = PedidoCrearForm()
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': 'Nuevo Pedido Manual'})

@user_passes_test(es_admin, login_url='index')
def cambiar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = request.POST.get('nuevo_estado')
        pedido.save()
        messages.success(request, "Estado actualizado.")
    return redirect('dashboard_admin')

@user_passes_test(es_admin, login_url='index')
def editar_pedido_completo(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = PedidoAdminForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f"Pedido #{pedido.id} actualizado.")
            return redirect('dashboard_admin')
    else:
        form = PedidoAdminForm(instance=pedido)
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': f'Editar Pedido #{pedido.id}'})

@user_passes_test(es_admin, login_url='index')
def detalle_pedido_admin(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = pedido.items.all()
    return render(request, 'tienda/detalle_pedido_admin.html', {'pedido': pedido, 'items': items})

@user_passes_test(es_admin, login_url='index')
def eliminar_pedido(request, pedido_id):
    obj = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Pedido eliminado.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Pedido', 'nombre': f"#{obj.id}"})


# ==========================================
# 6. CRUD: USUARIOS (ADMIN)
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_usuario_admin(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect('dashboard_admin')
    else:
        form = RegistroForm()
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': 'Nuevo Usuario'})

@user_passes_test(es_admin, login_url='index')
def editar_usuario_admin(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UsuarioAdminForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario {usuario.username} actualizado.")
            return redirect('dashboard_admin')
    else:
        form = UsuarioAdminForm(instance=usuario)
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': f'Editar {usuario.username}'})

@user_passes_test(es_admin, login_url='index')
def eliminar_usuario(request, user_id):
    obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if not obj.is_superuser:
            obj.delete()
            messages.success(request, "Usuario eliminado.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Usuario', 'nombre': obj.username})

@user_passes_test(es_admin, login_url='index')
def ver_perfil_usuario(request, user_id):
    usuario_ver = get_object_or_404(User, id=user_id)
    pedidos_usuario = Pedido.objects.filter(usuario=usuario_ver).order_by('-fecha_pedido')
    return render(request, 'tienda/perfil_usuario.html', {
        'usuario_ver': usuario_ver,
        'pedidos_usuario': pedidos_usuario
    })


# ==========================================
# 7. CRUD: INVENTARIO / LIBROS
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = LibroForm()
    return render(request, 'tienda/libro_form.html', {'form': form, 'titulo': 'Nuevo Libro'})

@user_passes_test(es_admin, login_url='index')
def editar_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = LibroForm(instance=libro)
    return render(request, 'tienda/libro_form.html', {'form': form, 'titulo': f'Editar {libro.titulo}'})

@user_passes_test(es_admin, login_url='index')
def eliminar_libro(request, libro_id):
    obj = get_object_or_404(Libro, id=libro_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Libro eliminado.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Libro', 'nombre': obj.titulo})


# ==========================================
# 8. CRUD: AUTORES
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_autor(request):
    if request.method == 'POST':
        form = AutorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = AutorForm()
    return render(request, 'tienda/autor_form.html', {'form': form, 'titulo': 'Nuevo Autor'})

@user_passes_test(es_admin, login_url='index')
def editar_autor(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)
    if request.method == 'POST':
        form = AutorForm(request.POST, request.FILES, instance=autor)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = AutorForm(instance=autor)
    return render(request, 'tienda/autor_form.html', {'form': form, 'titulo': 'Editar Autor'})

@user_passes_test(es_admin, login_url='index')
def eliminar_autor(request, autor_id):
    obj = get_object_or_404(Autor, id=autor_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Autor eliminado.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Autor', 'nombre': obj.nombre})


# ==========================================
# 9. CRUD: COLECCIONES
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_coleccion(request):
    if request.method == 'POST':
        form = ColeccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = ColeccionForm()
    return render(request, 'tienda/coleccion_form.html', {'form': form, 'titulo': 'Nueva Colección'})

@user_passes_test(es_admin, login_url='index')
def editar_coleccion(request, coleccion_id):
    col = get_object_or_404(Coleccion, id=coleccion_id)
    if request.method == 'POST':
        form = ColeccionForm(request.POST, instance=col)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = ColeccionForm(instance=col)
    return render(request, 'tienda/coleccion_form.html', {'form': form, 'titulo': 'Editar Colección'})

@user_passes_test(es_admin, login_url='index')
def eliminar_coleccion(request, coleccion_id):
    obj = get_object_or_404(Coleccion, id=coleccion_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Colección eliminada.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Colección', 'nombre': obj.nombre})


# ==========================================
# 10. CRUD: PROVEEDORES
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor registrado.")
            return redirect('dashboard_admin')
    else:
        form = ProveedorForm()
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': 'Nuevo Proveedor'})

@user_passes_test(es_admin, login_url='index')
def editar_proveedor(request, proveedor_id):
    prov = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=prov)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado.")
            return redirect('dashboard_admin')
    else:
        form = ProveedorForm(instance=prov)
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': 'Editar Proveedor'})

@user_passes_test(es_admin, login_url='index')
def eliminar_proveedor(request, proveedor_id):
    obj = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Proveedor eliminado.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Proveedor', 'nombre': obj.empresa})


# ==========================================
# 11. CRUD: RESEÑAS (ADMIN)
# ==========================================

@user_passes_test(es_admin, login_url='index')
def crear_resena_admin(request):
    if request.method == 'POST':
        form = ResenaAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña creada.")
            return redirect('dashboard_admin')
    else:
        form = ResenaAdminForm()
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': 'Nueva Reseña'})

@user_passes_test(es_admin, login_url='index')
def editar_resena_admin(request, resena_id):
    obj = get_object_or_404(Resena, id=resena_id)
    if request.method == 'POST':
        form = ResenaAdminForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña actualizada.")
            return redirect('dashboard_admin')
    else:
        form = ResenaAdminForm(instance=obj)
    return render(request, 'tienda/form_admin_generico.html', {'form': form, 'titulo': 'Editar Reseña'})

@user_passes_test(es_admin, login_url='index')
def eliminar_resena(request, resena_id):
    obj = get_object_or_404(Resena, id=resena_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Reseña eliminada.")
        return redirect('dashboard_admin')
    return render(request, 'tienda/confirmar_eliminar.html', {'obj': obj, 'tipo': 'Reseña', 'nombre': f"de {obj.usuario.username}"})