package com.smartlogix.order.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * Valida el token JWT firmado (HMAC) que envía el BFF en cada llamada.
 * Defensa en profundidad: el microservicio no confía en que la petición venga del gateway.
 * Si JWT_SECRET no está configurado, se rechaza toda petición protegida (fail closed).
 */
@Slf4j
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    @Value("${jwt.secret:}")
    private String secret;

    @PostConstruct
    void verificarConfiguracion() {
        if (secret == null || secret.length() < 32) {
            log.error("JWT_SECRET no configurado o demasiado corto: las peticiones protegidas serán rechazadas");
        }
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String cabecera = request.getHeader("Authorization");
        if (cabecera != null && cabecera.startsWith("Bearer ")) {
            String sujeto = validarYObtenerSujeto(cabecera.substring(7));
            if (sujeto != null) {
                SecurityContextHolder.getContext().setAuthentication(
                        new UsernamePasswordAuthenticationToken(sujeto, null, List.of()));
            }
        }
        chain.doFilter(request, response);
    }

    private String validarYObtenerSujeto(String token) {
        if (secret == null || secret.length() < 32) {
            return null;
        }
        try {
            return Jwts.parser()
                    .verifyWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .getSubject();
        } catch (RuntimeException e) {
            return null;
        }
    }
}
