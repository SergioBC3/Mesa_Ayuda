from django.shortcuts import render, get_object_or_404

from .models import Tecnico


def lista_tecnicos(request):
    """Vista 1: consulta el modelo y envía los datos al template por el contexto."""
    tecnicos = Tecnico.objects.all()                  
    contexto = {'tecnicos': tecnicos}                 
    return render(request, 'tecnicos/lista_tecnicos.html', contexto)  


def detalle_tecnico(request, tecnico_id):
    """Vista 2: ruta dinámica <int:tecnico_id>. get_object_or_404() devuelve el
    técnico o una página 404; luego se consultan sus tickets por la relación."""
    tecnico = get_object_or_404(Tecnico, pk=tecnico_id)
    tickets = tecnico.tickets.all()
    contexto = {'tecnico': tecnico, 'tickets': tickets}
    return render(request, 'tecnicos/detalle_tecnico.html', contexto)
