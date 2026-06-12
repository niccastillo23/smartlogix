package com.smartlogix.order.factory;

import com.smartlogix.order.dto.OrderItemDTO;
import com.smartlogix.order.dto.OrderRequest;
import com.smartlogix.order.entity.Order;
import com.smartlogix.order.entity.OrderItem;

import java.math.BigDecimal;
import java.util.List;

public abstract class OrderFactory {

    public Order createOrder(OrderRequest request) {
        Order order = Order.builder()
                .customerId(request.getCustomerId())
                .customerName(request.getCustomerName())
                .email(request.getEmail())
                .orderType(getOrderType())
                .status("PENDING")
                .discountApplied(getDiscount())
                .shippingMethod(getShippingMethod())
                .build();

        List<OrderItem> items = request.getItems().stream()
                .map(this::buildOrderItem)
                .toList();

        items.forEach(order::addItem);

        BigDecimal subtotal = items.stream()
                .map(OrderItem::getSubtotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal discount = subtotal.multiply(getDiscount().divide(new BigDecimal("100")));
        order.setTotalAmount(subtotal.subtract(discount));

        return order;
    }

    protected abstract String getOrderType();

    protected abstract BigDecimal getDiscount();

    protected abstract String getShippingMethod();

    private OrderItem buildOrderItem(OrderItemDTO dto) {
        BigDecimal subtotal = dto.getUnitPrice().multiply(new BigDecimal(dto.getQuantity()));
        return OrderItem.builder()
                .productId(dto.getProductId())
                .productName(dto.getProductName())
                .quantity(dto.getQuantity())
                .unitPrice(dto.getUnitPrice())
                .subtotal(subtotal)
                .build();
    }
}
