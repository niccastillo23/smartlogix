package com.smartlogix.order.factory;

import org.springframework.stereotype.Component;
import java.math.BigDecimal;

@Component
public class MarketplaceOrderFactory extends OrderFactory {

    @Override
    protected String getOrderType() {
        return "MARKETPLACE";
    }

    @Override
    protected BigDecimal getDiscount() {
        return new BigDecimal("10.00");
    }

    @Override
    protected String getShippingMethod() {
        return "EXPRESS";
    }
}
