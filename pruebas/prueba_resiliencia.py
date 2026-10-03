"""Prueba de RESILIENCIA del cliente de lectura (tickets/servicios.py).

No necesita Django instalado, ni internet, ni MongoDB: levanta servicios falsos
en local (http.server) y comprueba que:
  1. Con el principal sano, los datos vienen del principal (Python).
  2. Si el principal falla, los datos vienen del respaldo (Node.js).
  3. Tras varios fallos el circuit breaker salta el principal sin esperar.
  4. Si el principal se recupera y el circuito se cierra, vuelve a usarse.
  5. Si ambos fallan se lanza ServicioNoDisponible.
  6. Un 404 NO se trata como fallo (no activa el respaldo).

Uso:   python pruebas/prueba_resiliencia.py
"""
import importlib.util
import json
import os
import sys
import threading
import time
import types
from http.server import BaseHTTPRequestHandler, HTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- configuracion falsa (en vez de django.conf.settings) ------------------
cfg = types.SimpleNamespace(
    URL_LECTURA_PRINCIPAL='', URL_LECTURA_RESPALDO='',
    URL_INSERTAR='', URL_ACTUALIZAR='', URL_ELIMINAR='',
    TIMEOUT_PRINCIPAL=1.0, TIMEOUT_RESPALDO=2.0, TIMEOUT_ESCRITURA=2.0,
    CB_UMBRAL_FALLOS=2, CB_SEGUNDOS_ABIERTO=1.5,
)
django = types.ModuleType('django')
conf = types.ModuleType('django.conf')
conf.settings = cfg
sys.modules['django'] = django
sys.modules['django.conf'] = conf

spec = importlib.util.spec_from_file_location('servicios', os.path.join(RAIZ, 'tickets', 'servicios.py'))
servicios = importlib.util.module_from_spec(spec)
spec.loader.exec_module(servicios)


# --- servicios falsos -----------------------------------------------------
def crear_servicio(nombre):
    estado = {'caido': False, 'llamadas': 0}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            estado['llamadas'] += 1
            if estado['caido']:
                self.send_response(503); self.end_headers(); return
            if self.path == '/tickets':
                cuerpo = [{'id': 1, 'titulo': f'Ticket desde {nombre}', 'descripcion': 'x',
                           'estado': 'abierto', 'tecnico': None}]
            elif self.path == '/tickets/1':
                cuerpo = {'id': 1, 'titulo': f'Ticket desde {nombre}', 'descripcion': 'x',
                          'estado': 'abierto', 'tecnico': None}
            else:
                self.send_response(404); self.end_headers(); return
            datos = json.dumps(cuerpo).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)

    srv = HTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, estado


srv_p, est_p = crear_servicio('PYTHON')
srv_r, est_r = crear_servicio('NODE')
cfg.URL_LECTURA_PRINCIPAL = f'http://127.0.0.1:{srv_p.server_port}'
cfg.URL_LECTURA_RESPALDO = f'http://127.0.0.1:{srv_r.server_port}'

fallos = []


def comprobar(cond, texto):
    print(('OK   ' if cond else 'FALLA'), texto)
    if not cond:
        fallos.append(texto)


# 1. principal sano
servicios.reiniciar_breaker()
t, fuente = servicios.listar_tickets()
comprobar('Python' in fuente and 'PYTHON' in t[0]['titulo'], '1. principal sano -> responde Python')

# 2. principal caido -> respaldo
est_p['caido'] = True
t, fuente = servicios.listar_tickets()
comprobar('Node' in fuente and 'NODE' in t[0]['titulo'], '2. principal caido -> responde Node.js (respaldo)')

# 3. circuit breaker abierto tras 2 fallos: no vuelve a tocar el principal
servicios.listar_tickets()  # segundo fallo -> abre el circuito
antes = est_p['llamadas']
servicios.listar_tickets()
comprobar(est_p['llamadas'] == antes, '3. circuit breaker abierto -> el principal ya no se consulta')

# 4. recuperacion
est_p['caido'] = False
time.sleep(1.7)  # vence CB_SEGUNDOS_ABIERTO
t, fuente = servicios.listar_tickets()
comprobar('Python' in fuente, '4. principal recuperado -> vuelve a usarse Python')

# 5. ambos caidos
est_p['caido'] = est_r['caido'] = True
servicios.reiniciar_breaker()
try:
    servicios.listar_tickets()
    comprobar(False, '5. ambos caidos -> ServicioNoDisponible')
except servicios.ServicioNoDisponible:
    comprobar(True, '5. ambos caidos -> ServicioNoDisponible')

# 6. 404 no es fallo
est_p['caido'] = est_r['caido'] = False
servicios.reiniciar_breaker()
antes_r = est_r['llamadas']
try:
    servicios.obtener_ticket(99)
    comprobar(False, '6. 404 -> TicketNoEncontrado')
except servicios.TicketNoEncontrado:
    comprobar(est_r['llamadas'] == antes_r, '6. 404 -> TicketNoEncontrado sin usar el respaldo')

# 7. detalle tambien tiene failover
est_p['caido'] = True
servicios.reiniciar_breaker()
t, fuente = servicios.obtener_ticket(1)
comprobar('Node' in fuente, '7. detalle de ticket tambien usa el respaldo')

print()
print('TODAS LAS PRUEBAS PASARON' if not fallos else f'{len(fallos)} PRUEBA(S) FALLARON')
sys.exit(1 if fallos else 0)
