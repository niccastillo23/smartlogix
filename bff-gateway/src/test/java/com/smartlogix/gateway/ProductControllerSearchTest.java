package com.smartlogix.gateway;

import com.smartlogix.gateway.controller.ProductController;
import com.smartlogix.gateway.filter.JwtAuthFilter;
import com.smartlogix.gateway.service.InventoryProxyService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.util.MultiValueMap;

import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** Endpoints de búsqueda del BFF: verifican la ruta reenviada al inventario y la respuesta al cliente. */
@WebMvcTest(ProductController.class)
@AutoConfigureMockMvc(addFilters = false)
class ProductControllerSearchTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private InventoryProxyService inventoryProxyService;

    @MockBean
    private JwtAuthFilter jwtAuthFilter;

    private static final List<Map<String, Object>> RESULTADO =
            List.of(Map.of("id", 2, "name", "Bleu de Chanel", "brand", "Chanel"));

    @Test
    void porMarca_reenviaSegmentoDeMarca() throws Exception {
        when(inventoryProxyService.buscar(any(String[].class), any())).thenReturn(RESULTADO);
        mockMvc.perform(get("/api/products/brand/Chanel"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].brand").value("Chanel"));
        verify(inventoryProxyService).buscar(eq(new String[]{"brand", "Chanel"}), any());
    }

    @Test
    void porFragancia_reenviaSegmentoDeFragancia() throws Exception {
        when(inventoryProxyService.buscar(any(String[].class), any())).thenReturn(RESULTADO);
        mockMvc.perform(get("/api/products/fragrance/Amaderado")).andExpect(status().isOk());
        verify(inventoryProxyService).buscar(eq(new String[]{"fragrance", "Amaderado"}), any());
    }

    @Test
    void porPrecio_reenviaMinimoYMaximo() throws Exception {
        when(inventoryProxyService.buscar(any(String[].class), any())).thenReturn(RESULTADO);
        mockMvc.perform(get("/api/products/price-range?min=50&max=150")).andExpect(status().isOk());
        verify(inventoryProxyService).buscar(eq(new String[]{"price-range"}), any(MultiValueMap.class));
    }

    @Test
    void conStock_reenviaRutaDeStock() throws Exception {
        when(inventoryProxyService.buscar(any(String[].class), any())).thenReturn(RESULTADO);
        mockMvc.perform(get("/api/products/in-stock")).andExpect(status().isOk());
        verify(inventoryProxyService).buscar(eq(new String[]{"in-stock"}), any());
    }

    @Test
    void porNombre_reenviaParametroName() throws Exception {
        when(inventoryProxyService.buscar(any(String[].class), any())).thenReturn(RESULTADO);
        mockMvc.perform(get("/api/products/search?name=sauvage")).andExpect(status().isOk());
        verify(inventoryProxyService).buscar(eq(new String[]{"search"}), any(MultiValueMap.class));
    }
}
