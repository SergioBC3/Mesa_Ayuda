
import threading
import time

import requests
from django.conf import settings

ESTADOS = {'abierto': 'Abierto', 'cerrado': 'Cerrado'}


class ServicioNoDisponible(Exception):
    """Ningun microservicio pudo atender la peticion."""


class TicketNoEncontrado(Exception):
    pass


class DatosInvalidos(Exception):
    pass


# ---------------------------------------------------------------- circuit breaker
_lock = threading.Lock()
_breaker = {'fallos': 0, 'abierto_hasta': 0.0}


def _principal_disponible():
    with _lock:
        return time.monotonic() >= _breaker['abierto_hasta']


def _registrar_exito():
    with _lock:
        _breaker['fallos'] = 0
        _breaker['abierto_hasta'] = 0.0


def _registrar_fallo():
    with _lock:
        _breaker['fallos'] += 1
        if _breaker['fallos'] >= settings.CB_UMBRAL_FALLOS:
            _breaker['abierto_hasta'] = time.monotonic() + settings.CB_SEGUNDOS_ABIERTO


def reiniciar_breaker():
    """Util en pruebas."""
    _registrar_exito()


# ---------------------------------------------------------------- utilidades
def _normalizar(t):
    t = dict(t)
    t['estado_display'] = ESTADOS.get(t.get('estado'), t.get('estado'))
    return t


def _fuentes():
    """Lista ordenada de (nombre, url, timeout)."""
    return [
        ('Python (principal)', settings.URL_LECTURA_PRINCIPAL, settings.TIMEOUT_PRINCIPAL),
        ('Node.js (respaldo)', settings.URL_LECTURA_RESPALDO, settings.TIMEOUT_RESPALDO),
    ]


def _leer(ruta):
    """GET con failover. Devuelve (json, nombre_de_la_fuente_que_respondio)."""
    ultimo_error = None
    for i, (nombre, base, timeout) in enumerate(_fuentes()):
        if not base:
            continue
        es_principal = i == 0
        if es_principal and not _principal_disponible():
            continue  # circuito abierto: ir directo al respaldo
        try:
            r = requests.get(f'{base.rstrip("/")}{ruta}', timeout=timeout)
            if r.status_code == 404:
                
                if es_principal:
                    _registrar_exito()
                raise TicketNoEncontrado()
            r.raise_for_status()
            datos = r.json()
            if es_principal:
                _registrar_exito()
            return datos, nombre
        except TicketNoEncontrado:
            raise
        except (requests.RequestException, ValueError) as e:
            ultimo_error = e
            if es_principal:
                _registrar_fallo()
    raise ServicioNoDisponible(str(ultimo_error) if ultimo_error else 'Sin servicios configurados')


def _escribir(metodo, url, ruta='', **kw):
    if not url:
        raise ServicioNoDisponible('Microservicio no configurado')
    try:
        r = requests.request(metodo, f'{url.rstrip("/")}{ruta}', timeout=settings.TIMEOUT_ESCRITURA, **kw)
    except requests.RequestException as e:
        raise ServicioNoDisponible(str(e))
    if r.status_code == 404:
        raise TicketNoEncontrado()
    if r.status_code in (400, 422):
        try:
            detalle = r.json().get('error') or r.json().get('detail')
        except ValueError:
            detalle = None
        raise DatosInvalidos(str(detalle or 'Datos inválidos'))
    if r.status_code >= 400:
        raise ServicioNoDisponible(f'El microservicio respondió {r.status_code}')
    try:
        return r.json()
    except ValueError:
        return {}


def listar_tickets():
    """Devuelve (lista_de_tickets, nombre_de_la_fuente)."""
    datos, fuente = _leer('/tickets')
    return [_normalizar(t) for t in datos], fuente


def obtener_ticket(ticket_id):
    """Devuelve (ticket, nombre_de_la_fuente). Lanza TicketNoEncontrado."""
    datos, fuente = _leer(f'/tickets/{int(ticket_id)}')
    return _normalizar(datos), fuente


def crear_ticket(datos):
    return _escribir('POST', settings.URL_INSERTAR, '/tickets', json=datos)


def actualizar_ticket(ticket_id, datos):
    return _escribir('PUT', settings.URL_ACTUALIZAR, f'/tickets/{int(ticket_id)}', json=datos)


def eliminar_ticket(ticket_id):
    return _escribir('DELETE', settings.URL_ELIMINAR, f'/tickets/{int(ticket_id)}')
