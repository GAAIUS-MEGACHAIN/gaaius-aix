import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ShoppingCart, Plus, Package, TrendingUp, DollarSign } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #84cc16 0%, #4b5320 100%);
  border-radius: 12px;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 20px;
`;

const Title = styled.h2`
  font-size: 28px;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
`;

const Button = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const StatRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 8px 0;
`;

const ECommerceTab = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const mockProducts = [
    {
      product_id: '1',
      name: 'Premium Headphones',
      price: 199.99,
      stock: 45,
      sales: 234,
      revenue: 46796.66
    },
    {
      product_id: '2',
      name: 'Wireless Keyboard',
      price: 79.99,
      stock: 123,
      sales: 567,
      revenue: 45329.33
    },
    {
      product_id: '3',
      name: 'Smart Watch',
      price: 299.99,
      stock: 12,
      sales: 89,
      revenue: 26699.11
    },
    {
      product_id: '4',
      name: 'USB-C Cable',
      price: 19.99,
      stock: 456,
      sales: 1200,
      revenue: 23988
    }
  ];

  return (
    <Container>
      <Header>
        <Title>
          <ShoppingCart size={32} />
          E-Commerce
        </Title>
        <Button style={{ width: 'auto' }}>
          <Plus size={16} style={{ display: 'inline', marginRight: '5px' }} />
          Add Product
        </Button>
      </Header>

      <GridContainer>
        {mockProducts.map((product) => (
          <Card key={product.product_id}>
            <h3 style={{ margin: '0 0 10px 0' }}>{product.name}</h3>
            <StatRow>
              <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
                ${product.price}
              </span>
            </StatRow>
            <StatRow>
              <span>
                <Package size={16} style={{ display: 'inline', marginRight: '5px' }} />
                Stock: {product.stock}
              </span>
            </StatRow>
            <StatRow>
              <span>
                <TrendingUp size={16} style={{ display: 'inline', marginRight: '5px' }} />
                Sales: {product.sales}
              </span>
            </StatRow>
            <StatRow style={{ marginTop: '15px', fontSize: '15px', fontWeight: 'bold' }}>
              <span>
                <DollarSign size={16} style={{ display: 'inline', marginRight: '5px' }} />
                Revenue: ${product.revenue.toFixed(2)}
              </span>
            </StatRow>
            <Button style={{ marginTop: '15px' }}>Edit Product</Button>
            <Button style={{ marginTop: '10px' }}>Analytics</Button>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default ECommerceTab;
