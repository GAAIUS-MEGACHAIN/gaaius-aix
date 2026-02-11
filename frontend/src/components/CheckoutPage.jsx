import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

// ==================== STYLED COMPONENTS ====================

const CheckoutContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const CheckoutTitle = styled.h2`
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 12px;
`;

const FormSection = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 16px;
  color: #333;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
`;

const Input = styled.input`
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #999;
  }
`;

const Select = styled.select`
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Textarea = styled.textarea`
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const OrderSummary = styled.div`
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
`;

const SummaryItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;

  &.total {
    font-weight: 700;
    color: #667eea;
    border-top: 1px solid #ddd;
    padding-top: 8px;
    margin-top: 8px;
  }
`;

const PaymentMethodGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 12px;
`;

const PaymentMethodButton = styled.button`
  padding: 12px;
  border: 2px solid ${props => props.selected ? '#667eea' : '#e0e0e0'};
  background: ${props => props.selected ? '#f0f0ff' : 'white'};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;

  &:hover {
    border-color: #667eea;
  }

  ${props => props.selected && `
    background: #f0f0ff;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  `}
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
`;

const Checkbox = styled.input`
  width: 18px;
  height: 18px;
  cursor: pointer;
`;

const SubmitButton = styled.button`
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CancelButton = styled.button`
  width: 100%;
  padding: 14px;
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 12px;

  &:hover {
    background: #f0f0ff;
  }

  &:active {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #721c24;
`;

const SuccessMessage = styled.div`
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #155724;
`;

// ==================== COMPONENT ====================

