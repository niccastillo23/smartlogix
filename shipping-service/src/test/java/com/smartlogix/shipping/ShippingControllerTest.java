package com.smartlogix.shipping;

import com.smartlogix.shipping.controller.ShippingController;
import com.smartlogix.shipping.dto.ShippingRequest;
import com.smartlogix.shipping.dto.ShippingResponse;
import com.smartlogix.shipping.service.ShippingService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ShippingController.class)
class ShippingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ShippingService shippingService;

    @Autowired
    private ObjectMapper objectMapper;

    private ShippingResponse buildResponse() {
        return ShippingResponse.builder()
                .id(1L).orderId(100L).carrier("DHL")
                .trackingNumber("TRK-ABC12345").status("REGISTERED")
                .estimatedDelivery(LocalDate.now().plusDays(3))
                .address("Calle 123").city("Lima").country("Perú")
                .circuitBreakerFallback(false).createdAt(LocalDateTime.now())
                .build();
    }

    @Test
    void getAllShipments_shouldReturn200() throws Exception {
        when(shippingService.getAllShipments()).thenReturn(List.of(buildResponse()));
        mockMvc.perform(get("/api/shipments"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].carrier").value("DHL"));
    }

    @Test
    void getShipmentById_shouldReturn200() throws Exception {
        when(shippingService.getShipmentById(1L)).thenReturn(buildResponse());
        mockMvc.perform(get("/api/shipments/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.trackingNumber").value("TRK-ABC12345"));
    }

    @Test
    void getShipmentByOrderId_shouldReturn200() throws Exception {
        when(shippingService.getShipmentByOrderId(100L)).thenReturn(buildResponse());
        mockMvc.perform(get("/api/shipments/order/100"))
                .andExpect(status().isOk());
    }

    @Test
    void getByStatus_shouldReturn200() throws Exception {
        when(shippingService.getShipmentsByStatus("REGISTERED")).thenReturn(List.of(buildResponse()));
        mockMvc.perform(get("/api/shipments/status/REGISTERED"))
                .andExpect(status().isOk());
    }

    @Test
    void createShipment_shouldReturn201() throws Exception {
        when(shippingService.createShipment(any())).thenReturn(buildResponse());
        ShippingRequest req = ShippingRequest.builder()
                .orderId(100L).carrier("DHL").address("Calle 123").city("Lima").country("Perú").build();
        mockMvc.perform(post("/api/shipments")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.carrier").value("DHL"));
    }

    @Test
    void updateStatus_shouldReturn200() throws Exception {
        ShippingResponse resp = buildResponse();
        resp.setStatus("IN_TRANSIT");
        when(shippingService.updateShipmentStatus(eq(1L), eq("IN_TRANSIT"))).thenReturn(resp);
        mockMvc.perform(patch("/api/shipments/1/status?status=IN_TRANSIT"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("IN_TRANSIT"));
    }
}
