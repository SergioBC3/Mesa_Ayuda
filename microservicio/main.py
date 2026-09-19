
import os

from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI(title="Microservicio de FAQs - Mesa de Ayuda")

cliente = MongoClient(os.environ["MONGODB_URI"])
coleccion = cliente["mesa_ayuda"]["faqs"]

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


@app.get("/")
def inicio():
    return {"mensaje": "Microservicio de FAQs funcionando. Prueba /faqs o /docs"}


@app.get("/faqs")
def listar_faqs():
    if coleccion.count_documents({}) == 0:
        coleccion.insert_many([dict(f) for f in FAQS_INICIALES])
    return [
        {"id": str(d["_id"]), "pregunta": d["pregunta"], "respuesta": d["respuesta"]}
        for d in coleccion.find()
    ]


@app.post("/faqs")
def crear_faq(faq: Faq):
    resultado = coleccion.insert_one(faq.model_dump())
    return {"id": str(resultado.inserted_id), **faq.model_dump()}
