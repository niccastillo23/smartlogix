package com.smartlogix.gateway;

import com.smartlogix.gateway.config.GlobalExceptionHandler;
import com.smartlogix.gateway.exception.InvalidCredentialsException;
import com.smartlogix.gateway.exception.UserAlreadyExistsException;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;

import java.nio.charset.StandardCharsets;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class GlobalExceptionHandlerTest {

    private final MockMvc mvc = MockMvcBuilders.standaloneSetup(new FallaController())
            .setControllerAdvice(new GlobalExceptionHandler())
            .build();

    @RestController
    static class FallaController {
        @GetMapping("/t/credenciales")
        void credenciales() { throw new InvalidCredentialsException(); }

        @GetMapping("/t/duplicado")
        void duplicado() { throw new UserAlreadyExistsException(); }

        @GetMapping("/t/upstream4xx")
        void upstream4xx() {
            throw HttpClientErrorException.create(HttpStatus.BAD_REQUEST, "Bad Request", new HttpHeaders(),
                    "{\"message\":\"nombre vacio\"}".getBytes(StandardCharsets.UTF_8), StandardCharsets.UTF_8);
        }

        @GetMapping("/t/upstream5xx")
        void upstream5xx() {
            throw HttpServerErrorException.create(HttpStatus.INTERNAL_SERVER_ERROR, "boom", new HttpHeaders(),
                    "detalle-upstream".getBytes(StandardCharsets.UTF_8), StandardCharsets.UTF_8);
        }

        @GetMapping("/t/caido")
        void caido() { throw new ResourceAccessException("Connection refused"); }

        @GetMapping("/t/interno")
        void interno() { throw new IllegalStateException("detalle-secreto-interno"); }

        @GetMapping("/t/numero/{id}")
        String numero(@PathVariable long id) { return "ok"; }
    }

    @Test
    void credencialesInvalidas_devuelve401() throws Exception {
        mvc.perform(get("/t/credenciales"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.message").value("Credenciales inválidas"));
    }

    @Test
    void usuarioDuplicado_devuelve409() throws Exception {
        mvc.perform(get("/t/duplicado")).andExpect(status().isConflict());
    }

    @Test
    void errorCliente_delServicioDestino_seReenviaConSuCodigo() throws Exception {
        mvc.perform(get("/t/upstream4xx"))
                .andExpect(status().isBadRequest())
                .andExpect(content().string(org.hamcrest.Matchers.containsString("nombre vacio")));
    }

    @Test
    void errorServidor_delServicioDestino_devuelve502SinDetalle() throws Exception {
        mvc.perform(get("/t/upstream5xx"))
                .andExpect(status().isBadGateway())
                .andExpect(content().string(org.hamcrest.Matchers.not(org.hamcrest.Matchers.containsString("detalle-upstream"))));
    }

    @Test
    void servicioNoAlcanzable_devuelve503() throws Exception {
        mvc.perform(get("/t/caido")).andExpect(status().isServiceUnavailable());
    }

    @Test
    void errorNoControlado_noExponeMensajeInterno() throws Exception {
        mvc.perform(get("/t/interno"))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.message").value("Error interno del servidor"))
                .andExpect(content().string(org.hamcrest.Matchers.not(org.hamcrest.Matchers.containsString("detalle-secreto-interno"))));
    }

    @Test
    void tipoDeParametroInvalido_devuelve400() throws Exception {
        mvc.perform(get("/t/numero/abc")).andExpect(status().isBadRequest());
    }
}
