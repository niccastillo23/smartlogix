package com.smartlogix.gateway.exception;

public class UserAlreadyExistsException extends RuntimeException {
    public UserAlreadyExistsException() {
        super("El usuario ya existe");
    }
}
