package com.smartlogix.gateway.exception;

/** Credenciales incorrectas. Se usa el mismo mensaje para usuario inexistente y clave errónea (evita enumeración de usuarios). */
public class InvalidCredentialsException extends RuntimeException {
    public InvalidCredentialsException() {
        super("Credenciales inválidas");
    }
}
