package com.smartlogix.order;

import com.smartlogix.order.dto.OrderItemDTO;
import com.smartlogix.order.dto.OrderRequest;
import com.smartlogix.order.dto.OrderResponse;
import com.smartlogix.order.entity.Order;
import com.smartlogix.order.entity.OrderItem;
import com.smartlogix.order.factory.MarketplaceOrderFactory;
import com.smartlogix.order.factory.WebOrderFactory;
import com.smartlogix.order.repository.OrderRepository;
import com.smartlogix.order.service.OrderService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @InjectMocks
    private OrderService orderService;

    private WebOrderFactory webOrderFactory;
    private MarketplaceOrderFactory marketplaceOrderFactory;

    private OrderRequest buildWebRequest() {
        return OrderRequest.builder()
                .customerId(1L)
                .customerName("Juan Pérez")
                .email("juan@test.com")
                .orderType("WEB")
                .items(List.of(
                        OrderItemDTO.builder()
                                .productId(1L)
                                .productName("Sauvage")
                                .quantity(2)
                                .unitPrice(new BigDecimal("120.00"))
                                .build()
                ))
                .build();
    }

    private OrderRequest buildMarketplaceRequest() {
        return OrderRequest.builder()
                .customerId(2L)
                .customerName("María López")
                .email("maria@test.com")
                .orderType("MARKETPLACE")
                .items(List.of(
                        OrderItemDTO.builder()
                                .productId(2L)
                                .productName("Bleu de Chanel")
                                .quantity(1)
                                .unitPrice(new BigDecimal("135.00"))
                                .build()
                ))
                .build();
    }

    private Order buildSavedOrder(String type) {
        Order order = Order.builder()
                .id(1L)
                .customerId(1L)
                .customerName("Juan Pérez")
                .email("juan@test.com")
                .orderType(type)
                .status("PENDING")
                .discountApplied(type.equals("WEB") ? new BigDecimal("5.00") : new BigDecimal("10.00"))
                .shippingMethod(type.equals("WEB") ? "STANDARD" : "EXPRESS")
                .totalAmount(new BigDecimal("228.00"))
                .build();

        OrderItem item = OrderItem.builder()
                .id(1L)
                .productId(1L)
                .productName("Sauvage")
                .quantity(2)
                .unitPrice(new BigDecimal("120.00"))
                .subtotal(new BigDecimal("240.00"))
                .build();
        order.addItem(item);
        return order;
    }

    @BeforeEach
    void setUp() {
        webOrderFactory = new WebOrderFactory();
        marketplaceOrderFactory = new MarketplaceOrderFactory();
        orderService = new OrderService(orderRepository, webOrderFactory, marketplaceOrderFactory);
    }

    @Test
    void getAllOrders_shouldReturnList() {
        when(orderRepository.findAll()).thenReturn(List.of(buildSavedOrder("WEB")));
        List<OrderResponse> result = orderService.getAllOrders();
        assertEquals(1, result.size());
    }

    @Test
    void getOrderById_found_shouldReturnResponse() {
        when(orderRepository.findById(1L)).thenReturn(Optional.of(buildSavedOrder("WEB")));
        OrderResponse result = orderService.getOrderById(1L);
        assertNotNull(result);
        assertEquals("WEB", result.getOrderType());
    }

    @Test
    void getOrderById_notFound_shouldThrow() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> orderService.getOrderById(99L));
    }

    @Test
    void getOrdersByCustomer_shouldReturnList() {
        when(orderRepository.findByCustomerId(1L)).thenReturn(List.of(buildSavedOrder("WEB")));
        List<OrderResponse> result = orderService.getOrdersByCustomer(1L);
        assertEquals(1, result.size());
    }

    @Test
    void getOrdersByStatus_shouldReturnList() {
        when(orderRepository.findByStatus("PENDING")).thenReturn(List.of(buildSavedOrder("WEB")));
        List<OrderResponse> result = orderService.getOrdersByStatus("PENDING");
        assertEquals(1, result.size());
    }

    @Test
    void createOrder_web_shouldApplyWebDiscount() {
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> {
            Order o = inv.getArgument(0);
            o.setId(1L);
            return o;
        });
        OrderResponse result = orderService.createOrder(buildWebRequest());
        assertEquals("WEB", result.getOrderType());
        assertEquals("STANDARD", result.getShippingMethod());
        assertEquals(new BigDecimal("5.00"), result.getDiscountApplied());
        assertTrue(result.getTotalAmount().compareTo(new BigDecimal("240.00")) < 0);
    }

    @Test
    void createOrder_marketplace_shouldApplyMarketplaceDiscount() {
        when(orderRepository.save(any(Order.class))).thenAnswer(inv -> {
            Order o = inv.getArgument(0);
            o.setId(2L);
            return o;
        });
        OrderResponse result = orderService.createOrder(buildMarketplaceRequest());
        assertEquals("MARKETPLACE", result.getOrderType());
        assertEquals("EXPRESS", result.getShippingMethod());
        assertEquals(new BigDecimal("10.00"), result.getDiscountApplied());
    }

    @Test
    void createOrder_invalidType_shouldThrow() {
        OrderRequest bad = OrderRequest.builder()
                .customerId(1L).customerName("Test").email("t@t.com")
                .orderType("INVALID")
                .items(List.of(OrderItemDTO.builder().productId(1L).productName("X").quantity(1).unitPrice(new BigDecimal("10")).build()))
                .build();
        assertThrows(RuntimeException.class, () -> orderService.createOrder(bad));
    }

    @Test
    void updateOrderStatus_found_shouldUpdate() {
        Order order = buildSavedOrder("WEB");
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));
        when(orderRepository.save(any(Order.class))).thenReturn(order);
        OrderResponse result = orderService.updateOrderStatus(1L, "CONFIRMED");
        assertEquals("CONFIRMED", result.getStatus());
    }

    @Test
    void updateOrderStatus_notFound_shouldThrow() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> orderService.updateOrderStatus(99L, "CONFIRMED"));
    }
}
