package com.smartlogix.gateway.config;

import com.smartlogix.gateway.exception.InvalidCredentialsException;
import com.smartlogix.gateway.exception.TooManyLoginAttemptsException;
import com.smartlogix.gateway.exception.UserAlreadyExistsException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Traduce errores a respuestas HTTP con código correcto y sin detalles internos.
 * Los errores 4xx del servicio de destino se reenvían (ya están sanitizados por cada microservicio).
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static ResponseEntity<Map<String, Object>> error(HttpStatus estado, String mensaje) {
        return ResponseEntity.status(estado).body(Map.of(
                "timestamp", LocalDateTime.now().toString(),
                "status", estado.value(),
                "error", estado.getReasonPhrase(),
                "message", mensaje));
    }

    @ExceptionHandler(InvalidCredentialsException.class)
    public ResponseEntity<Map<String, Object>> credencialesInvalidas(InvalidCredentialsException ex) {
        return error(HttpStatus.UNAUTHORIZED, ex.getMessage());
    }

    @ExceptionHandler(TooManyLoginAttemptsException.class)
    public ResponseEntity<Map<String, Object>> demasiadosIntentos(TooManyLoginAttemptsException ex) {
        return error(HttpStatus.TOO_MANY_REQUESTS, ex.getMessage());
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<Map<String, Object>> parametroAusente(MissingServletRequestParameterException ex) {
        return error(HttpStatus.BAD_REQUEST, "Parámetro obligatorio ausente: " + ex.getParameterName());
    }

    @ExceptionHandler(UserAlreadyExistsException.class)
    public ResponseEntity<Map<String, Object>> usuarioExistente(UserAlreadyExistsException ex) {
        return error(HttpStatus.CONFLICT, ex.getMessage());
    }

    @ExceptionHandler(HttpStatusCodeException.class)
    public ResponseEntity<?> errorDeServicioDestino(HttpStatusCodeException ex) {
        if (ex.getStatusCode().is4xxClientError()) {
            return ResponseEntity.status(ex.getStatusCode())
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(ex.getResponseBodyAsString());
        }
        log.error("Error 5xx del servicio de destino (HTTP {})", ex.getStatusCode().value());
        return error(HttpStatus.BAD_GATEWAY, "Error en el servicio de destino");
    }

    @ExceptionHandler(ResourceAccessException.class)
    public ResponseEntity<Map<String, Object>> servicioNoDisponible(ResourceAccessException ex) {
        // No se registra el mensaje: contiene la URL con datos del cliente (riesgo de inyección en logs).
        log.error("Servicio de destino no alcanzable");
        return error(HttpStatus.SERVICE_UNAVAILABLE, "Servicio no disponible temporalmente");
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> validacion(MethodArgumentNotValidException ex) {
        String campos = ex.getBindingResult().getFieldErrors().stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage())
                .collect(Collectors.joining("; "));
        return error(HttpStatus.BAD_REQUEST, "Datos de entrada inválidos: " + campos);
    }

    @ExceptionHandler({MethodArgumentTypeMismatchException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<Map<String, Object>> formatoInvalido(Exception ex) {
        return error(HttpStatus.BAD_REQUEST, "Formato de solicitud inválido");
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<Map<String, Object>> metodoNoPermitido(HttpRequestMethodNotSupportedException ex) {
        return error(HttpStatus.METHOD_NOT_ALLOWED, "Método HTTP no permitido");
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<Map<String, Object>> noEncontrado(NoResourceFoundException ex) {
        return error(HttpStatus.NOT_FOUND, "Recurso no encontrado");
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> errorNoControlado(Exception ex) {
        log.error("Error no controlado", ex);
        return error(HttpStatus.INTERNAL_SERVER_ERROR, "Error interno del servidor");
    }
}
