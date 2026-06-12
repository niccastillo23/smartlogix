package com.smartlogix.gateway.service;

import com.smartlogix.gateway.config.JwtUtil;
import com.smartlogix.gateway.dto.LoginRequest;
import com.smartlogix.gateway.dto.LoginResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final JwtUtil jwtUtil;
    private final Map<String, String> users = new ConcurrentHashMap<>();

    public LoginResponse login(LoginRequest request) {
        String storedPassword = users.get(request.getUsername());
        if (storedPassword == null) {
            throw new RuntimeException("Usuario no encontrado: " + request.getUsername());
        }
        if (!storedPassword.equals(request.getPassword())) {
            throw new RuntimeException("Contraseña incorrecta");
        }
        String token = jwtUtil.generateToken(request.getUsername());
        return LoginResponse.builder()
                .token(token)
                .username(request.getUsername())
                .message("Login exitoso")
                .build();
    }

    public LoginResponse register(LoginRequest request) {
        if (users.containsKey(request.getUsername())) {
            throw new RuntimeException("El usuario ya existe: " + request.getUsername());
        }
        users.put(request.getUsername(), request.getPassword());
        String token = jwtUtil.generateToken(request.getUsername());
        return LoginResponse.builder()
                .token(token)
                .username(request.getUsername())
                .message("Registro exitoso")
                .build();
    }
}
