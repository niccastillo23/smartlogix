package com.smartlogix.shipping.config;

import com.smartlogix.shipping.exception.ResourceNotFoundException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Traduce excepciones a respuestas HTTP con el codigo correcto.
 * No devuelve mensajes internos del framework ni trazas al cliente; los errores no controlados
 * se registran en el log del servidor y se responde con un mensaje generico.
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

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> noEncontrado(ResourceNotFoundException ex) {
        return error(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> argumentoInvalido(IllegalArgumentException ex) {
        return error(HttpStatus.BAD_REQUEST, ex.getMessage());
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
    public ResponseEntity<Map<String, Object>> rutaNoEncontrada(NoResourceFoundException ex) {
        return error(HttpStatus.NOT_FOUND, "Recurso no encontrado");
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<Map<String, Object>> parametroAusente(MissingServletRequestParameterException ex) {
        return error(HttpStatus.BAD_REQUEST, "Parámetro obligatorio ausente: " + ex.getParameterName());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> errorNoControlado(Exception ex) {
        log.error("Error no controlado", ex);
        return error(HttpStatus.INTERNAL_SERVER_ERROR, "Error interno del servidor");
    }
}
