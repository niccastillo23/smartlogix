package com.smartlogix.order.dto;

import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderResponse {
    private Long id;
    private Long customerId;
    private String customerName;
    private String email;
    private List<OrderItemDTO> items;
    private BigDecimal totalAmount;
    private String orderType;
    private String status;
    private BigDecimal discountApplied;
    private String shippingMethod;
    private LocalDateTime createdAt;
}
