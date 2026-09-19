import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from .models import Ticket

# PATRÓN DE LA CLASE:
#   1) La vista consulta el modelo (o un servicio externo).
#   2) Guarda lo que obtuvo en un diccionario llamado "contexto".
#   3) Se lo envía al template con render(request, template, contexto).


def lista_tickets(request):
    """Vista 1: consulta el modelo y envía los datos al template por el contexto."""
    tickets = Ticket.objects.all()                    # 1) consumir el modelo
    contexto = {'tickets': tickets}                   # 2) armar el contexto
    return render(request, 'tickets/lista_tickets.html', contexto)  # 3) render()


def detalle_ticket(request, ticket_id):
    """Vista 2: ruta dinámica <int:ticket_id>. get_object_or_404() devuelve
    el ticket o, si no existe, una página 404 (en lugar de un error 500)."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    contexto = {'ticket': ticket}
    return render(request, 'tickets/detalle_ticket.html', contexto)


def tickets_por_estado(request, estado):
    """Vista 3: ruta dinámica <str:estado>. Filtra tickets por su estado."""
    tickets = Ticket.objects.filter(estado=estado)
    contexto = {'tickets': tickets, 'estado': estado}
    return render(request, 'tickets/tickets_por_estado.html', contexto)


def preguntas_frecuentes(request):
    """Vista 4: consume un MICROSERVICIO propio (FastAPI en Render) que a su
    vez lee la información de MongoDB Atlas. Django no toca esa base de datos:
    solo hace una petición HTTP y pasa la respuesta al template por el contexto."""
    faqs = []
    error = None
    try:
        # timeout largo: el plan gratis de Render "duerme" el servicio y
        # la primera petición puede tardar cerca de un minuto en responder.
        respuesta = requests.get(f'{settings.MICROSERVICIO_URL}/faqs', timeout=60)
        respuesta.raise_for_status()
        faqs = respuesta.json()
    except requests.RequestException:
        error = 'No se pudo consultar el microservicio de preguntas frecuentes.'

    contexto = {'faqs': faqs, 'error': error}
    return render(request, 'tickets/preguntas_frecuentes.html', contexto)
