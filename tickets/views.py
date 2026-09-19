import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from .models import Ticket


def lista_tickets(request):
    """Vista 1: consulta el modelo y envía los datos al template por el contexto."""
    tickets = Ticket.objects.all()                    
    contexto = {'tickets': tickets}                   
    return render(request, 'tickets/lista_tickets.html', contexto)  


def detalle_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    contexto = {'ticket': ticket}
    return render(request, 'tickets/detalle_ticket.html', contexto)


def tickets_por_estado(request, estado):
    """Vista 3: ruta dinámica <str:estado>. Filtra tickets por su estado."""
    tickets = Ticket.objects.filter(estado=estado)
    contexto = {'tickets': tickets, 'estado': estado}
    return render(request, 'tickets/tickets_por_estado.html', contexto)


def preguntas_frecuentes(request):
    faqs = []
    error = None
    try:
        respuesta = requests.get(f'{settings.MICROSERVICIO_URL}/faqs', timeout=60)
        respuesta.raise_for_status()
        faqs = respuesta.json()
    except requests.RequestException:
        error = 'No se pudo consultar el microservicio de preguntas frecuentes.'

    contexto = {'faqs': faqs, 'error': error}
    return render(request, 'tickets/preguntas_frecuentes.html', contexto)
