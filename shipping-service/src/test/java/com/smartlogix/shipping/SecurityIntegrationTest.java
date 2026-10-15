package com.smartlogix.shipping;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.nio.charset.StandardCharsets;
import java.util.Date;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** Validación de JWT en el microservicio: sin token o con token inválido se rechaza; con token firmado, se acepta. */
@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {"jwt.secret=" + SecurityIntegrationTest.SECRETO,
        "spring.datasource.url=jdbc:h2:mem:seguridad-test;DB_CLOSE_DELAY=-1"})
class SecurityIntegrationTest {

    static final String SECRETO = "test-only-secret-for-integration-0123456789-0123456789-0123456789-0123456789";

    @Autowired
    private MockMvc mvc;

    @Test
    void sinToken_responde401() throws Exception {
        mvc.perform(get("/api/shipments")).andExpect(status().isUnauthorized());
    }

    @Test
    void tokenInvalido_responde401() throws Exception {
        mvc.perform(get("/api/shipments").header("Authorization", "Bearer token.falso.firma"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void tokenFirmadoConElSecreto_responde200() throws Exception {
        String token = Jwts.builder()
                .subject("bff-gateway")
                .expiration(new Date(System.currentTimeMillis() + 60_000))
                .signWith(Keys.hmacShaKeyFor(SECRETO.getBytes(StandardCharsets.UTF_8)))
                .compact();
        mvc.perform(get("/api/shipments").header("Authorization", "Bearer " + token)).andExpect(status().isOk());
    }
}
