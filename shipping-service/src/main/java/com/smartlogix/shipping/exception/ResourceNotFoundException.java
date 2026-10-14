package com.smartlogix.shipping.exception;

/** Recurso solicitado inexistente. Se traduce a HTTP 404. */
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String mensaje) {
        super(mensaje);
    }
}
