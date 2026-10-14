package com.smartlogix.gateway.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import org.springframework.util.MultiValueMap;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class InventoryProxyService {

    private final RestTemplate restTemplate;

    @Value("${services.inventory.url}")
    private String inventoryUrl;

    public List<Map<String, Object>> getAllProducts() {
        return restTemplate.exchange(
                inventoryUrl + "/api/products",
                HttpMethod.GET, null,
                new ParameterizedTypeReference<List<Map<String, Object>>>() {}
        ).getBody();
    }

    public Map<String, Object> getProductById(Long id) {
        return restTemplate.getForObject(inventoryUrl + "/api/products/" + id, Map.class);
    }

    public Map<String, Object> createProduct(Map<String, Object> product) {
        return restTemplate.postForObject(inventoryUrl + "/api/products", product, Map.class);
    }

    public Map<String, Object> updateProduct(Long id, Map<String, Object> product) {
        restTemplate.put(inventoryUrl + "/api/products/" + id, product);
        return restTemplate.getForObject(inventoryUrl + "/api/products/" + id, Map.class);
    }

    public Map<String, Object> updateStock(Long id, Map<String, Object> stockRequest) {
        return restTemplate.patchForObject(inventoryUrl + "/api/products/" + id + "/stock", stockRequest, Map.class);
    }

    /**
     * Reenvía una consulta de búsqueda al inventario. Los segmentos de ruta y los parámetros
     * se codifican por separado, de modo que la entrada del cliente no altera la URL destino.
     */
    public List<Map<String, Object>> buscar(String[] segmentos, MultiValueMap<String, String> parametros) {
        URI destino = UriComponentsBuilder.fromUriString(inventoryUrl)
                .pathSegment("api", "products")
                .pathSegment(segmentos)
                .queryParams(parametros)
                .build()
                .encode()
                .toUri();
        return restTemplate.exchange(destino, HttpMethod.GET, null,
                new ParameterizedTypeReference<List<Map<String, Object>>>() {}).getBody();
    }
}
