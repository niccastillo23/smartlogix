package com.smartlogix.gateway.controller;

import com.smartlogix.gateway.service.InventoryProxyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
@Tag(name = "Products (BFF)", description = "Proxy al microservicio de Inventario")
public class ProductController {

    private final InventoryProxyService inventoryProxyService;

    @GetMapping
    @Operation(summary = "Listar todos los productos del catálogo")
    public ResponseEntity<List<Map<String, Object>>> getAllProducts() {
        return ResponseEntity.ok(inventoryProxyService.getAllProducts());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener producto por ID")
    public ResponseEntity<Map<String, Object>> getProductById(@PathVariable Long id) {
        return ResponseEntity.ok(inventoryProxyService.getProductById(id));
    }

    @PostMapping
    @Operation(summary = "Crear nuevo producto")
    public ResponseEntity<Map<String, Object>> createProduct(@RequestBody Map<String, Object> product) {
        return ResponseEntity.status(HttpStatus.CREATED).body(inventoryProxyService.createProduct(product));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar producto")
    public ResponseEntity<Map<String, Object>> updateProduct(@PathVariable Long id, @RequestBody Map<String, Object> product) {
        return ResponseEntity.ok(inventoryProxyService.updateProduct(id, product));
    }

    @PatchMapping("/{id}/stock")
    @Operation(summary = "Actualizar stock de producto")
    public ResponseEntity<Map<String, Object>> updateStock(@PathVariable Long id, @RequestBody Map<String, Object> stockRequest) {
        return ResponseEntity.ok(inventoryProxyService.updateStock(id, stockRequest));
    }

    @GetMapping("/brand/{brand}")
    @Operation(summary = "Buscar productos por marca")
    public ResponseEntity<List<Map<String, Object>>> porMarca(@PathVariable String brand) {
        return ResponseEntity.ok(inventoryProxyService.buscar(new String[]{"brand", brand}, new LinkedMultiValueMap<>()));
    }

    @GetMapping("/fragrance/{fragrance}")
    @Operation(summary = "Buscar productos por fragancia")
    public ResponseEntity<List<Map<String, Object>>> porFragancia(@PathVariable String fragrance) {
        return ResponseEntity.ok(inventoryProxyService.buscar(new String[]{"fragrance", fragrance}, new LinkedMultiValueMap<>()));
    }

    @GetMapping("/price-range")
    @Operation(summary = "Buscar productos por rango de precio")
    public ResponseEntity<List<Map<String, Object>>> porPrecio(@RequestParam BigDecimal min, @RequestParam BigDecimal max) {
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("min", min.toPlainString());
        params.add("max", max.toPlainString());
        return ResponseEntity.ok(inventoryProxyService.buscar(new String[]{"price-range"}, params));
    }

    @GetMapping("/in-stock")
    @Operation(summary = "Listar productos con stock disponible")
    public ResponseEntity<List<Map<String, Object>>> conStock() {
        return ResponseEntity.ok(inventoryProxyService.buscar(new String[]{"in-stock"}, new LinkedMultiValueMap<>()));
    }

    @GetMapping("/search")
    @Operation(summary = "Buscar productos por nombre")
    public ResponseEntity<List<Map<String, Object>>> porNombre(@RequestParam String name) {
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("name", name);
        return ResponseEntity.ok(inventoryProxyService.buscar(new String[]{"search"}, params));
    }
}
