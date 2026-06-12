package com.smartlogix.gateway.controller;

import com.smartlogix.gateway.dto.LoginRequest;
import com.smartlogix.gateway.dto.LoginResponse;
import com.smartlogix.gateway.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "Auth", description = "Endpoints de autenticación JWT")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    @Operation(summary = "Iniciar sesión y obtener token JWT")
    public ResponseEntity<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/register")
    @Operation(summary = "Registrar nuevo usuario y obtener token JWT")
    public ResponseEntity<LoginResponse> register(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.register(request));
    }
}
