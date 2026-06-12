package com.smartlogix.shipping.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI shippingOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("SmartLogix Shipping Service API")
                        .description("API REST para gestión de envíos de perfumes - Circuit Breaker Pattern")
                        .version("1.0.0"));
    }
}
