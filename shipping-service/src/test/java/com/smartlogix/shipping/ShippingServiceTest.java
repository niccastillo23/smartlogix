package com.smartlogix.shipping;

import com.smartlogix.shipping.dto.ShippingRequest;
import com.smartlogix.shipping.dto.ShippingResponse;
import com.smartlogix.shipping.entity.Shipment;
import com.smartlogix.shipping.repository.ShipmentRepository;
import com.smartlogix.shipping.service.ExternalCarrierService;
import com.smartlogix.shipping.service.ShippingService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ShippingServiceTest {

    @Mock
    private ShipmentRepository shipmentRepository;

    @Mock
    private ExternalCarrierService externalCarrierService;

    private ShippingService shippingService;

    private Shipment buildShipment() {
        return Shipment.builder()
                .id(1L)
                .orderId(100L)
                .carrier("DHL")
                .trackingNumber("TRK-ABC12345")
                .status("REGISTERED")
                .estimatedDelivery(LocalDate.now().plusDays(3))
                .address("Calle 123")
                .city("Lima")
                .country("Perú")
                .circuitBreakerFallback(false)
                .createdAt(LocalDateTime.now())
                .build();
    }

    private ShippingRequest buildRequest() {
        return ShippingRequest.builder()
                .orderId(100L)
                .carrier("DHL")
                .address("Calle 123")
                .city("Lima")
                .country("Perú")
                .build();
    }

    @BeforeEach
    void setUp() {
        shippingService = new ShippingService(shipmentRepository, externalCarrierService);
    }

    @Test
    void getAllShipments_shouldReturnList() {
        when(shipmentRepository.findAll()).thenReturn(List.of(buildShipment()));
        List<ShippingResponse> result = shippingService.getAllShipments();
        assertEquals(1, result.size());
        assertEquals("DHL", result.get(0).getCarrier());
    }

    @Test
    void getShipmentById_found_shouldReturn() {
        when(shipmentRepository.findById(1L)).thenReturn(Optional.of(buildShipment()));
        ShippingResponse result = shippingService.getShipmentById(1L);
        assertNotNull(result);
        assertEquals("TRK-ABC12345", result.getTrackingNumber());
    }

    @Test
    void getShipmentById_notFound_shouldThrow() {
        when(shipmentRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> shippingService.getShipmentById(99L));
    }

    @Test
    void getShipmentByOrderId_found_shouldReturn() {
        when(shipmentRepository.findByOrderId(100L)).thenReturn(Optional.of(buildShipment()));
        ShippingResponse result = shippingService.getShipmentByOrderId(100L);
        assertEquals(100L, result.getOrderId());
    }

    @Test
    void getShipmentByOrderId_notFound_shouldThrow() {
        when(shipmentRepository.findByOrderId(999L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> shippingService.getShipmentByOrderId(999L));
    }

    @Test
    void getShipmentsByStatus_shouldReturnList() {
        when(shipmentRepository.findByStatus("REGISTERED")).thenReturn(List.of(buildShipment()));
        List<ShippingResponse> result = shippingService.getShipmentsByStatus("REGISTERED");
        assertEquals(1, result.size());
    }

    @Test
    void createShipment_carrierAvailable_shouldRegisterNormally() {
        when(externalCarrierService.registerShipment("DHL", "Calle 123", "Lima", "Perú"))
                .thenReturn(Map.of(
                        "trackingNumber", "TRK-TEST123",
                        "estimatedDelivery", LocalDate.now().plusDays(3).toString(),
                        "carrierConfirmed", "DHL",
                        "fallback", false
                ));
        when(shipmentRepository.save(any(Shipment.class))).thenAnswer(inv -> {
            Shipment s = inv.getArgument(0);
            s.setId(1L);
            return s;
        });

        ShippingResponse result = shippingService.createShipment(buildRequest());
        assertEquals("TRK-TEST123", result.getTrackingNumber());
        assertFalse(result.getCircuitBreakerFallback());
        assertEquals("REGISTERED", result.getStatus());
    }

    @Test
    void createShipment_carrierDown_shouldUseFallback() {
        when(externalCarrierService.registerShipment("FAIL_CARRIER", "Calle 123", "Lima", "Perú"))
                .thenReturn(Map.of(
                        "trackingNumber", "FBK-FALLBACK",
                        "estimatedDelivery", LocalDate.now().plusDays(7).toString(),
                        "carrierConfirmed", "PENDING_CONFIRMATION",
                        "fallback", true
                ));
        when(shipmentRepository.save(any(Shipment.class))).thenAnswer(inv -> {
            Shipment s = inv.getArgument(0);
            s.setId(2L);
            return s;
        });

        ShippingRequest failReq = ShippingRequest.builder()
                .orderId(200L).carrier("FAIL_CARRIER")
                .address("Calle 123").city("Lima").country("Perú").build();

        ShippingResponse result = shippingService.createShipment(failReq);
        assertTrue(result.getCircuitBreakerFallback());
        assertEquals("FBK-FALLBACK", result.getTrackingNumber());
    }

    @Test
    void updateShipmentStatus_found_shouldUpdate() {
        Shipment shipment = buildShipment();
        when(shipmentRepository.findById(1L)).thenReturn(Optional.of(shipment));
        when(shipmentRepository.save(any(Shipment.class))).thenReturn(shipment);
        ShippingResponse result = shippingService.updateShipmentStatus(1L, "IN_TRANSIT");
        assertEquals("IN_TRANSIT", result.getStatus());
    }

    @Test
    void updateShipmentStatus_notFound_shouldThrow() {
        when(shipmentRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> shippingService.updateShipmentStatus(99L, "IN_TRANSIT"));
    }
}
