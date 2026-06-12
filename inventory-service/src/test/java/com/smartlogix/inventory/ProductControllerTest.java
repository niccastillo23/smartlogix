package com.smartlogix.inventory;

import com.smartlogix.inventory.controller.ProductController;
import com.smartlogix.inventory.dto.ProductDTO;
import com.smartlogix.inventory.dto.StockUpdateRequest;
import com.smartlogix.inventory.service.ProductService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Autowired
    private ObjectMapper objectMapper;

    private ProductDTO buildDTO() {
        return ProductDTO.builder()
                .id(1L)
                .name("Sauvage")
                .brand("Dior")
                .description("Fragancia masculina")
                .price(new BigDecimal("120.00"))
                .stockQuantity(50)
                .fragrance("Amaderado")
                .build();
    }

    @Test
    void getAllProducts_shouldReturn200() throws Exception {
        when(productService.getAllProducts()).thenReturn(List.of(buildDTO()));
        mockMvc.perform(get("/api/products"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Sauvage"));
    }

    @Test
    void getProductById_shouldReturn200() throws Exception {
        when(productService.getProductById(1L)).thenReturn(buildDTO());
        mockMvc.perform(get("/api/products/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.brand").value("Dior"));
    }

    @Test
    void getByBrand_shouldReturn200() throws Exception {
        when(productService.getProductsByBrand("Dior")).thenReturn(List.of(buildDTO()));
        mockMvc.perform(get("/api/products/brand/Dior"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());
    }

    @Test
    void getByFragrance_shouldReturn200() throws Exception {
        when(productService.getProductsByFragrance("Amaderado")).thenReturn(List.of(buildDTO()));
        mockMvc.perform(get("/api/products/fragrance/Amaderado"))
                .andExpect(status().isOk());
    }

    @Test
    void getByPriceRange_shouldReturn200() throws Exception {
        when(productService.getProductsByPriceRange(any(), any())).thenReturn(List.of(buildDTO()));
        mockMvc.perform(get("/api/products/price-range?min=50&max=200"))
                .andExpect(status().isOk());
    }

    @Test
    void getInStock_shouldReturn200() throws Exception {
        when(productService.getInStockProducts()).thenReturn(List.of(buildDTO()));
        mockMvc.perform(get("/api/products/in-stock"))
                .andExpect(status().isOk());
    }

    @Test
    void searchProducts_shouldReturn200() throws Exception {
        when(productService.searchProducts("sauv")).thenReturn(List.of(buildDTO()));
        mockMvc.perform(get("/api/products/search?name=sauv"))
                .andExpect(status().isOk());
    }

    @Test
    void createProduct_shouldReturn201() throws Exception {
        when(productService.createProduct(any())).thenReturn(buildDTO());
        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(buildDTO())))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Sauvage"));
    }

    @Test
    void updateProduct_shouldReturn200() throws Exception {
        when(productService.updateProduct(eq(1L), any())).thenReturn(buildDTO());
        mockMvc.perform(put("/api/products/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(buildDTO())))
                .andExpect(status().isOk());
    }

    @Test
    void updateStock_shouldReturn200() throws Exception {
        when(productService.updateStock(eq(1L), any())).thenReturn(buildDTO());
        StockUpdateRequest req = new StockUpdateRequest(100);
        mockMvc.perform(patch("/api/products/1/stock")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk());
    }

    @Test
    void deleteProduct_shouldReturn204() throws Exception {
        doNothing().when(productService).deleteProduct(1L);
        mockMvc.perform(delete("/api/products/1"))
                .andExpect(status().isNoContent());
    }
}
