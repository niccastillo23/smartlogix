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
public class OrderProxyService {

    private final RestTemplate restTemplate;

    @Value("${services.order.url}")
    private String orderUrl;

    public List<Map<String, Object>> getAllOrders() {
        return restTemplate.exchange(
                orderUrl + "/api/orders",
                HttpMethod.GET, null,
                new ParameterizedTypeReference<List<Map<String, Object>>>() {}
        ).getBody();
    }

    public Map<String, Object> getOrderById(Long id) {
        return restTemplate.getForObject(orderUrl + "/api/orders/" + id, Map.class);
    }

    public Map<String, Object> createOrder(Map<String, Object> orderRequest) {
        return restTemplate.postForObject(orderUrl + "/api/orders", orderRequest, Map.class);
    }

    public Map<String, Object> updateOrderStatus(Long id, String status) {
        // El valor se codifica como parámetro: no puede alterar la ruta ni añadir parámetros (INC-22).
        URI destino = UriComponentsBuilder.fromUriString(orderUrl)
                .pathSegment("api", "orders", String.valueOf(id), "status")
                .queryParam("status", "{status}")
                .buildAndExpand(status)
                .encode()
                .toUri();
        return restTemplate.patchForObject(destino, null, Map.class);
    }
}
