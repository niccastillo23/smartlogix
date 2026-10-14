package com.smartlogix.order.service;

import com.smartlogix.order.exception.ResourceNotFoundException;
import com.smartlogix.order.dto.OrderItemDTO;
import com.smartlogix.order.dto.OrderRequest;
import com.smartlogix.order.dto.OrderResponse;
import com.smartlogix.order.entity.Order;
import com.smartlogix.order.factory.MarketplaceOrderFactory;
import com.smartlogix.order.factory.OrderFactory;
import com.smartlogix.order.factory.WebOrderFactory;
import com.smartlogix.order.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final WebOrderFactory webOrderFactory;
    private final MarketplaceOrderFactory marketplaceOrderFactory;

    public List<OrderResponse> getAllOrders() {
        return orderRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    public OrderResponse getOrderById(Long id) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Pedido no encontrado con id: " + id));
        return toResponse(order);
    }

    public List<OrderResponse> getOrdersByCustomer(Long customerId) {
        return orderRepository.findByCustomerId(customerId).stream()
                .map(this::toResponse)
                .toList();
    }

    public List<OrderResponse> getOrdersByStatus(String status) {
        return orderRepository.findByStatus(status).stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public OrderResponse createOrder(OrderRequest request) {
        OrderFactory factory = resolveFactory(request.getOrderType());
        Order order = factory.createOrder(request);
        Order saved = orderRepository.save(order);
        return toResponse(saved);
    }

    @Transactional
    public OrderResponse updateOrderStatus(Long id, String status) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Pedido no encontrado con id: " + id));
        order.setStatus(status);
        Order saved = orderRepository.save(order);
        return toResponse(saved);
    }

    private OrderFactory resolveFactory(String orderType) {
        return switch (orderType.toUpperCase()) {
            case "WEB" -> webOrderFactory;
            case "MARKETPLACE" -> marketplaceOrderFactory;
            default -> throw new IllegalArgumentException("Tipo de orden no soportado: " + orderType);
        };
    }

    private OrderResponse toResponse(Order order) {
        List<OrderItemDTO> items = order.getItems().stream()
                .map(item -> OrderItemDTO.builder()
                        .productId(item.getProductId())
                        .productName(item.getProductName())
                        .quantity(item.getQuantity())
                        .unitPrice(item.getUnitPrice())
                        .build())
                .toList();

        return OrderResponse.builder()
                .id(order.getId())
                .customerId(order.getCustomerId())
                .customerName(order.getCustomerName())
                .email(order.getEmail())
                .items(items)
                .totalAmount(order.getTotalAmount())
                .orderType(order.getOrderType())
                .status(order.getStatus())
                .discountApplied(order.getDiscountApplied())
                .shippingMethod(order.getShippingMethod())
                .createdAt(order.getCreatedAt())
                .build();
    }
}
