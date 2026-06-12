package com.smartlogix.gateway.controller;

import com.smartlogix.gateway.service.InventoryProxyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
}
