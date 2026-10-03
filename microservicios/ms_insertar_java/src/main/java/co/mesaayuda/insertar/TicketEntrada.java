package co.mesaayuda.insertar;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

@Schema(description = "Datos para crear un ticket")
public record TicketEntrada(
        @Schema(example = "Impresora sin conexión")
        @NotBlank(message = "titulo es obligatorio")
        String titulo,

        @Schema(example = "La impresora del piso 2 no imprime")
        @NotBlank(message = "descripcion es obligatoria")
        String descripcion,

        @Schema(example = "abierto", allowableValues = {"abierto", "cerrado"}, defaultValue = "abierto")
        @Pattern(regexp = "abierto|cerrado", message = "estado debe ser 'abierto' o 'cerrado'")
        String estado,

        @Schema(example = "Carlos Pérez", nullable = true)
        String tecnico) {
}
