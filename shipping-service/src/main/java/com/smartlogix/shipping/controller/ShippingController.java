package com.smartlogix.shipping.controller;

import com.smartlogix.shipping.dto.ShippingRequest;
import com.smartlogix.shipping.dto.ShippingResponse;
import com.smartlogix.shipping.service.ShippingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/shipments")
@RequiredArgsConstructor
@Tag(name = "Shipments", description = "API de gestión de envíos - Circuit Breaker Pattern")
public class ShippingController {

    private final ShippingService shippingService;

    @GetMapping
    @Operation(summary = "Listar todos los envíos")
    public ResponseEntity<List<ShippingResponse>> getAllShipments() {
        return ResponseEntity.ok(shippingService.getAllShipments());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener envío por ID")
    public ResponseEntity<ShippingResponse> getShipmentById(@PathVariable Long id) {
        return ResponseEntity.ok(shippingService.getShipmentById(id));
    }

    @GetMapping("/order/{orderId}")
    @Operation(summary = "Obtener envío por orderId")
    public ResponseEntity<ShippingResponse> getShipmentByOrderId(@PathVariable Long orderId) {
        return ResponseEntity.ok(shippingService.getShipmentByOrderId(orderId));
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "Obtener envíos por estado")
    public ResponseEntity<List<ShippingResponse>> getByStatus(@PathVariable String status) {
        return ResponseEntity.ok(shippingService.getShipmentsByStatus(status));
    }

    @PostMapping
    @Operation(summary = "Crear nuevo envío (con Circuit Breaker al carrier externo)")
    public ResponseEntity<ShippingResponse> createShipment(@Valid @RequestBody ShippingRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(shippingService.createShipment(request));
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Actualizar estado de un envío")
    public ResponseEntity<ShippingResponse> updateStatus(@PathVariable Long id, @RequestParam String status) {
        return ResponseEntity.ok(shippingService.updateShipmentStatus(id, status));
    }
}
