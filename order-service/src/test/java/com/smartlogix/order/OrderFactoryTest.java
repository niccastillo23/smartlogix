package com.smartlogix.order;

import com.smartlogix.order.dto.OrderItemDTO;
import com.smartlogix.order.dto.OrderRequest;
import com.smartlogix.order.entity.Order;
import com.smartlogix.order.factory.MarketplaceOrderFactory;
import com.smartlogix.order.factory.WebOrderFactory;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class OrderFactoryTest {

    private OrderRequest buildRequest(String type) {
        return OrderRequest.builder()
                .customerId(1L)
                .customerName("Test User")
                .email("test@test.com")
                .orderType(type)
                .items(List.of(
                        OrderItemDTO.builder()
                                .productId(1L)
                                .productName("Sauvage")
                                .quantity(2)
                                .unitPrice(new BigDecimal("100.00"))
                                .build()
                ))
                .build();
    }

    @Test
    void webFactory_shouldCreateWebOrderWith5PercentDiscount() {
        WebOrderFactory factory = new WebOrderFactory();
        Order order = factory.createOrder(buildRequest("WEB"));

        assertEquals("WEB", order.getOrderType());
        assertEquals("STANDARD", order.getShippingMethod());
        assertEquals(new BigDecimal("5.00"), order.getDiscountApplied());
        assertEquals("PENDING", order.getStatus());
        assertEquals(1, order.getItems().size());
        assertEquals(0, new BigDecimal("190.00").compareTo(order.getTotalAmount()));
    }

    @Test
    void marketplaceFactory_shouldCreateMarketplaceOrderWith10PercentDiscount() {
        MarketplaceOrderFactory factory = new MarketplaceOrderFactory();
        Order order = factory.createOrder(buildRequest("MARKETPLACE"));

        assertEquals("MARKETPLACE", order.getOrderType());
        assertEquals("EXPRESS", order.getShippingMethod());
        assertEquals(new BigDecimal("10.00"), order.getDiscountApplied());
        assertEquals("PENDING", order.getStatus());
        assertEquals(1, order.getItems().size());
        assertEquals(0, new BigDecimal("180.00").compareTo(order.getTotalAmount()));
    }

    @Test
    void factory_shouldCalculateSubtotalCorrectly() {
        WebOrderFactory factory = new WebOrderFactory();
        Order order = factory.createOrder(buildRequest("WEB"));

        assertEquals(new BigDecimal("200.00"), order.getItems().get(0).getSubtotal());
        assertEquals(2, order.getItems().get(0).getQuantity());
    }

    @Test
    void factory_shouldSetCustomerData() {
        WebOrderFactory factory = new WebOrderFactory();
        Order order = factory.createOrder(buildRequest("WEB"));

        assertEquals(1L, order.getCustomerId());
        assertEquals("Test User", order.getCustomerName());
        assertEquals("test@test.com", order.getEmail());
    }
}
