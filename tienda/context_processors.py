from .models import Coleccion

def menu_colecciones(request):
    
    return {'colecciones_menu': Coleccion.objects.all()}