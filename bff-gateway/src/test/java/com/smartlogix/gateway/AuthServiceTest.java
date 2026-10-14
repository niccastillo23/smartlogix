package com.smartlogix.gateway;

import com.smartlogix.gateway.dto.LoginRequest;
import com.smartlogix.gateway.dto.LoginResponse;
import com.smartlogix.gateway.service.AuthService;
import com.smartlogix.gateway.exception.InvalidCredentialsException;
import com.smartlogix.gateway.exception.UserAlreadyExistsException;
import java.lang.reflect.Field;
import java.util.Map;
import com.smartlogix.gateway.config.JwtUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private JwtUtil jwtUtil;

    private AuthService authService;

    @BeforeEach
    void setUp() {
        authService = new AuthService(jwtUtil, new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder());
    }

    @Test
    void register_shouldCreateUserAndReturnToken() {
        when(jwtUtil.generateToken(anyString())).thenReturn("mock-token");
        LoginRequest request = new LoginRequest("newuser", "password123");
        LoginResponse response = authService.register(request);

        assertNotNull(response);
        assertEquals("mock-token", response.getToken());
        assertEquals("newuser", response.getUsername());
        assertEquals("Registro exitoso", response.getMessage());
    }

    @Test
    void register_duplicateUser_shouldThrow() {
        LoginRequest first = new LoginRequest("user1", "pass1");
        when(jwtUtil.generateToken(anyString())).thenReturn("token1");
        authService.register(first);

        LoginRequest duplicate = new LoginRequest("user1", "pass2");
        assertThrows(UserAlreadyExistsException.class, () -> authService.register(duplicate));
    }

    @Test
    void login_validCredentials_shouldReturnToken() {
        when(jwtUtil.generateToken(anyString())).thenReturn("mock-token");
        LoginRequest registerReq = new LoginRequest("loginuser", "pass123");
        authService.register(registerReq);

        LoginRequest loginReq = new LoginRequest("loginuser", "pass123");
        LoginResponse response = authService.login(loginReq);

        assertNotNull(response);
        assertEquals("mock-token", response.getToken());
        assertEquals("Login exitoso", response.getMessage());
    }

    @Test
    void login_wrongPassword_shouldThrow() {
        when(jwtUtil.generateToken(anyString())).thenReturn("token");
        authService.register(new LoginRequest("user2", "correct"));

        assertThrows(InvalidCredentialsException.class, () -> authService.login(new LoginRequest("user2", "wrong")));
    }

    @Test
    void login_nonExistentUser_shouldThrow() {
        assertThrows(InvalidCredentialsException.class, () -> authService.login(new LoginRequest("ghost", "pass")));
    }

    @Test
    @SuppressWarnings("unchecked")
    void register_shouldStoreBcryptHashNotPlaintext() throws Exception {
        when(jwtUtil.generateToken(anyString())).thenReturn("token");
        authService.register(new LoginRequest("hashuser", "password123"));

        Field campo = AuthService.class.getDeclaredField("users");
        campo.setAccessible(true);
        String almacenado = ((Map<String, String>) campo.get(authService)).get("hashuser");

        assertNotEquals("password123", almacenado);
        assertTrue(almacenado.startsWith("$2"), "Se esperaba hash BCrypt");
    }
}
