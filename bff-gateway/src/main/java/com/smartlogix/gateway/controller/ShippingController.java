package com.smartlogix.gateway.controller;

import com.smartlogix.gateway.service.ShippingProxyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/shipments")
@RequiredArgsConstructor
@Tag(name = "Shipments (BFF)", description = "Proxy al microservicio de Envíos")
public class ShippingController {

    private final ShippingProxyService shippingProxyService;

    @GetMapping
    @Operation(summary = "Listar todos los envíos")
    public ResponseEntity<List<Map<String, Object>>> getAllShipments() {
        return ResponseEntity.ok(shippingProxyService.getAllShipments());
    }

    @GetMapping("/order/{orderId}")
    @Operation(summary = "Obtener envío por orderId")
    public ResponseEntity<Map<String, Object>> getShipmentByOrderId(@PathVariable Long orderId) {
        return ResponseEntity.ok(shippingProxyService.getShipmentByOrderId(orderId));
    }

    @PostMapping
    @Operation(summary = "Crear nuevo envío")
    public ResponseEntity<Map<String, Object>> createShipment(@RequestBody Map<String, Object> shippingRequest) {
        return ResponseEntity.status(HttpStatus.CREATED).body(shippingProxyService.createShipment(shippingRequest));
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Actualizar estado de envío")
    public ResponseEntity<Map<String, Object>> updateStatus(@PathVariable Long id, @RequestParam String status) {
        return ResponseEntity.ok(shippingProxyService.updateShipmentStatus(id, status));
    }
}
