package com.smartlogix.shipping;

import com.smartlogix.shipping.config.GlobalExceptionHandler;
import com.smartlogix.shipping.exception.ResourceNotFoundException;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class GlobalExceptionHandlerTest {

    private final MockMvc mvc = MockMvcBuilders.standaloneSetup(new FallaController())
            .setControllerAdvice(new GlobalExceptionHandler())
            .build();

    record Entrada(@NotBlank String nombre) { }

    @RestController
    static class FallaController {
        @GetMapping("/t/noexiste")
        void noExiste() { throw new ResourceNotFoundException("Recurso no encontrado con id: 7"); }

        @GetMapping("/t/argumento")
        void argumento() { throw new IllegalArgumentException("Tipo no soportado: X"); }

        @GetMapping("/t/interno")
        void interno() { throw new IllegalStateException("detalle-secreto-interno"); }

        @GetMapping("/t/numero/{id}")
        String numero(@PathVariable long id) { return "ok"; }

        @PostMapping("/t/crear")
        String crear(@Valid @RequestBody Entrada entrada) { return "ok"; }
    }

    @Test
    void recursoInexistente_devuelve404() throws Exception {
        mvc.perform(get("/t/noexiste"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.message").value("Recurso no encontrado con id: 7"));
    }

    @Test
    void argumentoInvalido_devuelve400ConMensajeControlado() throws Exception {
        mvc.perform(get("/t/argumento"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("Tipo no soportado: X"));
    }

    @Test
    void errorNoControlado_devuelve500SinExponerDetalle() throws Exception {
        mvc.perform(get("/t/interno"))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.message").value("Error interno del servidor"))
                .andExpect(content().string(org.hamcrest.Matchers.not(org.hamcrest.Matchers.containsString("detalle-secreto-interno"))));
    }

    @Test
    void parametroConFormatoInvalido_devuelve400() throws Exception {
        mvc.perform(get("/t/numero/abc")).andExpect(status().isBadRequest());
    }

    @Test
    void validacionFallida_devuelve400IndicandoCampo() throws Exception {
        mvc.perform(post("/t/crear").contentType("application/json").content("{\"nombre\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value(org.hamcrest.Matchers.containsString("nombre")));
    }

    @Test
    void metodoNoPermitido_devuelve405() throws Exception {
        mvc.perform(get("/t/crear")).andExpect(status().isMethodNotAllowed());
    }
}
