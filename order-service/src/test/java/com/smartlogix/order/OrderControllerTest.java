package com.smartlogix.order;

import com.smartlogix.order.dto.OrderItemDTO;
import com.smartlogix.order.dto.OrderRequest;
import com.smartlogix.order.dto.OrderResponse;
import com.smartlogix.order.controller.OrderController;
import com.smartlogix.order.service.OrderService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(OrderController.class)
@org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc(addFilters = false)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Autowired
    private ObjectMapper objectMapper;

    private OrderResponse buildResponse() {
        return OrderResponse.builder()
                .id(1L)
                .customerId(1L)
                .customerName("Juan Pérez")
                .email("juan@test.com")
                .orderType("WEB")
                .status("PENDING")
                .totalAmount(new BigDecimal("228.00"))
                .discountApplied(new BigDecimal("5.00"))
                .shippingMethod("STANDARD")
                .items(List.of(OrderItemDTO.builder()
                        .productId(1L).productName("Sauvage").quantity(2).unitPrice(new BigDecimal("120.00")).build()))
                .build();
    }

    @Test
    void getAllOrders_shouldReturn200() throws Exception {
        when(orderService.getAllOrders()).thenReturn(List.of(buildResponse()));
        mockMvc.perform(get("/api/orders"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].orderType").value("WEB"));
    }

    @Test
    void getOrderById_shouldReturn200() throws Exception {
        when(orderService.getOrderById(1L)).thenReturn(buildResponse());
        mockMvc.perform(get("/api/orders/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerName").value("Juan Pérez"));
    }

    @Test
    void getOrdersByCustomer_shouldReturn200() throws Exception {
        when(orderService.getOrdersByCustomer(1L)).thenReturn(List.of(buildResponse()));
        mockMvc.perform(get("/api/orders/customer/1"))
                .andExpect(status().isOk());
    }

    @Test
    void getOrdersByStatus_shouldReturn200() throws Exception {
        when(orderService.getOrdersByStatus("PENDING")).thenReturn(List.of(buildResponse()));
        mockMvc.perform(get("/api/orders/status/PENDING"))
                .andExpect(status().isOk());
    }

    @Test
    void createOrder_shouldReturn201() throws Exception {
        when(orderService.createOrder(any())).thenReturn(buildResponse());
        OrderRequest req = OrderRequest.builder()
                .customerId(1L).customerName("Juan Pérez").email("juan@test.com")
                .orderType("WEB")
                .items(List.of(OrderItemDTO.builder()
                        .productId(1L).productName("Sauvage").quantity(2).unitPrice(new BigDecimal("120.00")).build()))
                .build();
        mockMvc.perform(post("/api/orders")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.orderType").value("WEB"));
    }

    @Test
    void updateStatus_shouldReturn200() throws Exception {
        OrderResponse resp = buildResponse();
        resp.setStatus("CONFIRMED");
        when(orderService.updateOrderStatus(eq(1L), eq("CONFIRMED"))).thenReturn(resp);
        mockMvc.perform(patch("/api/orders/1/status?status=CONFIRMED"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CONFIRMED"));
    }
}
