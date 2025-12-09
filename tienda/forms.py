from django import forms
from .models import Libro, Autor, Resena, Perfil, Coleccion, Pedido, Proveedor
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ColeccionForm(forms.ModelForm):
    class Meta:
        model = Coleccion
        fields = '__all__'
        widgets = {
            'color_fondo': forms.TextInput(attrs={'type': 'color'}), 
        }

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = '__all__'
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = '__all__'
        widgets = {'biografia': forms.Textarea(attrs={'rows': 4})}


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': '¿Qué te pareció el libro?'}),
        }


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico") 

    class Meta:
        model = User
        fields = ['username', 'email'] 
        help_texts = {
            'username': None, 
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'foto']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }

class PedidoAdminForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion_envio', 'estado', 'total_final', 'metodo_pago']
        widgets = {
            'direccion_envio': forms.Textarea(attrs={'rows': 3}),
        }

class UsuarioAdminForm(forms.ModelForm):
    is_staff = forms.BooleanField(label="Es Administrador (Staff)", required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']




class ResenaAdminForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = '__all__' 
        widgets = {'comentario': forms.Textarea(attrs={'rows': 3})}

class PedidoCrearForm(forms.ModelForm):
    
    class Meta:
        model = Pedido
        fields = ['usuario', 'direccion_envio', 'metodo_pago', 'total_final', 'estado']
        widgets = {'direccion_envio': forms.Textarea(attrs={'rows': 2})}


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'