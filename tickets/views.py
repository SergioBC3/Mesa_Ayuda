import requests
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect

from tecnicos.models import Tecnico
from . import servicios
from .forms import TicketForm
from .servicios import (DatosInvalidos, ServicioNoDisponible, TicketNoEncontrado)

MSG_SIN_SERVICIO = ('No se pudo contactar a los microservicios. '
                    'Si es el primer acceso en un rato, espera ~1 minuto y recarga (arranque en frío).')


def _tecnico_por_nombre(nombre):
    return Tecnico.objects.filter(nombre=nombre).first() if nombre else None


def lista_tickets(request):
    tickets, origen, error = [], None, None
    try:
        tickets, origen = servicios.listar_tickets()
    except ServicioNoDisponible:
        error = MSG_SIN_SERVICIO
    contexto = {'tickets': tickets, 'origen': origen, 'error': error}
    return render(request, 'tickets/lista_tickets.html', contexto)


def detalle_ticket(request, ticket_id):
    try:
        ticket, origen = servicios.obtener_ticket(ticket_id)
    except TicketNoEncontrado:
        raise Http404('Ticket no encontrado')
    except ServicioNoDisponible:
        return render(request, 'tickets/detalle_ticket.html', {'error': MSG_SIN_SERVICIO})
    contexto = {'ticket': ticket, 'origen': origen,
                'tecnico': _tecnico_por_nombre(ticket.get('tecnico'))}
    return render(request, 'tickets/detalle_ticket.html', contexto)


def tickets_por_estado(request, estado):
    tickets, origen, error = [], None, None
    try:
        todos, origen = servicios.listar_tickets()
        tickets = [t for t in todos if t['estado'] == estado]
    except ServicioNoDisponible:
        error = MSG_SIN_SERVICIO
    contexto = {'tickets': tickets, 'estado': estado, 'origen': origen, 'error': error}
    return render(request, 'tickets/tickets_por_estado.html', contexto)


def crear_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                servicios.crear_ticket(form.a_payload())
                messages.success(request, 'Ticket creado (microservicio Java).')
                return redirect('tickets:lista_tickets')
            except DatosInvalidos as e:
                form.add_error(None, str(e))
            except ServicioNoDisponible:
                form.add_error(None, MSG_SIN_SERVICIO)
    else:
        form = TicketForm()
    return render(request, 'tickets/formulario_ticket.html',
                  {'form': form, 'titulo_pagina': 'Nuevo ticket'})


def editar_ticket(request, ticket_id):
    try:
        ticket, _ = servicios.obtener_ticket(ticket_id)
    except TicketNoEncontrado:
        raise Http404('Ticket no encontrado')
    except ServicioNoDisponible:
        messages.error(request, MSG_SIN_SERVICIO)
        return redirect('tickets:lista_tickets')

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                servicios.actualizar_ticket(ticket_id, form.a_payload())
                messages.success(request, 'Ticket actualizado (microservicio Go).')
                return redirect('tickets:detalle_ticket', ticket_id=ticket_id)
            except TicketNoEncontrado:
                raise Http404('Ticket no encontrado')
            except DatosInvalidos as e:
                form.add_error(None, str(e))
            except ServicioNoDisponible:
                form.add_error(None, MSG_SIN_SERVICIO)
    else:
        form = TicketForm(initial={
            'titulo': ticket['titulo'],
            'descripcion': ticket['descripcion'],
            'estado': ticket['estado'],
            'tecnico': _tecnico_por_nombre(ticket.get('tecnico')),
        })
    return render(request, 'tickets/formulario_ticket.html',
                  {'form': form, 'titulo_pagina': 'Editar ticket'})


def eliminar_ticket(request, ticket_id):
    try:
        ticket, _ = servicios.obtener_ticket(ticket_id)
    except TicketNoEncontrado:
        raise Http404('Ticket no encontrado')
    except ServicioNoDisponible:
        messages.error(request, MSG_SIN_SERVICIO)
        return redirect('tickets:lista_tickets')

    if request.method == 'POST':
        try:
            servicios.eliminar_ticket(ticket_id)
            messages.success(request, 'Ticket eliminado (microservicio Node.js).')
        except TicketNoEncontrado:
            messages.error(request, 'El ticket ya no existe.')
        except ServicioNoDisponible:
            messages.error(request, MSG_SIN_SERVICIO)
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
            try:
                tickets, _ = servicios.listar_tickets()
            except ServicioNoDisponible:
                tickets = []
            lineas = []
            for t in tickets:
                tecnico_nombre = t.get('tecnico') or 'Sin asignar'
                lineas.append(
                    f'- Ticket #{t["id"]}: "{t["titulo"]}" | Estado: {t["estado_display"]} '
                    f'| Técnico: {tecnico_nombre} | Descripción: {t["descripcion"]}'
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