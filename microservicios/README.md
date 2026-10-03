# Microservicios de Mesa de Ayuda

| Carpeta | Operación | Lenguaje | Endpoint | Swagger |
|---|---|---|---|---|
| `../microservicio` | **Lectura principal** | Python (FastAPI) | `GET /tickets`, `GET /tickets/{id}` | `/docs` |
| `ms_lectura_respaldo_node` | **Lectura de respaldo** | Node.js (Express) | `GET /tickets`, `GET /tickets/{id}` | `/api-docs` |
| `ms_insertar_java` | **Inserción** | Java 17 (Spring Boot) | `POST /tickets` | `/swagger-ui.html` |
| `ms_actualizar_go` | **Actualización** | Go | `PUT /tickets/{id}` | `/docs` |
| `ms_eliminar_node` | **Eliminación** | Node.js (Express) | `DELETE /tickets/{id}` | `/api-docs` |

Todos usan la misma base MongoDB Atlas (`mesa_ayuda`, colección `tickets`) y la variable `MONGODB_URI`.
Formato de un ticket: `{ "id": 1, "titulo": "...", "descripcion": "...", "estado": "abierto|cerrado", "tecnico": "Nombre" | null }`.

## Ejecutar en local (cada uno en una terminal)
```bash
export MONGODB_URI="mongodb+srv://usuario:clave@cluster.mongodb.net/"

# Python (lectura principal)   -> http://localhost:8001/docs
cd microservicio && pip install -r requirements.txt && uvicorn main:app --port 8001

# Node.js (respaldo)           -> http://localhost:3001/api-docs
cd microservicios/ms_lectura_respaldo_node && npm install && PORT=3001 npm start

# Node.js (eliminar)           -> http://localhost:3000/api-docs
cd microservicios/ms_eliminar_node && npm install && PORT=3000 npm start

# Go (actualizar)              -> http://localhost:8000/docs
cd microservicios/ms_actualizar_go && go mod tidy && PORT=8000 go run .

# Java (insertar)              -> http://localhost:8080/swagger-ui.html
cd microservicios/ms_insertar_java && mvn spring-boot:run
```
