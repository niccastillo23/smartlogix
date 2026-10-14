package com.smartlogix.shipping.service;

import com.smartlogix.shipping.exception.ResourceNotFoundException;
import com.smartlogix.shipping.dto.ShippingRequest;
import com.smartlogix.shipping.dto.ShippingResponse;
import com.smartlogix.shipping.entity.Shipment;
import com.smartlogix.shipping.repository.ShipmentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ShippingService {

    private final ShipmentRepository shipmentRepository;
    private final ExternalCarrierService externalCarrierService;

    public List<ShippingResponse> getAllShipments() {
        return shipmentRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    public ShippingResponse getShipmentById(Long id) {
        Shipment shipment = shipmentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Envío no encontrado con id: " + id));
        return toResponse(shipment);
    }

    public ShippingResponse getShipmentByOrderId(Long orderId) {
        Shipment shipment = shipmentRepository.findByOrderId(orderId)
                .orElseThrow(() -> new ResourceNotFoundException("Envío no encontrado para orderId: " + orderId));
        return toResponse(shipment);
    }

    public List<ShippingResponse> getShipmentsByStatus(String status) {
        return shipmentRepository.findByStatus(status).stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public ShippingResponse createShipment(ShippingRequest request) {
        Map<String, Object> carrierResult = externalCarrierService.registerShipment(
                request.getCarrier(), request.getAddress(), request.getCity(), request.getCountry());

        String trackingNumber = (String) carrierResult.get("trackingNumber");
        LocalDate estimatedDelivery = LocalDate.parse((String) carrierResult.get("estimatedDelivery"));
        Boolean isFallback = (Boolean) carrierResult.get("fallback");

        Shipment shipment = Shipment.builder()
                .orderId(request.getOrderId())
                .carrier(request.getCarrier())
                .trackingNumber(trackingNumber)
                .status("REGISTERED")
                .estimatedDelivery(estimatedDelivery)
                .address(request.getAddress())
                .city(request.getCity())
                .country(request.getCountry())
                .circuitBreakerFallback(isFallback)
                .build();

        Shipment saved = shipmentRepository.save(shipment);
        return toResponse(saved);
    }

    @Transactional
    public ShippingResponse updateShipmentStatus(Long id, String status) {
        Shipment shipment = shipmentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Envío no encontrado con id: " + id));
        shipment.setStatus(status);
        Shipment saved = shipmentRepository.save(shipment);
        return toResponse(saved);
    }

    private ShippingResponse toResponse(Shipment shipment) {
        return ShippingResponse.builder()
                .id(shipment.getId())
                .orderId(shipment.getOrderId())
                .carrier(shipment.getCarrier())
                .trackingNumber(shipment.getTrackingNumber())
                .status(shipment.getStatus())
                .estimatedDelivery(shipment.getEstimatedDelivery())
                .address(shipment.getAddress())
                .city(shipment.getCity())
                .country(shipment.getCountry())
                .circuitBreakerFallback(shipment.getCircuitBreakerFallback())
                .createdAt(shipment.getCreatedAt())
                .build();
    }
}
