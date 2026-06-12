package com.smartlogix.order.factory;

import org.springframework.stereotype.Component;
import java.math.BigDecimal;

@Component
public class WebOrderFactory extends OrderFactory {

    @Override
    protected String getOrderType() {
        return "WEB";
    }

    @Override
    protected BigDecimal getDiscount() {
        return new BigDecimal("5.00");
    }

    @Override
    protected String getShippingMethod() {
        return "STANDARD";
    }
}
