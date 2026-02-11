import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

// ==================== STYLED COMPONENTS ====================

const ProductBrowserContainer = styled.div`
  padding: 20px;
  background: #f5f5f5;
  border-radius: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const BrowserHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 24px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SearchContainer = styled.div`
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 250px;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SearchButton = styled.button`
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
`;

const FilterContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
`;

const FilterTag = styled.button`
  padding: 8px 16px;
  border: 2px solid ${props => props.active ? '#667eea' : '#e0e0e0'};
  background: ${props => props.active ? '#667eea' : 'white'};
  color: ${props => props.active ? 'white' : '#333'};
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;

  &:hover {
    border-color: #667eea;
    color: ${props => props.active ? 'white' : '#667eea'};
  }
`;

const ProductGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }

  @media (max-width: 480px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
`;

const ProductCard = styled.div`
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
`;

const ProductImage = styled.img`
  width: 100%;
  height: 150px;
  object-fit: cover;
  background: #f0f0f0;
`;

const ProductInfo = styled.div`
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const ProductName = styled.div`
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ProductRating = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #999;
`;

const ProductPrice = styled.div`
  font-size: 16px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
`;

const ProductStatus = styled.div`
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  background: ${props => {
    switch(props.status) {
      case 'active': return '#d4edda';
      case 'limited': return '#fff3cd';
      case 'out_of_stock': return '#f8d7da';
      default: return '#e2e3e5';
    }
  }};
  color: ${props => {
    switch(props.status) {
      case 'active': return '#155724';
      case 'limited': return '#856404';
      case 'out_of_stock': return '#721c24';
      default: return '#383d41';
    }
  }};
  text-align: center;
  margin-bottom: 8px;
`;

const AddToCartButton = styled.button`
  width: 100%;
  padding: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.3s;
  margin-top: auto;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
`;

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #999;

  div {
    font-size: 48px;
    margin-bottom: 12px;
  }
`;

const DiscountBadge = styled.div`
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff4757;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
`;

const ProductCardWrapper = styled.div`
  position: relative;
`;

// ==================== COMPONENT ====================

const ProductBrowser = ({ 
  contentId, 
  contentType, 
  userId, 
  onAddToCart,
  showSearch = true,
  showFilters = true
}) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categories, setCategories] = useState([]);
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    if (contentId && contentType) {
      fetchProductsByContent();
    } else {
      fetchAllProducts();
    }
  }, [contentId, contentType]);

  const fetchProductsByContent = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${backendUrl}/api/products/content/${contentId}?content_type=${contentType}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setProducts(response.data.products || []);
      extractCategories(response.data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllProducts = async () => {
    try {
      setLoading(true);
      // Placeholder - in real app, would fetch from /api/products
      setProducts([]);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const response = await axios.get(
        `${backendUrl}/api/products/search?query=${encodeURIComponent(searchQuery)}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setProducts(response.data.products || []);
      extractCategories(response.data.products || []);
    } catch (error) {
      console.error('Error searching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const extractCategories = (productList) => {
    const cats = [...new Set(productList.map(p => p.category))];
    setCategories(cats);
  };

  const handleAddToCart = async (product) => {
    try {
      await axios.post(
        `${backendUrl}/api/cart/${userId}/add`,
        {
          product_id: product.id,
          quantity: 1
        },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      
      if (onAddToCart) {
        onAddToCart(product);
      }

      // Show toast notification
      alert(`✅ ${product.name} added to cart!`);
    } catch (error) {
      console.error('Error adding to cart:', error);
      alert('Failed to add to cart');
    }
  };

  const filteredProducts = selectedCategory 
    ? products.filter(p => p.category === selectedCategory)
    : products;

  return (
    <ProductBrowserContainer>
      {showSearch && (
        <BrowserHeader>
          <Title>🛍️ Live Shopping</Title>
          <SearchContainer>
            <SearchInput
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <SearchButton onClick={handleSearch}>Search</SearchButton>
          </SearchContainer>
        </BrowserHeader>
      )}

      {showFilters && categories.length > 0 && (
        <FilterContainer>
          <FilterTag 
            active={selectedCategory === null}
            onClick={() => setSelectedCategory(null)}
          >
            All Products
          </FilterTag>
          {categories.map(cat => (
            <FilterTag
              key={cat}
              active={selectedCategory === cat}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </FilterTag>
          ))}
        </FilterContainer>
      )}

      {loading ? (
        <LoadingContainer>
          <LoadingSpinner />
        </LoadingContainer>
      ) : filteredProducts.length === 0 ? (
        <EmptyState>
          <div>🔍</div>
          <div>No products available</div>
          <div style={{ fontSize: '12px', marginTop: '8px', color: '#bbb' }}>
            Try searching or browsing different categories
          </div>
        </EmptyState>
      ) : (
        <ProductGrid>
          {filteredProducts.map(product => (
            <ProductCardWrapper key={product.id}>
              {product.discount_percent > 0 && (
                <DiscountBadge>-{product.discount_percent}%</DiscountBadge>
              )}
              <ProductCard>
                <ProductImage 
                  src={product.thumbnail_url || 'https://via.placeholder.com/200x150'}
                  alt={product.name}
                />
                <ProductInfo>
                  <ProductName>{product.name}</ProductName>
                  <ProductRating>
                    {'⭐'.repeat(Math.round(product.rating || 0))}
                    {product.reviews_count > 0 && ` (${product.reviews_count})`}
                  </ProductRating>
                  <ProductPrice>${product.base_price}</ProductPrice>
                  <ProductStatus status={product.status}>
                    {product.status === 'out_of_stock' ? 'Out of Stock' : 
                     product.status === 'limited' ? 'Limited Stock' :
                     product.total_inventory > 0 ? 'In Stock' : 'Check Back'}
                  </ProductStatus>
                  <AddToCartButton
                    onClick={() => handleAddToCart(product)}
                    disabled={product.status === 'out_of_stock'}
                  >
                    {product.status === 'out_of_stock' ? 'Out of Stock' : 'Add to Cart'}
                  </AddToCartButton>
                </ProductInfo>
              </ProductCard>
            </ProductCardWrapper>
          ))}
        </ProductGrid>
      )}
    </ProductBrowserContainer>
  );
};

export default ProductBrowser;
