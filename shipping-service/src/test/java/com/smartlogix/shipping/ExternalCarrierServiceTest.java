package com.smartlogix.shipping;

import com.smartlogix.shipping.service.ExternalCarrierService;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ExternalCarrierServiceTest {

    private final ExternalCarrierService service = new ExternalCarrierService();

    @Test
    void registerShipment_validCarrier_shouldReturnTrackingInfo() {
        Map<String, Object> result = service.registerShipment("DHL", "Calle 123", "Lima", "Perú");
        assertNotNull(result.get("trackingNumber"));
        assertTrue(((String) result.get("trackingNumber")).startsWith("TRK-"));
        assertNotNull(result.get("estimatedDelivery"));
        assertEquals("DHL", result.get("carrierConfirmed"));
        assertEquals(false, result.get("fallback"));
    }

    @Test
    void registerShipment_failCarrier_shouldTriggerFallback() {
        Map<String, Object> result = service.carrierFallback("FAIL_CARRIER", "Calle 123", "Lima", "Perú", new RuntimeException("fail"));
        assertNotNull(result.get("trackingNumber"));
        assertTrue(((String) result.get("trackingNumber")).startsWith("FBK-"));
        assertEquals("PENDING_CONFIRMATION", result.get("carrierConfirmed"));
        assertEquals(true, result.get("fallback"));
    }

    @Test
    void registerShipment_failCarrier_shouldThrowException() {
        assertThrows(RuntimeException.class, () -> service.registerShipment("FAIL_CARRIER", "addr", "city", "country"));
    }
}