const CheckoutPage = ({ userId, cartItems, cartTotal, onCheckoutSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    cardName: '',
    cardNumber: '',
    cardExpiry: '',
    cardCVV: '',
    paymentMethod: 'credit_card',
    sameAsShipping: true,
    agreeToTerms: false
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handlePaymentMethodChange = (method) => {
    setFormData(prev => ({
      ...prev,
      paymentMethod: method
    }));
  };

  const validateForm = () => {
    if (!formData.firstName.trim()) return 'First name is required';
    if (!formData.lastName.trim()) return 'Last name is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.address.trim()) return 'Address is required';
    if (!formData.city.trim()) return 'City is required';
    if (!formData.zipCode.trim()) return 'ZIP code is required';
    if (!formData.country.trim()) return 'Country is required';
    if (!formData.agreeToTerms) return 'You must agree to terms and conditions';

    // Payment method validation
    if (formData.paymentMethod === 'credit_card') {
      if (!formData.cardName.trim()) return 'Card name is required';
      if (!formData.cardNumber.trim()) return 'Card number is required';
      if (!formData.cardExpiry.trim()) return 'Card expiry is required';
      if (!formData.cardCVV.trim()) return 'Card CVV is required';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const shippingAddress = {
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        address: formData.address,
        city: formData.city,
        state: formData.state,
        zipCode: formData.zipCode,
        country: formData.country
      };

      const response = await axios.post(
        `${backendUrl}/api/orders/checkout/${userId}`,
        {
          shipping_address: shippingAddress,
          payment_method: formData.paymentMethod
        },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );

      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => {
          if (onCheckoutSuccess) {
            onCheckoutSuccess(response.data.order_ids);
          }
        }, 2000);
      } else {
        setError(response.data.error || 'Checkout failed');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      setError(err.response?.data?.detail || 'Checkout failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const subtotal = cartTotal || 0;
  const tax = subtotal * 0.1;
  const shipping = subtotal > 100 ? 0 : 9.99;
  const total = subtotal + tax + shipping;

  return (
    <CheckoutContainer>
      <CheckoutTitle>🛒 Checkout</CheckoutTitle>

      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>✅ Order placed successfully! Redirecting...</SuccessMessage>}

      {/* Order Summary */}
      <OrderSummary>
        <h4 style={{ margin: '0 0 12px 0', color: '#333' }}>Order Summary</h4>
        <SummaryItem>
          <span>Subtotal:</span>
          <span>${subtotal.toFixed(2)}</span>
        </SummaryItem>
        <SummaryItem>
          <span>Tax (10%):</span>
          <span>${tax.toFixed(2)}</span>
        </SummaryItem>
        <SummaryItem>
          <span>Shipping:</span>
          <span>{shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`}</span>
        </SummaryItem>
        <SummaryItem className="total">
          <span>Total:</span>
          <span>${total.toFixed(2)}</span>
        </SummaryItem>
      </OrderSummary>

      <form onSubmit={handleSubmit}>
        {/* Shipping Address */}
        <FormSection>
          <SectionTitle>📍 Shipping Address</SectionTitle>
          <FormGrid>
            <FormGroup>
              <Label>First Name *</Label>
              <Input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                placeholder="John"
              />
            </FormGroup>
            <FormGroup>
              <Label>Last Name *</Label>
              <Input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                placeholder="Doe"
              />
            </FormGroup>
          </FormGrid>

          <FormGrid>
            <FormGroup>
              <Label>Email *</Label>
              <Input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="john@example.com"
              />
            </FormGroup>
            <FormGroup>
              <Label>Phone</Label>
              <Input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+1 (555) 000-0000"
              />
            </FormGroup>
          </FormGrid>

          <FormGroup>
            <Label>Address *</Label>
            <Input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder="123 Main Street"
            />
          </FormGroup>

          <FormGrid>
            <FormGroup>
              <Label>City *</Label>
              <Input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                placeholder="New York"
              />
            </FormGroup>
            <FormGroup>
              <Label>State</Label>
              <Input
                type="text"
                name="state"
                value={formData.state}
                onChange={handleInputChange}
                placeholder="NY"
              />
            </FormGroup>
            <FormGroup>
              <Label>ZIP Code *</Label>
              <Input
                type="text"
                name="zipCode"
                value={formData.zipCode}
                onChange={handleInputChange}
                placeholder="10001"
              />
            </FormGroup>
          </FormGrid>

          <FormGroup>
            <Label>Country *</Label>
            <Select
              name="country"
              value={formData.country}
              onChange={handleInputChange}
            >
              <option value="">Select Country</option>
              <option value="US">United States</option>
              <option value="CA">Canada</option>
              <option value="GB">United Kingdom</option>
              <option value="ZA">South Africa</option>
              <option value="NG">Nigeria</option>
              <option value="KE">Kenya</option>
              <option value="IN">India</option>
              <option value="JP">Japan</option>
              <option value="AU">Australia</option>
            </Select>
          </FormGroup>
        </FormSection>

        {/* Payment Method */}
        <FormSection>
          <SectionTitle>💳 Payment Method</SectionTitle>
          <PaymentMethodGrid>
            <PaymentMethodButton
              type="button"
              selected={formData.paymentMethod === 'credit_card'}
              onClick={() => handlePaymentMethodChange('credit_card')}
            >
              💳 Credit Card
            </PaymentMethodButton>
            <PaymentMethodButton
              type="button"
              selected={formData.paymentMethod === 'paypal'}
              onClick={() => handlePaymentMethodChange('paypal')}
            >
              🅿️ PayPal
            </PaymentMethodButton>
            <PaymentMethodButton
              type="button"
              selected={formData.paymentMethod === 'digital_wallet'}
              onClick={() => handlePaymentMethodChange('digital_wallet')}
            >
              📱 Digital Wallet
            </PaymentMethodButton>
            <PaymentMethodButton
              type="button"
              selected={formData.paymentMethod === 'bank_transfer'}
              onClick={() => handlePaymentMethodChange('bank_transfer')}
            >
              🏦 Bank Transfer
            </PaymentMethodButton>
          </PaymentMethodGrid>

          {formData.paymentMethod === 'credit_card' && (
            <div style={{ marginTop: '16px' }}>
              <FormGroup>
                <Label>Card Name *</Label>
                <Input
                  type="text"
                  name="cardName"
                  value={formData.cardName}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                />
              </FormGroup>
              <FormGroup>
                <Label>Card Number *</Label>
                <Input
                  type="text"
                  name="cardNumber"
                  value={formData.cardNumber}
                  onChange={handleInputChange}
                  placeholder="4111 1111 1111 1111"
                />
              </FormGroup>
              <FormGrid>
                <FormGroup>
                  <Label>Expiry Date *</Label>
                  <Input
                    type="text"
                    name="cardExpiry"
                    value={formData.cardExpiry}
                    onChange={handleInputChange}
                    placeholder="MM/YY"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>CVV *</Label>
                  <Input
                    type="text"
                    name="cardCVV"
                    value={formData.cardCVV}
                    onChange={handleInputChange}
                    placeholder="123"
                  />
                </FormGroup>
              </FormGrid>
            </div>
          )}
        </FormSection>

        {/* Terms */}
        <FormSection>
          <CheckboxLabel>
            <Checkbox
              type="checkbox"
              name="agreeToTerms"
              checked={formData.agreeToTerms}
              onChange={handleInputChange}
            />
            I agree to terms and conditions *
          </CheckboxLabel>
        </FormSection>

        {/* Submit Buttons */}
        <SubmitButton type="submit" disabled={loading || success}>
          {loading ? (
            <>
              <LoadingSpinner />
              Processing...
            </>
          ) : success ? (
            <>✅ Order Placed</>
          ) : (
            <>Place Order (${total.toFixed(2)})</>
          )}
        </SubmitButton>

        <CancelButton type="button" onClick={onCancel} disabled={loading}>
          Cancel
        </CancelButton>
      </form>
    </CheckoutContainer>
  );
};

export default CheckoutPage;
