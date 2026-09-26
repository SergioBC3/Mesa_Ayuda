import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from .models import Ticket


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
                respuesta = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': 'openai/gpt-oss-20b',
                        'messages': [
                            {
                                'role': 'system',
                                'content': (
                                    'Eres el asistente virtual de una mesa de ayuda '
                                    'de soporte técnico. Responde en español, de '
                                    'forma breve y clara, preguntas sobre cómo '
                                    'reportar una falla, el estado de los tickets, '
                                    'los técnicos disponibles o consejos básicos de '
                                    'soporte técnico (por ejemplo: internet lento, '
                                    'impresora sin conexión, correo que no llega).'
                                ),
                            },
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