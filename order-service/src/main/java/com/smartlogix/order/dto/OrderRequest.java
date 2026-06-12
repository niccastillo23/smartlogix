package com.smartlogix.order.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.*;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderRequest {

    @NotNull(message = "El customerId es obligatorio")
    private Long customerId;

    @NotBlank(message = "El nombre del cliente es obligatorio")
    private String customerName;

    @NotBlank(message = "El email es obligatorio")
    @Email(message = "Email inválido")
    private String email;

    @NotBlank(message = "El tipo de orden es obligatorio")
    private String orderType;

    @NotEmpty(message = "Debe incluir al menos un item")
    @Valid
    private List<OrderItemDTO> items;
}
