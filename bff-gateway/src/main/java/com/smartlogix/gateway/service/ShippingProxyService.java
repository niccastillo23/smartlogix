package com.smartlogix.gateway.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import org.springframework.web.util.UriComponentsBuilder;
import java.net.URI;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ShippingProxyService {

    private final RestTemplate restTemplate;

    @Value("${services.shipping.url}")
    private String shippingUrl;

    public List<Map<String, Object>> getAllShipments() {
        return restTemplate.exchange(
                shippingUrl + "/api/shipments",
                HttpMethod.GET, null,
                new ParameterizedTypeReference<List<Map<String, Object>>>() {}
        ).getBody();
    }

    public Map<String, Object> getShipmentByOrderId(Long orderId) {
        return restTemplate.getForObject(shippingUrl + "/api/shipments/order/" + orderId, Map.class);
    }

    public Map<String, Object> createShipment(Map<String, Object> shippingRequest) {
        return restTemplate.postForObject(shippingUrl + "/api/shipments", shippingRequest, Map.class);
    }

    public Map<String, Object> updateShipmentStatus(Long id, String status) {
        // El valor se codifica como parámetro: no puede alterar la ruta ni añadir parámetros (INC-22).
        URI destino = UriComponentsBuilder.fromUriString(shippingUrl)
                .pathSegment("api", "shipments", String.valueOf(id), "status")
                .queryParam("status", "{status}")
                .buildAndExpand(status)
                .encode()
                .toUri();
        return restTemplate.patchForObject(destino, null, Map.class);
    }
}
