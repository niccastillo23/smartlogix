package com.smartlogix.inventory;

import com.smartlogix.inventory.dto.ProductDTO;
import com.smartlogix.inventory.dto.StockUpdateRequest;
import com.smartlogix.inventory.entity.Product;
import com.smartlogix.inventory.repository.ProductRepository;
import com.smartlogix.inventory.service.ProductService;
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
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    private Product sampleProduct;
    private ProductDTO sampleDTO;

    @BeforeEach
    void setUp() {
        sampleProduct = Product.builder()
                .id(1L)
                .name("Sauvage")
                .brand("Dior")
                .description("Fragancia masculina")
                .price(new BigDecimal("120.00"))
                .stockQuantity(50)
                .fragrance("Amaderado")
                .build();

        sampleDTO = ProductDTO.builder()
                .id(1L)
                .name("Sauvage")
                .brand("Dior")
                .description("Fragancia masculina")
                .price(new BigDecimal("120.00"))
                .stockQuantity(50)
                .fragrance("Amaderado")
                .build();
    }

    @Test
    void getAllProducts_shouldReturnList() {
        when(productRepository.findAll()).thenReturn(List.of(sampleProduct));
        List<ProductDTO> result = productService.getAllProducts();
        assertEquals(1, result.size());
        assertEquals("Sauvage", result.get(0).getName());
        verify(productRepository).findAll();
    }

    @Test
    void getProductById_found_shouldReturnDTO() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(sampleProduct));
        ProductDTO result = productService.getProductById(1L);
        assertNotNull(result);
        assertEquals("Dior", result.getBrand());
    }

    @Test
    void getProductById_notFound_shouldThrow() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> productService.getProductById(99L));
    }

    @Test
    void getProductsByBrand_shouldReturnFilteredList() {
        when(productRepository.findByBrand("Dior")).thenReturn(List.of(sampleProduct));
        List<ProductDTO> result = productService.getProductsByBrand("Dior");
        assertEquals(1, result.size());
    }

    @Test
    void getProductsByFragrance_shouldReturnFilteredList() {
        when(productRepository.findByFragrance("Amaderado")).thenReturn(List.of(sampleProduct));
        List<ProductDTO> result = productService.getProductsByFragrance("Amaderado");
        assertEquals(1, result.size());
    }

    @Test
    void getProductsByPriceRange_shouldReturnFilteredList() {
        BigDecimal min = new BigDecimal("50");
        BigDecimal max = new BigDecimal("200");
        when(productRepository.findByPriceRange(min, max)).thenReturn(List.of(sampleProduct));
        List<ProductDTO> result = productService.getProductsByPriceRange(min, max);
        assertEquals(1, result.size());
    }

    @Test
    void getInStockProducts_shouldReturnOnlyInStock() {
        when(productRepository.findInStock()).thenReturn(List.of(sampleProduct));
        List<ProductDTO> result = productService.getInStockProducts();
        assertTrue(result.stream().allMatch(p -> p.getStockQuantity() > 0));
    }

    @Test
    void searchProducts_shouldReturnMatchingProducts() {
        when(productRepository.findByNameContainingIgnoreCase("sauv")).thenReturn(List.of(sampleProduct));
        List<ProductDTO> result = productService.searchProducts("sauv");
        assertEquals(1, result.size());
    }

    @Test
    void createProduct_shouldSaveAndReturnDTO() {
        when(productRepository.save(any(Product.class))).thenReturn(sampleProduct);
        ProductDTO result = productService.createProduct(sampleDTO);
        assertNotNull(result.getId());
        assertEquals("Sauvage", result.getName());
        verify(productRepository).save(any(Product.class));
    }

    @Test
    void updateProduct_found_shouldUpdateAndReturn() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(sampleProduct));
        when(productRepository.save(any(Product.class))).thenReturn(sampleProduct);
        sampleDTO.setName("Sauvage Elixir");
        ProductDTO result = productService.updateProduct(1L, sampleDTO);
        assertEquals("Sauvage Elixir", result.getName());
    }

    @Test
    void updateProduct_notFound_shouldThrow() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> productService.updateProduct(99L, sampleDTO));
    }

    @Test
    void updateStock_shouldUpdateQuantity() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(sampleProduct));
        when(productRepository.save(any(Product.class))).thenReturn(sampleProduct);
        StockUpdateRequest request = new StockUpdateRequest(100);
        ProductDTO result = productService.updateStock(1L, request);
        assertNotNull(result);
    }

    @Test
    void updateStock_notFound_shouldThrow() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());
        assertThrows(RuntimeException.class, () -> productService.updateStock(99L, new StockUpdateRequest(10)));
    }

    @Test
    void deleteProduct_exists_shouldDelete() {
        when(productRepository.existsById(1L)).thenReturn(true);
        productService.deleteProduct(1L);
        verify(productRepository).deleteById(1L);
    }

    @Test
    void deleteProduct_notExists_shouldThrow() {
        when(productRepository.existsById(99L)).thenReturn(false);
        assertThrows(RuntimeException.class, () -> productService.deleteProduct(99L));
    }
}
