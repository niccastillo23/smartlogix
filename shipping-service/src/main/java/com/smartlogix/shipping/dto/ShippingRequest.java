package com.smartlogix.shipping.dto;

import jakarta.validation.constraints.*;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ShippingRequest {

    @NotNull(message = "El orderId es obligatorio")
    private Long orderId;

    @NotBlank(message = "El carrier es obligatorio")
    private String carrier;

    @NotBlank(message = "La dirección es obligatoria")
    private String address;

    @NotBlank(message = "La ciudad es obligatoria")
    private String city;

    @NotBlank(message = "El país es obligatorio")
    private String country;
}
