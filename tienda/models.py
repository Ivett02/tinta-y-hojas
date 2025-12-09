from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver



class Autor(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    foto = models.ImageField(upload_to='autores/', verbose_name="Foto del Autor", null=True, blank=True)
    biografia = models.TextField(verbose_name="Biografía", blank=True)

    def __str__(self):
        return self.nombre

class Coleccion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Colección")
    descripcion = models.TextField(verbose_name="Descripción breve")
    icono = models.CharField(max_length=10, default="📚", verbose_name="Icono (Emoji)")
    color_fondo = models.CharField(max_length=100, default="#800000", verbose_name="Color Hex o CSS")

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    empresa = models.CharField(max_length=100, verbose_name="Nombre Empresa")
    contacto = models.CharField(max_length=100, verbose_name="Nombre Contacto")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")

    def __str__(self):
        return self.empresa



class Libro(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    
    
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros', verbose_name="Autor")
    coleccion = models.ForeignKey(Coleccion, on_delete=models.CASCADE, related_name='libros', verbose_name="Colección/Género")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proveedor")
    
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Stock disponible")
    descripcion = models.TextField(verbose_name="Descripción")
    imagen = models.ImageField(upload_to='libros/', verbose_name="Imagen del libro", null=True, blank=True)
    es_recomendado = models.BooleanField(default=False, verbose_name="¿Es recomendado?")

    def __str__(self):
        return self.titulo



class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección de Envío")
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name="Foto de Perfil")

    def __str__(self):
        return f"Perfil de {self.usuario.username}"



class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    @property
    def subtotal(self):
        return self.libro.precio * self.cantidad



class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Cliente")
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    direccion_envio = models.TextField(verbose_name="Dirección de Envío")
    metodo_pago = models.CharField(max_length=50, verbose_name="Método de Pago", default='tarjeta')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_final = models.DecimalField(max_digits=10, decimal_places=2)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.libro.titulo}"



class Resena(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField(choices=[
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ], verbose_name="Calificación")
    comentario = models.TextField(verbose_name="Tu opinión")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo}"



@receiver(post_save, sender=User)
def crear_datos_usuario(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.create(usuario=instance)
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_datos_usuario(sender, instance, **kwargs):
    instance.perfil.save()