package com.smartlogix.inventory;

import com.smartlogix.inventory.entity.Product;
import com.smartlogix.inventory.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.test.context.TestPropertySource;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@TestPropertySource(properties = {
        "spring.sql.init.mode=never",
        "spring.jpa.defer-datasource-initialization=false"
})
class ProductRepositoryTest {

    @Autowired
    private ProductRepository productRepository;

    private Product createProduct(String name, String brand, String fragrance, BigDecimal price, int stock) {
        return Product.builder()
                .name(name).brand(brand).description("Test")
                .price(price).stockQuantity(stock).fragrance(fragrance)
                .build();
    }

    @Test
    void findByBrand_shouldReturnMatchingProducts() {
        productRepository.save(createProduct("Sauvage", "Dior", "Amaderado", new BigDecimal("120"), 50));
        productRepository.save(createProduct("Bleu", "Chanel", "Cítrico", new BigDecimal("135"), 40));
        List<Product> result = productRepository.findByBrand("Dior");
        assertEquals(1, result.size());
        assertEquals("Sauvage", result.get(0).getName());
    }

    @Test
    void findByFragrance_shouldReturnMatchingProducts() {
        productRepository.save(createProduct("Sauvage", "Dior", "Amaderado", new BigDecimal("120"), 50));
        List<Product> result = productRepository.findByFragrance("Amaderado");
        assertEquals(1, result.size());
    }

    @Test
    void findByPriceRange_shouldReturnProductsInRange() {
        productRepository.save(createProduct("Cheap", "A", "Floral", new BigDecimal("30"), 10));
        productRepository.save(createProduct("Mid", "B", "Floral", new BigDecimal("100"), 20));
        productRepository.save(createProduct("Expensive", "C", "Floral", new BigDecimal("300"), 5));
        List<Product> result = productRepository.findByPriceRange(new BigDecimal("50"), new BigDecimal("200"));
        assertEquals(1, result.size());
        assertEquals("Mid", result.get(0).getName());
    }

    @Test
    void findInStock_shouldReturnOnlyPositiveStock() {
        productRepository.save(createProduct("InStock", "A", "Floral", new BigDecimal("50"), 10));
        productRepository.save(createProduct("OutOfStock", "B", "Floral", new BigDecimal("50"), 0));
        List<Product> result = productRepository.findInStock();
        assertEquals(1, result.size());
        assertEquals("InStock", result.get(0).getName());
    }

    @Test
    void findByNameContainingIgnoreCase_shouldReturnMatches() {
        productRepository.save(createProduct("Sauvage EDP", "Dior", "Amaderado", new BigDecimal("120"), 50));
        productRepository.save(createProduct("Bleu de Chanel", "Chanel", "Cítrico", new BigDecimal("135"), 40));
        List<Product> result = productRepository.findByNameContainingIgnoreCase("sauvage");
        assertEquals(1, result.size());
    }
}
