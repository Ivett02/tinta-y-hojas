from django.contrib import admin
from .models import Libro, Pedido, Carrito, Perfil, ItemPedido, Autor, Coleccion, Resena


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_pedido', 'total_final', 'estado')
    list_filter = ('estado', 'fecha_pedido')
    inlines = [ItemPedidoInline]

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    
    list_display = ('titulo', 'precio', 'stock', 'coleccion') 
    search_fields = ('titulo', 'autor__nombre') 
    list_filter = ('coleccion',) 

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'direccion')

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Coleccion)
class ColeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'icono')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('libro', 'usuario', 'calificacion', 'fecha')

admin.site.register(Carrito)