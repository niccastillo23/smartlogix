package com.smartlogix.shipping.dto;

import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ShippingResponse {
    private Long id;
    private Long orderId;
    private String carrier;
    private String trackingNumber;
    private String status;
    private LocalDate estimatedDelivery;
    private String address;
    private String city;
    private String country;
    private Boolean circuitBreakerFallback;
    private LocalDateTime createdAt;
}
