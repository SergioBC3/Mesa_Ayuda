import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket
from .forms import TicketForm


def lista_tickets(request):
    tickets = Ticket.objects.all()
    contexto = {'tickets': tickets}
    return render(request, 'tickets/lista_tickets.html', contexto)


def detalle_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    contexto = {'ticket': ticket}
    return render(request, 'tickets/detalle_ticket.html', contexto)


def tickets_por_estado(request, estado):
    tickets = Ticket.objects.filter(estado=estado)
    contexto = {'tickets': tickets, 'estado': estado}
    return render(request, 'tickets/tickets_por_estado.html', contexto)


def crear_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tickets:lista_tickets')
    else:
        form = TicketForm()
    return render(request, 'tickets/formulario_ticket.html',
                  {'form': form, 'titulo_pagina': 'Nuevo ticket'})


def editar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('tickets:detalle_ticket', ticket_id=ticket.id)
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/formulario_ticket.html',
                  {'form': form, 'titulo_pagina': 'Editar ticket'})


def eliminar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('tickets:lista_tickets')
    return render(request, 'tickets/confirmar_eliminar.html', {'ticket': ticket})


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


def asistente_ia(request):
    pregunta = ''
    respuesta_ia = None
    error = None

    if request.method == 'POST':
        pregunta = request.POST.get('pregunta', '').strip()
        if not pregunta:
            error = 'Escribe una pregunta antes de enviar.'
        elif not settings.GROQ_API_KEY:
            error = 'Falta configurar GROQ_API_KEY en el servidor.'
        else:
            tickets = Ticket.objects.all().select_related('tecnico')
            lineas = []
            for t in tickets:
                tecnico_nombre = t.tecnico.nombre if t.tecnico else 'Sin asignar'
                lineas.append(
                    f'- Ticket #{t.id}: "{t.titulo}" | Estado: {t.get_estado_display()} '
                    f'| Técnico: {tecnico_nombre} | Descripción: {t.descripcion}'
                )
            contexto_bd = '\n'.join(lineas) if lineas else 'No hay tickets registrados.'

            mensaje_sistema = (
                'Eres el asistente virtual de una mesa de ayuda técnico. '
                'Responde en español, de forma breve y clara. '
                'Aquí está la base de datos actual de tickets:\n'
                f'{contexto_bd}\n'
                'Usa esta información para responder preguntas sobre el estado, '
                'técnico asignado o descripción de los tickets. '
                'Si preguntan algo que no está relacionado con los tickets, '
                'responde de todas formas de forma general.'
            )

            try:
                respuesta = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': 'openai/gpt-oss-20b',
                        'messages': [
                            {'role': 'system', 'content': mensaje_sistema},
                            {'role': 'user', 'content': pregunta},
                        ],
                    },
                    timeout=30,
                )
                respuesta.raise_for_status()
                datos = respuesta.json()
                respuesta_ia = datos['choices'][0]['message']['content']
            except requests.RequestException:
                error = 'No se pudo contactar al servicio de IA. Intenta de nuevo.'
            except (KeyError, IndexError):
                error = 'La IA respondió en un formato inesperado.'

    contexto = {'pregunta': pregunta, 'respuesta_ia': respuesta_ia, 'error': error}
    return render(request, 'tickets/asistente_ia.html', contexto)