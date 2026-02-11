import React, { useState } from 'react';
import styled from 'styled-components';
import {
  ShoppingCart, TrendingUp, Package, Truck, CreditCard,
  Plus, Edit, Trash2, Eye, Filter, Download, Search,
  ArrowUp, Star, Heart, Share2, ChevronRight
} from 'lucide-react';

// ============================================================================
// MODERN E-COMMERCE DASHBOARD STYLES
// ============================================================================

const DashboardContainer = styled.div`
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  min-height: 100vh;
  padding: 40px;
  font-family: 'Manrope', sans-serif;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(244, 114, 182, 0.3);
  }
`;

const SecondaryButton = styled(Button)`
  background: rgba(148, 163, 184, 0.1);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.2);
`;

// ============================================================================
// TABS
// ============================================================================

const TabsContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
`;

const Tab = styled.button`
  background: transparent;
  border: none;
  color: ${props => props.active ? '#f472b6' : 'rgba(226, 232, 240, 0.6)'};
  padding: 12px 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  border-bottom: 2px solid ${props => props.active ? '#f472b6' : 'transparent'};
  
  &:hover {
    color: #e2e8f0;
  }
`;

// ============================================================================
// PRODUCT CARDS
// ============================================================================

const ProductsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const ProductCard = styled.div`
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  
  &:hover {
    transform: translateY(-8px);
    border-color: rgba(244, 114, 182, 0.3);
    box-shadow: 0 20px 50px rgba(244, 114, 182, 0.1);
  }
