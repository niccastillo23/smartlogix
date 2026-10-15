package com.smartlogix.gateway.exception;

/** Demasiados intentos fallidos de inicio de sesión para el mismo usuario en la ventana configurada (HTTP 429). */
public class TooManyLoginAttemptsException extends RuntimeException {
    public TooManyLoginAttemptsException() {
        super("Demasiados intentos fallidos. Intenta nuevamente más tarde");
    }
}
