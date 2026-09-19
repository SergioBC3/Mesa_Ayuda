# Mesa de Ayuda (con microservicio)

## Problema que resuelve
Una oficina recibe solicitudes de soporte de forma verbal o por WhatsApp
y las anota en papel: se pierden solicitudes y no se sabe quién las atiende.
Este proyecto las organiza en dos apps: `tickets` y `tecnicos`.

## Qué se agregó en esta entrega
1. **Shortcuts**: todas las vistas usan `render()` y las de detalle usan
   `get_object_or_404()`.
2. **Patrón de la clase** (modelo → vista → contexto → template): cada vista consulta
   el modelo, arma un diccionario `contexto` y se lo envía al template con
   `render(request, template, contexto)`. Ver `tickets/views.py` y `tecnicos/views.py`.
3. **Microservicio propio** (`microservicio/`): API hecha con FastAPI, desplegada en
   Render, que lee las preguntas frecuentes de **MongoDB Atlas**.
   La vista `preguntas_frecuentes` (`/faqs/`) de Django lo consume con `requests`
   y muestra los datos en `tickets/templates/tickets/preguntas_frecuentes.html`.

```
Navegador → Django (vista preguntas_frecuentes) → Microservicio en Render → MongoDB Atlas
```

## Enlaces (completar)
- Repositorio GitHub: https://github.com/TU-USUARIO/TU-REPOSITORIO
- Microservicio en Render: https://TU-SERVICIO.onrender.com  (documentación en `/docs`)

## Cómo ejecutar la app Django
```bash
python -m venv venv
# Windows: venv\Scripts\activate      Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations tecnicos tickets
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- Admin: http://127.0.0.1:8000/admin/ (crea técnicos y tickets)
- Tickets: http://127.0.0.1:8000/
- Preguntas frecuentes (usa el microservicio): http://127.0.0.1:8000/faqs/

Antes de probar `/faqs/`, en `config/settings.py` cambia `MICROSERVICIO_URL`
por la URL de tu servicio en Render.

## Cómo desplegar el microservicio
1. **MongoDB Atlas** (gratis): crea un cluster M0, un usuario de base de datos y en
   *Network Access* agrega `0.0.0.0/0`. Copia la cadena de conexión
   (`mongodb+srv://usuario:clave@cluster.../`).
2. **Render**: New → Web Service → conecta el repositorio de GitHub y configura:
   - Root Directory: `microservicio`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variable: `MONGODB_URI` = tu cadena de conexión
3. Abre `https://TU-SERVICIO.onrender.com/faqs`: debe mostrar el JSON con las FAQs
   (la primera vez se cargan 3 de ejemplo en Mongo).

Nota: en el plan gratis Render "duerme" el servicio; la primera petición puede
tardar cerca de un minuto.

## Subir a GitHub
```bash
git init
git add .
git commit -m "Mesa de ayuda con microservicio"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git push -u origin main
```
