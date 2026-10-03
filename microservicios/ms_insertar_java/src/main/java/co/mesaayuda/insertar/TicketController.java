package co.mesaayuda.insertar;

import static com.mongodb.client.model.Filters.eq;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.model.FindOneAndUpdateOptions;
import com.mongodb.client.model.ReturnDocument;
import com.mongodb.client.model.Updates;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.LinkedHashMap;
import java.util.Map;
import org.bson.Document;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Tag(name = "Tickets", description = "Inserción de tickets")
public class TicketController {

    private final MongoCollection<Document> tickets;
    private final MongoCollection<Document> contadores;

    public TicketController(MongoClient cliente,
                            @Value("${MONGODB_DB:mesa_ayuda}") String nombreBd) {
        var bd = cliente.getDatabase(nombreBd);
        this.tickets = bd.getCollection("tickets");
        this.contadores = bd.getCollection("counters");
    }

    /** Id autoincremental (1, 2, 3...) usando una coleccion "counters". */
    private long siguienteId() {
        Document c = contadores.findOneAndUpdate(
                eq("_id", "tickets"),
                Updates.inc("seq", 1L),
                new FindOneAndUpdateOptions().upsert(true).returnDocument(ReturnDocument.AFTER));
        return ((Number) c.get("seq")).longValue();
    }

    @GetMapping("/")
    public ResponseEntity<Void> inicio() {
        return ResponseEntity.status(HttpStatus.FOUND).header("Location", "/swagger-ui.html").build();
    }

    @GetMapping("/health")
    @Operation(summary = "Estado del servicio")
    public Map<String, String> health() {
        return Map.of("estado", "ok", "servicio", "insertar-java");
    }

    @PostMapping("/tickets")
    @Operation(summary = "Crear un ticket nuevo")
    @ApiResponse(responseCode = "201", description = "Ticket creado")
    @ApiResponse(responseCode = "400", description = "Datos inválidos")
    public ResponseEntity<Map<String, Object>> crear(@Valid @RequestBody TicketEntrada entrada) {
        long id = siguienteId();
        String estado = (entrada.estado() == null || entrada.estado().isBlank()) ? "abierto" : entrada.estado();
        String tecnico = (entrada.tecnico() == null || entrada.tecnico().isBlank()) ? null : entrada.tecnico().trim();

        Document doc = new Document("_id", id)
                .append("titulo", entrada.titulo().trim())
                .append("descripcion", entrada.descripcion().trim())
                .append("estado", estado)
                .append("tecnico", tecnico);
        tickets.insertOne(doc);

        Map<String, Object> salida = new LinkedHashMap<>();
        salida.put("id", id);
        salida.put("titulo", doc.getString("titulo"));
        salida.put("descripcion", doc.getString("descripcion"));
        salida.put("estado", estado);
        salida.put("tecnico", tecnico);
        return ResponseEntity.status(HttpStatus.CREATED).body(salida);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> datosInvalidos(MethodArgumentNotValidException e) {
        String mensaje = e.getBindingResult().getFieldErrors().stream()
                .map(f -> f.getDefaultMessage()).findFirst().orElse("Datos inválidos");
        return ResponseEntity.badRequest().body(Map.of("error", mensaje));
    }
}
