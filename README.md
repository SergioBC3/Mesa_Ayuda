# Mesa de Ayuda — Proyecto final (Django + microservicios)

Plataforma web en Django para centralizar los requerimientos de soporte técnico (antes dispersos en WhatsApp y
solicitudes verbales). Los **tickets** se gestionan mediante **microservicios** en distintos lenguajes sobre MongoDB Atlas.

## Arquitectura

```
                      ┌────────────────────────────┐
   Navegador ───────► │  App Django (Render)       │
                      │  tickets/servicios.py      │
                      └──┬───────┬───────┬───────┬─┘
        INSERTAR (POST)  │       │       │       │ LEER (GET) con RESILIENCIA
                         ▼       ▼       ▼       ▼
                    ┌──────┐ ┌──────┐ ┌────────┐ ┌─────────────┐   si falla   ┌──────────────┐
                    │ Java │ │  Go  │ │Node.js │ │ Python      │ ───────────► │ Node.js      │
                    │ POST │ │ PUT  │ │ DELETE │ │ (principal) │              │ (respaldo)   │
                    └──┬───┘ └──┬───┘ └───┬────┘ └──────┬──────┘              └──────┬───────┘
                       └────────┴─────────┴─────────────┴────────────────────────────┘
                                        MongoDB Atlas (mesa_ayuda.tickets)
```

| Operación | Lenguaje | Carpeta | Swagger |
|---|---|---|---|
| Inserción | Java (Spring Boot) | `microservicios/ms_insertar_java` | `/swagger-ui.html` |
| Actualización | Go | `microservicios/ms_actualizar_go` | `/docs` |
| Eliminación | Node.js | `microservicios/ms_eliminar_node` | `/api-docs` |
| Lectura principal | Python (FastAPI) | `microservicio` | `/docs` |
| Lectura de respaldo | Node.js | `microservicios/ms_lectura_respaldo_node` | `/api-docs` |

### Resiliencia en la lectura
`tickets/servicios.py` consulta primero el servicio **Python**. Si este falla (caído, timeout o error 5xx) llama
automáticamente al servicio **Node.js** y la página sigue mostrando los datos; en pantalla aparece
*"Datos servidos por el microservicio de lectura: Node.js (respaldo)"*. Además hay un **circuit breaker**: tras 2 fallos
seguidos el principal se salta durante 30 s para no hacer esperar al usuario. Un 404 (ticket inexistente) no cuenta como fallo.

**Cómo demostrarlo** (cualquiera de las dos):
1. En Render, suspende el servicio `mesa-ayuda-lectura-python` y recarga la lista de tickets → aparece "Node.js (respaldo)".
2. Sin suspender nada: `curl -X POST https://<lectura-python>/admin/simular-fallo -H "X-Admin-Token: <ADMIN_TOKEN>" -H "Content-Type: application/json" -d '{"activo": true}'`
   (el `ADMIN_TOKEN` está en las variables de entorno del servicio Python). Usa `{"activo": false}` para restaurarlo.

**Prueba automática** (sin internet ni MongoDB): `python pruebas/prueba_resiliencia.py`

## Despliegue

1. **MongoDB Atlas**: cluster gratis → *Network Access* → permitir `0.0.0.0/0` → copia la cadena `MONGODB_URI`.
2. **GitHub**: sube esta carpeta al repo (`git add . && git commit -m "Proyecto final" && git push`).
   Opcional, un repo por microservicio: `bash scripts_crear_repos.sh TU_USUARIO`.
3. **Render**: *New → Blueprint* y elige el repo (usa `render.yaml`; crea los 6 servicios). Pega `MONGODB_URI` en cada
   microservicio. Con las URLs públicas que Render asigne, completa en `mesa-ayuda-web`:
   `URL_LECTURA_PRINCIPAL`, `URL_LECTURA_RESPALDO`, `URL_INSERTAR` (Java), `URL_ACTUALIZAR` (Go), `URL_ELIMINAR` (Node),
   `MICROSERVICIO_URL` (= la del Python) y `GROQ_API_KEY`.
4. Verifica cada `/health` y Swagger, y luego la app.

> Plan gratis de Render: los servicios se duermen y el primer acceso tarda ~50 s (más el de Java). Abre todos los
> Swagger/`/health` unos minutos antes de la revisión.

## Ejecutar la app Django en local
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # y ajusta las URLs
python manage.py migrate && python manage.py runserver
```

---
PROBLEMATICA
Actualmente las solicitudes y requerimientos de soporte técnico llegan por canales 
informales o no centralizados, principalmente mediante mensajes de WhatsApp y 
solicitudes verbales directas de los usuarios.

Esto puede generar inconvenientes como:
Perdida u olvido de requerimientos pendientes.
Dificultad para hacer seguimiento al estado real de los soportes.
Falta de visibilidad para los técnicos sobre qué tareas tienen activas 
y cuales ya han sido resueltas.
Ausencia de un historial centralizado de atenciones prestadas.

SOLUCIÓN PROPUESTA:
Implementar una plataforma web centralizada en Django que permita a los técnicos:
Registrar manualmente y de forma rápida cualquier requerimiento recibido por WhatsApp o de manera verbal.
Clasificar y visibilizar claramente el estado de cada solicitud.
Consultar un panel central con la lista actualizada de tickets asignados o por atender en tiempo real.
