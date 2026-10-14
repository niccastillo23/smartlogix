package com.smartlogix.inventory;

import com.smartlogix.inventory.entity.Product;
import com.smartlogix.inventory.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Regresión: con la semilla de data.sql (IDs 1..11 explícitos) el alta de un producto
 * debe asignar un ID nuevo. Antes fallaba con "PRIMARY KEY ON PUBLIC.PRODUCT(ID)".
 */
@SpringBootTest
class ProductSeedIdIntegrationTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void altaDeProductoConSemilla_asignaIdNuevoSinViolarClavePrimaria() {
        long antes = productRepository.count();
        Product nuevo = Product.builder()
                .name("Prueba de regresión").brand("Test").description("alta")
                .price(new BigDecimal("10.00")).stockQuantity(1).fragrance("Test")
                .build();

        Product guardado = productRepository.save(nuevo);

        assertNotNull(guardado.getId());
        assertTrue(guardado.getId() > 11, "El ID debe superar los IDs de la semilla");
        assertTrue(productRepository.count() == antes + 1);
    }
}
