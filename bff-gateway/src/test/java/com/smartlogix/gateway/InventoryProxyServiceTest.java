package com.smartlogix.gateway;

import com.smartlogix.gateway.service.InventoryProxyService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class InventoryProxyServiceTest {

    @Mock
    private RestTemplate restTemplate;

    private InventoryProxyService servicio;

    private URI capturarDestino() {
        ArgumentCaptor<URI> captor = ArgumentCaptor.forClass(URI.class);
        when(restTemplate.exchange(captor.capture(), eq(HttpMethod.GET), isNull(),
                any(ParameterizedTypeReference.class)))
                .thenReturn(ResponseEntity.ok(List.<Map<String, Object>>of()));
        servicio.buscar(new String[]{"brand", "Chanel"}, new LinkedMultiValueMap<>());
        return captor.getValue();
    }

    @Test
    void buscar_construyeRutaDeMarcaSobreElInventario() {
        servicio = new InventoryProxyService(restTemplate);
        ReflectionTestUtils.setField(servicio, "inventoryUrl", "http://inventario:8081");
        URI destino = capturarDestino();
        assertEquals("http://inventario:8081/api/products/brand/Chanel", destino.toString());
    }

    @Test
    void buscar_codificaElSegmentoParaEvitarInyeccionDeRuta() {
        servicio = new InventoryProxyService(restTemplate);
        ReflectionTestUtils.setField(servicio, "inventoryUrl", "http://inventario:8081");
        ArgumentCaptor<URI> captor = ArgumentCaptor.forClass(URI.class);
        when(restTemplate.exchange(captor.capture(), eq(HttpMethod.GET), isNull(),
                any(ParameterizedTypeReference.class)))
                .thenReturn(ResponseEntity.ok(List.<Map<String, Object>>of()));
        servicio.buscar(new String[]{"search"}, paramsNombre("../admin?x=1"));
        String url = captor.getValue().toString();
        // La ruta no cambia: el valor viaja solo en la query string.
        assertTrue(url.startsWith("http://inventario:8081/api/products/search?name="), url);
    }

    @Test
    void buscar_precioEnviaRangoComoParametros() {
        servicio = new InventoryProxyService(restTemplate);
        ReflectionTestUtils.setField(servicio, "inventoryUrl", "http://inventario:8081");
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("min", "50");
        params.add("max", "150");
        ArgumentCaptor<URI> captor = ArgumentCaptor.forClass(URI.class);
        when(restTemplate.exchange(captor.capture(), eq(HttpMethod.GET), isNull(),
                any(ParameterizedTypeReference.class)))
                .thenReturn(ResponseEntity.ok(List.<Map<String, Object>>of()));
        servicio.buscar(new String[]{"price-range"}, params);
        assertEquals("http://inventario:8081/api/products/price-range?min=50&max=150", captor.getValue().toString());
    }

    private MultiValueMap<String, String> paramsNombre(String valor) {
        MultiValueMap<String, String> p = new LinkedMultiValueMap<>();
        p.add("name", valor);
        return p;
    }
}
