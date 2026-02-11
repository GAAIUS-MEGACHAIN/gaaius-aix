import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

// ==================== STYLED COMPONENTS ====================

const FloatingCartContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 998;
  max-width: 400px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const CartButton = styled.button`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.4);
  }

  &:active {
    transform: scale(0.95);
  }
`;

const CartBadge = styled.div`
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
`;

const CartModal = styled.div`
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 400px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: slideUp 0.3s ease;
  display: ${props => props.isOpen ? 'flex' : 'none'};
  flex-direction: column;

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media (max-width: 480px) {
    width: calc(100vw - 40px);
    max-height: 80vh;
  }
`;

const CartHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CartTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
`;

const CartContent = styled.div`
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
  padding: 12px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  &::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 3px;
  }
`;

const EmptyCart = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #999;
`;

const CartItemContainer = styled.div`
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #eee;
  background: #fafafa;
  margin-bottom: 8px;
  border-radius: 8px;

  &:last-child {
    border-bottom: none;
  }
`;

const CartItemImage = styled.img`
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  background: #eee;
`;

const CartItemInfo = styled.div`
  flex: 1;
`;

const CartItemName = styled.div`
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
`;

const CartItemPrice = styled.div`
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
`;

const QuantityControl = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
`;

const QuantityButton = styled.button`
  background: #f0f0f0;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: #667eea;
    color: white;
  }
`;

const RemoveButton = styled.button`
  background: #ff4757;
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: #ff3838;
  }
`;

const CartFooter = styled.div`
  border-top: 1px solid #eee;
  padding: 16px;
  background: #f9f9f9;
`;

const CartTotal = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;

  &.subtotal {
    color: #666;
  }

  &.tax {
    color: #666;
  }

  &.total {
    font-weight: 700;
    font-size: 16px;
    color: #667eea;
    border-top: 1px solid #eee;
    padding-top: 12px;
  }
`;

const CheckoutButton = styled.button`
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ClearButton = styled.button`
  width: 100%;
  padding: 10px;
  background: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #e0e0e0;
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    opacity: 0.8;
  }
`;

const MinimizeButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// ==================== COMPONENT ====================

const FloatingShoppingCart = ({ userId, contentId, contentType, onCheckout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    if (userId) {
      fetchCart();
    }
  }, [userId]);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/cart/${userId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      setLoading(true);
      await axios.delete(`${backendUrl}/api/cart/${userId}/items/${itemId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      await fetchCart();
    } catch (error) {
      console.error('Error removing item:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (itemId, currentQuantity, change) => {
    const newQuantity = currentQuantity + change;
    if (newQuantity <= 0) {
      handleRemoveItem(itemId);
      return;
    }

    try {
      setLoading(true);
      await axios.put(`${backendUrl}/api/cart/${userId}/items/${itemId}`, 
        { quantity: newQuantity },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      await fetchCart();
    } catch (error) {
      console.error('Error updating quantity:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Clear cart?')) {
      try {
        setLoading(true);
        await axios.delete(`${backendUrl}/api/cart/${userId}/clear`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        await fetchCart();
      } catch (error) {
        console.error('Error clearing cart:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const itemCount = cart?.items ? cart.items.length : 0;

  return (
    <FloatingCartContainer>
      <CartButton onClick={() => setIsOpen(!isOpen)}>
        🛒
        {itemCount > 0 && <CartBadge>{itemCount}</CartBadge>}
      </CartButton>

      <CartModal isOpen={isOpen && !isMinimized}>
        <CartHeader>
          <CartTitle>Shopping Cart ({itemCount})</CartTitle>
          <div style={{ display: 'flex', gap: '8px' }}>
            <MinimizeButton onClick={() => setIsMinimized(true)}>−</MinimizeButton>
            <CloseButton onClick={() => setIsOpen(false)}>✕</CloseButton>
          </div>
        </CartHeader>

        <CartContent>
          {itemCount === 0 ? (
            <EmptyCart>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>🛍️</div>
              <div>Your cart is empty</div>
              <div style={{ fontSize: '12px', marginTop: '8px', color: '#bbb' }}>
                Browse and add items to shop
              </div>
            </EmptyCart>
          ) : (
            cart?.items?.map(item => (
              <CartItemContainer key={item.id}>
                <CartItemImage 
                  src={item.thumbnail || 'https://via.placeholder.com/60'} 
                  alt={item.product_name}
                />
                <CartItemInfo>
                  <CartItemName>{item.product_name}</CartItemName>
                  <CartItemPrice>${item.unit_price}</CartItemPrice>
                  <QuantityControl>
                    <QuantityButton 
                      onClick={() => handleUpdateQuantity(item.id, item.quantity, -1)}
                      disabled={loading}
                    >
                      −
                    </QuantityButton>
                    <span style={{ width: '30px', textAlign: 'center', fontSize: '12px' }}>
                      {item.quantity}
                    </span>
                    <QuantityButton 
                      onClick={() => handleUpdateQuantity(item.id, item.quantity, 1)}
                      disabled={loading}
                    >
                      +
                    </QuantityButton>
                    <RemoveButton 
                      onClick={() => handleRemoveItem(item.id)}
                      disabled={loading}
                    >
                      ✕
                    </RemoveButton>
                  </QuantityControl>
                </CartItemInfo>
              </CartItemContainer>
            ))
          )}
        </CartContent>

        <CartFooter>
          <CartTotal className="subtotal">
            <span>Subtotal:</span>
            <span>${(cart?.subtotal || 0).toFixed(2)}</span>
          </CartTotal>
          <CartTotal className="tax">
            <span>Tax:</span>
            <span>${(cart?.tax || 0).toFixed(2)}</span>
          </CartTotal>
          <CartTotal className="total">
            <span>Total:</span>
            <span>${(cart?.total || 0).toFixed(2)}</span>
          </CartTotal>

          <CheckoutButton 
            onClick={onCheckout}
            disabled={itemCount === 0 || loading}
          >
            {loading ? <LoadingSpinner /> : 'Proceed to Checkout'}
          </CheckoutButton>
          <ClearButton 
            onClick={handleClearCart}
            disabled={itemCount === 0 || loading}
          >
            Clear Cart
          </ClearButton>
        </CartFooter>
      </CartModal>
    </FloatingCartContainer>
  );
};

export default FloatingShoppingCart;
