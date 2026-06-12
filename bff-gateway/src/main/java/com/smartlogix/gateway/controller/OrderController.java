package com.smartlogix.gateway.controller;

import com.smartlogix.gateway.service.OrderProxyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Tag(name = "Orders (BFF)", description = "Proxy al microservicio de Pedidos")
public class OrderController {

    private final OrderProxyService orderProxyService;

    @GetMapping
    @Operation(summary = "Listar todos los pedidos")
    public ResponseEntity<List<Map<String, Object>>> getAllOrders() {
        return ResponseEntity.ok(orderProxyService.getAllOrders());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener pedido por ID")
    public ResponseEntity<Map<String, Object>> getOrderById(@PathVariable Long id) {
        return ResponseEntity.ok(orderProxyService.getOrderById(id));
    }

    @PostMapping
    @Operation(summary = "Crear nuevo pedido")
    public ResponseEntity<Map<String, Object>> createOrder(@RequestBody Map<String, Object> orderRequest) {
        return ResponseEntity.status(HttpStatus.CREATED).body(orderProxyService.createOrder(orderRequest));
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Actualizar estado de un pedido")
    public ResponseEntity<Map<String, Object>> updateStatus(@PathVariable Long id, @RequestParam String status) {
        return ResponseEntity.ok(orderProxyService.updateOrderStatus(id, status));
    }
}
