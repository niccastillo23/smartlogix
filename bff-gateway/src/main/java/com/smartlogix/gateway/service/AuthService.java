package com.smartlogix.gateway.service;

import com.smartlogix.gateway.config.JwtUtil;
import com.smartlogix.gateway.dto.LoginRequest;
import com.smartlogix.gateway.dto.LoginResponse;
import com.smartlogix.gateway.exception.InvalidCredentialsException;
import com.smartlogix.gateway.exception.UserAlreadyExistsException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final JwtUtil jwtUtil;
    private final PasswordEncoder passwordEncoder;
    /** usuario -> hash BCrypt de la contraseña (nunca el valor en claro). */
    private final Map<String, String> users = new ConcurrentHashMap<>();

    public LoginResponse login(LoginRequest request) {
        String storedHash = users.get(request.getUsername());
        if (storedHash == null || !passwordEncoder.matches(request.getPassword(), storedHash)) {
            throw new InvalidCredentialsException();
        }
        String token = jwtUtil.generateToken(request.getUsername());
        return LoginResponse.builder()
                .token(token)
                .username(request.getUsername())
                .message("Login exitoso")
                .build();
    }

    public LoginResponse register(LoginRequest request) {
        String hash = passwordEncoder.encode(request.getPassword());
        // putIfAbsent es atómico: evita que dos registros simultáneos del mismo usuario tengan éxito.
        if (users.putIfAbsent(request.getUsername(), hash) != null) {
            throw new UserAlreadyExistsException();
        }
        String token = jwtUtil.generateToken(request.getUsername());
        return LoginResponse.builder()
                .token(token)
                .username(request.getUsername())
                .message("Registro exitoso")
                .build();
    }
}
