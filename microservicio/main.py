"""Microservicio de LECTURA (Python / FastAPI) - Mesa de Ayuda.

Es el servicio PRINCIPAL que consulta los datos. Si falla, Django llama
automaticamente al servicio de respaldo escrito en Node.js
(microservicios/ms_lectura_respaldo_node).

Swagger UI disponible en /docs
"""
import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI(
    title="Microservicio de Lectura (Python) - Mesa de Ayuda",
    description="Consulta de tickets y preguntas frecuentes. Servicio principal de lectura.",
    version="2.0.0",
)

cliente = MongoClient(os.environ["MONGODB_URI"])
bd = cliente[os.environ.get("MONGODB_DB", "mesa_ayuda")]
coleccion = bd["faqs"]
tickets = bd["tickets"]

# Interruptor para DEMOSTRAR la resiliencia: simula que este servicio se cae.
# Se activa con la variable SIMULAR_FALLO=true o con POST /admin/simular-fallo
estado = {"simular_fallo": os.environ.get("SIMULAR_FALLO", "").lower() == "true"}

FAQS_INICIALES = [
    {"pregunta": "¿Cómo creo una solicitud de soporte?",
     "respuesta": "Escribe al equipo de soporte y se registrará un ticket con tu solicitud."},
    {"pregunta": "¿Cómo sé quién atiende mi ticket?",
     "respuesta": "Entra al detalle del ticket: allí aparece el técnico asignado."},
    {"pregunta": "¿Qué significa que un ticket esté cerrado?",
     "respuesta": "Que el problema ya fue resuelto por el técnico asignado."},
]


class Faq(BaseModel):
    pregunta: str
    respuesta: str


class Fallo(BaseModel):
    activo: bool


def ticket_a_json(d):
    return {
        "id": d["_id"],
        "titulo": d.get("titulo", ""),
        "descripcion": d.get("descripcion", ""),
        "estado": d.get("estado", "abierto"),
        "tecnico": d.get("tecnico"),
    }


def verificar_disponible():
    if estado["simular_fallo"]:
        raise HTTPException(status_code=503, detail="Fallo simulado en el servicio Python")


@app.get("/")
def inicio():
    return {"mensaje": "Microservicio de lectura (Python) funcionando. Prueba /tickets o /docs"}


@app.get("/health", tags=["Estado"])
def health():
    verificar_disponible()
    return {"estado": "ok", "servicio": "lectura-python"}


@app.get("/tickets", tags=["Tickets"], summary="Listar todos los tickets")
def listar_tickets():
    verificar_disponible()
    return [ticket_a_json(d) for d in tickets.find().sort("_id", 1)]


@app.get("/tickets/{ticket_id}", tags=["Tickets"], summary="Consultar un ticket por id")
def obtener_ticket(ticket_id: int):
    verificar_disponible()
    d = tickets.find_one({"_id": ticket_id})
    if d is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket_a_json(d)


@app.post("/admin/simular-fallo", tags=["Demostración de resiliencia"],
          summary="Activa/desactiva un fallo simulado (requiere X-Admin-Token)")
def simular_fallo(datos: Fallo, x_admin_token: str = Header(default="")):
    token = os.environ.get("ADMIN_TOKEN", "")
    if not token or x_admin_token != token:
        raise HTTPException(status_code=401, detail="Token de administrador inválido")
    estado["simular_fallo"] = datos.activo
    return {"simular_fallo": estado["simular_fallo"]}


@app.get("/faqs", tags=["FAQs"])
def listar_faqs():
    if coleccion.count_documents({}) == 0:
        coleccion.insert_many([dict(f) for f in FAQS_INICIALES])
    return [
        {"id": str(d["_id"]), "pregunta": d["pregunta"], "respuesta": d["respuesta"]}
        for d in coleccion.find()
    ]


@app.post("/faqs", tags=["FAQs"])
def crear_faq(faq: Faq):
    resultado = coleccion.insert_one(faq.model_dump())
    return {"id": str(resultado.inserted_id), **faq.model_dump()}
