// Microservicio de ACTUALIZACION (Go) - Mesa de Ayuda.
// Swagger UI en /docs, especificacion OpenAPI en /openapi.json
package main

import (
	"context"
	_ "embed"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

//go:embed openapi.json
var openapiJSON []byte

const swaggerHTML = `<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Swagger - Actualizar (Go)</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"></head>
<body><div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>window.ui = SwaggerUIBundle({url: '/openapi.json', dom_id: '#swagger-ui'});</script>
</body></html>`

type ticketEntrada struct {
	Titulo      string  `json:"titulo"`
	Descripcion string  `json:"descripcion"`
	Estado      string  `json:"estado"`
	Tecnico     *string `json:"tecnico"`
}

type ticketSalida struct {
	ID          int64   `json:"id"`
	Titulo      string  `json:"titulo"`
	Descripcion string  `json:"descripcion"`
	Estado      string  `json:"estado"`
	Tecnico     *string `json:"tecnico"`
}

type ticketDoc struct {
	ID          int64   `bson:"_id"`
	Titulo      string  `bson:"titulo"`
	Descripcion string  `bson:"descripcion"`
	Estado      string  `bson:"estado"`
	Tecnico     *string `bson:"tecnico"`
}

var tickets *mongo.Collection

func responderJSON(w http.ResponseWriter, codigo int, cuerpo any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(codigo)
	_ = json.NewEncoder(w).Encode(cuerpo)
}

func actualizar(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil {
		responderJSON(w, 400, map[string]string{"error": "id inválido"})
		return
	}
	var in ticketEntrada
	if err := json.NewDecoder(r.Body).Decode(&in); err != nil {
		responderJSON(w, 400, map[string]string{"error": "JSON inválido"})
		return
	}
	in.Titulo = strings.TrimSpace(in.Titulo)
	in.Descripcion = strings.TrimSpace(in.Descripcion)
	if in.Estado == "" {
		in.Estado = "abierto"
	}
	if in.Titulo == "" || in.Descripcion == "" {
		responderJSON(w, 400, map[string]string{"error": "titulo y descripcion son obligatorios"})
		return
	}
	if in.Estado != "abierto" && in.Estado != "cerrado" {
		responderJSON(w, 400, map[string]string{"error": "estado debe ser 'abierto' o 'cerrado'"})
		return
	}
	if in.Tecnico != nil && strings.TrimSpace(*in.Tecnico) == "" {
		in.Tecnico = nil
	}

	ctx, cancel := context.WithTimeout(r.Context(), 15*time.Second)
	defer cancel()

	cambios := bson.M{"$set": bson.M{
		"titulo":      in.Titulo,
		"descripcion": in.Descripcion,
		"estado":      in.Estado,
		"tecnico":     in.Tecnico,
	}}
	var doc ticketDoc
	err = tickets.FindOneAndUpdate(ctx, bson.M{"_id": id}, cambios,
		options.FindOneAndUpdate().SetReturnDocument(options.After)).Decode(&doc)
	if err == mongo.ErrNoDocuments {
		responderJSON(w, 404, map[string]string{"error": "Ticket no encontrado"})
		return
	}
	if err != nil {
		log.Println("error actualizando:", err)
		responderJSON(w, 500, map[string]string{"error": "Error actualizando en la base de datos"})
		return
	}
	responderJSON(w, 200, ticketSalida{doc.ID, doc.Titulo, doc.Descripcion, doc.Estado, doc.Tecnico})
}

func main() {
	uri := os.Getenv("MONGODB_URI")
	if uri == "" {
		log.Fatal("Falta la variable de entorno MONGODB_URI")
	}
	nombreBD := os.Getenv("MONGODB_DB")
	if nombreBD == "" {
		nombreBD = "mesa_ayuda"
	}
	puerto := os.Getenv("PORT")
	if puerto == "" {
		puerto = "8000"
	}

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	cliente, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))
	if err != nil {
		log.Fatal("No se pudo conectar a MongoDB: ", err)
	}
	tickets = cliente.Database(nombreBD).Collection("tickets")

	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/docs", http.StatusFound)
	})
	mux.HandleFunc("GET /docs", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		_, _ = w.Write([]byte(swaggerHTML))
	})
	mux.HandleFunc("GET /openapi.json", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(openapiJSON)
	})
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		responderJSON(w, 200, map[string]string{"estado": "ok", "servicio": "actualizar-go"})
	})
	mux.HandleFunc("PUT /tickets/{id}", actualizar)

	log.Println("Actualizar (Go) escuchando en puerto " + puerto)
	log.Fatal(http.ListenAndServe(":"+puerto, mux))
}
