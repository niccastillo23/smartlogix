package com.smartlogix.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

/**
 * Cliente HTTP hacia los microservicios.
 * - JdkClientHttpRequestFactory: HttpURLConnection (valor por defecto) no admite PATCH (INC-19).
 * - Interceptor: cada llamada lleva un token de servicio firmado; los microservicios lo validan (INC-15).
 */
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate(JwtUtil jwtUtil) {
        RestTemplate restTemplate = new RestTemplate(new JdkClientHttpRequestFactory());
        restTemplate.getInterceptors().add((request, body, execution) -> {
            request.getHeaders().setBearerAuth(jwtUtil.generateToken("bff-gateway"));
            return execution.execute(request, body);
        });
        return restTemplate;
    }
}