`;

const ProductImage = styled.div`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, rgba(244, 114, 182, 0.2) 0%, rgba(236, 72, 153, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  svg {
    width: 60px;
    height: 60px;
    opacity: 0.5;
  }
`;

const ProductBadge = styled.span`
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
`;

const ProductInfo = styled.div`
  padding: 20px;
`;

const ProductName = styled.h3`
  font-size: 16px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 8px;
`;

const ProductPrice = styled.div`
  font-size: 20px;
  font-weight: 700;
  color: #f472b6;
  margin-bottom: 12px;
`;

const ProductStats = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
`;

const StatBadge = styled.span`
  background: rgba(244, 114, 182, 0.1);
  border: 1px solid rgba(244, 114, 182, 0.2);
  color: rgba(226, 232, 240, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
`;

const ProductActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

const IconButton = styled.button`
  flex: 1;
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  
  &:hover {
    background: rgba(244, 114, 182, 0.1);
    border-color: #f472b6;
    color: #f472b6;
  }
`;

// ============================================================================
// ORDERS TABLE
// ============================================================================

const TableContainer = styled.div`
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  
  table {
    width: 100%;
    border-collapse: collapse;
    
    thead {
      background: rgba(244, 114, 182, 0.05);
      border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    th {
      padding: 18px 24px;
      text-align: left;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: rgba(226, 232, 240, 0.7);
    }
    
    td {
      padding: 18px 24px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.1);
      color: #e2e8f0;
    }
    
    tbody tr {
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(244, 114, 182, 0.05);
      }
    }
  }
`;

const StatusBadge = styled.span`
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => {
    switch(props.status) {
      case 'completed': return 'rgba(16, 185, 129, 0.2)';
      case 'pending': return 'rgba(245, 158, 11, 0.2)';
      case 'processing': return 'rgba(59, 130, 246, 0.2)';
      case 'shipped': return 'rgba(168, 85, 247, 0.2)';
      default: return 'rgba(148, 163, 184, 0.2)';
    }
  }};
  color: ${props => {
    switch(props.status) {
      case 'completed': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'processing': return '#3b82f6';
      case 'shipped': return '#a855f7';
      default: return '#94a3b8';
    }
  }};
  border: 1px solid currentColor;
`;

// ============================================================================
// E-COMMERCE DASHBOARD COMPONENT
// ============================================================================

const ECommerceDashboard = () => {
  const [activeTab, setActiveTab] = useState('products');

  const mockProducts = [
    { id: 1, name: 'Premium Edition', price: 49.99, sales: 234, stock: 45, image: '📦' },
    { id: 2, name: 'Starter Pack', price: 19.99, sales: 521, stock: 120, image: '🎁' },
    { id: 3, name: 'Mega Bundle', price: 129.99, sales: 89, stock: 12, image: '⚡' },
    { id: 4, name: 'Limited Edition', price: 199.99, sales: 34, stock: 5, image: '👑' },
    { id: 5, name: 'Exclusive Box', price: 299.99, sales: 12, stock: 3, image: '💎' },
    { id: 6, name: 'Collector\'s Item', price: 499.99, sales: 5, stock: 1, image: '🌟' },
  ];

  const mockOrders = [
    { id: 'ORD001', customer: 'John Doe', product: 'Premium Edition', amount: 49.99, date: '2024-01-20', status: 'completed' },
    { id: 'ORD002', customer: 'Jane Smith', product: 'Starter Pack', amount: 19.99, date: '2024-01-20', status: 'processing' },
    { id: 'ORD003', customer: 'Mike Johnson', product: 'Mega Bundle', amount: 129.99, date: '2024-01-19', status: 'shipped' },
    { id: 'ORD004', customer: 'Sarah Lee', product: 'Limited Edition', amount: 199.99, date: '2024-01-19', status: 'pending' },
    { id: 'ORD005', customer: 'Tom Wilson', product: 'Exclusive Box', amount: 299.99, date: '2024-01-18', status: 'completed' },
  ];

  return (
    <DashboardContainer>
      {/* HEADER */}
      <Header>
        <Title>
          <ShoppingCart size={32} />
          E-Commerce Store
        </Title>
        <ActionButtons>
          <SecondaryButton>
            <Download size={18} />
            Export
          </SecondaryButton>
          <Button>
            <Plus size={18} />
            Add Product
          </Button>
        </ActionButtons>
      </Header>

      {/* TABS */}
      <TabsContainer>
        <Tab active={activeTab === 'products'} onClick={() => setActiveTab('products')}>
          Products
        </Tab>
        <Tab active={activeTab === 'orders'} onClick={() => setActiveTab('orders')}>
          Orders
        </Tab>
        <Tab active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')}>
          Analytics
        </Tab>
      </TabsContainer>

      {/* PRODUCTS TAB */}
      {activeTab === 'products' && (
        <>
          <ProductsGrid>
            {mockProducts.map((product) => (
              <ProductCard key={product.id}>
                <ProductImage>
                  <div style={{ fontSize: '60px' }}>{product.image}</div>
                  <ProductBadge>{'HOT'}</ProductBadge>
                </ProductImage>
                <ProductInfo>
                  <ProductName>{product.name}</ProductName>
                  <ProductPrice>${product.price}</ProductPrice>
                  <ProductStats>
                    <StatBadge>📊 {product.sales} sales</StatBadge>
                    <StatBadge>📦 {product.stock} stock</StatBadge>
                  </ProductStats>
                  <ProductActions>
                    <IconButton title="View">
                      <Eye size={16} />
                    </IconButton>
                    <IconButton title="Edit">
                      <Edit size={16} />
                    </IconButton>
                    <IconButton title="Delete">
                      <Trash2 size={16} />
                    </IconButton>
                  </ProductActions>
                </ProductInfo>
              </ProductCard>
            ))}
          </ProductsGrid>
        </>
      )}

      {/* ORDERS TAB */}
      {activeTab === 'orders' && (
        <TableContainer>
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {mockOrders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{order.customer}</td>
                  <td>{order.product}</td>
                  <td>${order.amount.toFixed(2)}</td>
                  <td>{order.date}</td>
                  <td>
                    <StatusBadge status={order.status}>
                      {order.status}
                    </StatusBadge>
                  </td>
                  <td>
                    <IconButton as="button" style={{ width: '30px', height: '30px', padding: 0 }}>
                      <ChevronRight size={16} />
                    </IconButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableContainer>
      )}

      {/* ANALYTICS TAB */}
      {activeTab === 'analytics' && (
        <div style={{ 
          background: 'linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          borderRadius: '14px',
          padding: '40px',
          textAlign: 'center'
        }}>
          <h3 style={{ fontSize: '20px', marginBottom: '20px', color: '#e2e8f0' }}>
            📊 Analytics Coming Soon
          </h3>
          <p style={{ color: 'rgba(226, 232, 240, 0.6)' }}>
            Detailed sales analytics, revenue trends, and customer insights
          </p>
        </div>
      )}
    </DashboardContainer>
  );
};

export default ECommerceDashboard;
