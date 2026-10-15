package com.smartlogix.gateway;

import com.smartlogix.gateway.service.OrderProxyService;
import com.smartlogix.gateway.service.ShippingProxyService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/** Regresión INC-22: el valor de status no puede alterar la URL destino del microservicio. */
@ExtendWith(MockitoExtension.class)
class StatusUrlEncodingTest {

    @Mock
    private RestTemplate restTemplate;

    @Test
    void pedido_valorConAmpersandYLlavesNoAñadeParametros() {
        OrderProxyService servicio = new OrderProxyService(restTemplate);
        ReflectionTestUtils.setField(servicio, "orderUrl", "http://pedidos:8082");
        when(restTemplate.patchForObject(any(URI.class), any(), eq(Map.class))).thenReturn(Map.of());

        servicio.updateOrderStatus(7L, "SHIPPED&admin=true#x${y}");

        ArgumentCaptor<URI> captor = ArgumentCaptor.forClass(URI.class);
        verify(restTemplate).patchForObject(captor.capture(), any(), eq(Map.class));
        URI destino = captor.getValue();
        assertEquals("/api/orders/7/status", destino.getRawPath(), "La ruta no debe cambiar");
        assertTrue(destino.getRawQuery().startsWith("status="), destino.getRawQuery());
        assertFalse(destino.getRawQuery().contains("&"), "No debe aparecer un segundo parámetro");
        assertFalse(destino.getRawQuery().contains("#"), "El fragmento no debe truncar la petición");
        assertNull(destino.getFragment(), "No debe existir fragmento");
    }

    @Test
    void envio_valorConSecuenciasDeRutaNoCambiaLaRuta() {
        ShippingProxyService servicio = new ShippingProxyService(restTemplate);
        ReflectionTestUtils.setField(servicio, "shippingUrl", "http://envios:8083");
        when(restTemplate.patchForObject(any(URI.class), any(), eq(Map.class))).thenReturn(Map.of());

        servicio.updateShipmentStatus(3L, "../../admin");

        ArgumentCaptor<URI> captor = ArgumentCaptor.forClass(URI.class);
        verify(restTemplate).patchForObject(captor.capture(), any(), eq(Map.class));
        assertEquals("/api/shipments/3/status", captor.getValue().getRawPath(), "No debe haber recorrido de directorios");
        assertEquals("http://envios:8083", captor.getValue().getScheme() + "://" + captor.getValue().getAuthority());
    }
}
