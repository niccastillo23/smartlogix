package com.smartlogix.shipping.service;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

@Service
public class ExternalCarrierService {

    @CircuitBreaker(name = "carrierService", fallbackMethod = "carrierFallback")
    public Map<String, Object> registerShipment(String carrier, String address, String city, String country) {
        simulateCarrierCall(carrier);

        String trackingNumber = "TRK-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        LocalDate estimatedDelivery = LocalDate.now().plusDays(carrier.equalsIgnoreCase("DHL") ? 3 : 5);

        return Map.of(
                "trackingNumber", trackingNumber,
                "estimatedDelivery", estimatedDelivery.toString(),
                "carrierConfirmed", carrier,
                "fallback", false
        );
    }

    public Map<String, Object> carrierFallback(String carrier, String address, String city, String country, Throwable t) {
        String trackingNumber = "FBK-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        LocalDate estimatedDelivery = LocalDate.now().plusDays(7);

        return Map.of(
                "trackingNumber", trackingNumber,
                "estimatedDelivery", estimatedDelivery.toString(),
                "carrierConfirmed", "PENDING_CONFIRMATION",
                "fallback", true
        );
    }

    private void simulateCarrierCall(String carrier) {
        if (carrier.equalsIgnoreCase("FAIL_CARRIER")) {
            throw new RuntimeException("Carrier externo no disponible: " + carrier);
        }
    }
}
