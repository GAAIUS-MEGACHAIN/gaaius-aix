import React, { useState } from 'react';
import styled from 'styled-components';
import { Heart, DollarSign } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const TipButtonContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TipButton = styled.button`
  background: linear-gradient(135deg, #EC4899 0%, #F43F5E 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  @media (max-width: 640px) {
    padding: 6px 12px;
    font-size: 0.85rem;
  }
`;

const ModalOverlay = styled.div`
  display: ${props => props.isOpen ? 'flex' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 16px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;

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
`;

const ModalHeader = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const TierGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

const TierButton = styled.button`
  background: ${props => props.selected ? 'linear-gradient(135deg, #EC4899 0%, #F43F5E 100%)' : '#f5f5f5'};
  color: ${props => props.selected ? 'white' : '#333'};
  border: 2px solid ${props => props.selected ? '#EC4899' : '#e0e0e0'};
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s;
  font-weight: 600;

  &:hover {
    border-color: #EC4899;
    transform: translateY(-2px);
  }

  div:first-child {
    font-size: 1.3rem;
    margin-bottom: 4px;
  }

  div:last-child {
    font-size: 0.85rem;
    opacity: 0.8;
  }
`;

const CustomAmountContainer = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #EC4899;
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  min-height: 80px;
  resize: vertical;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #EC4899;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
  justify-content: flex-end;

  @media (max-width: 480px) {
    flex-direction: column;
  }
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const PrimaryButton = styled(Button)`
  background: linear-gradient(135deg, #EC4899 0%, #F43F5E 100%);
  color: white;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
  }
`;

const SecondaryButton = styled(Button)`
  background: #f0f0f0;
  color: #333;

  &:hover:not(:disabled) {
    background: #e0e0e0;
  }
`;

const CurrencySelect = styled.select`
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;

  &:focus {
    outline: none;
    border-color: #EC4899;
  }
`;

const VisibilityContainer = styled.div`
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9rem;

  input {
    cursor: pointer;
  }
`;

const DonationButton = ({
  creatorId,
  contentId = null,
  contentType = 'video',
  onDonationSuccess = null,
  showLabel = true,
  compact = false,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedTier, setSelectedTier] = useState(null);
  const [customAmount, setCustomAmount] = useState('');
  const [currency, setCurrency] = useState('usd');
  const [message, setMessage] = useState('');
  const [visibility, setVisibility] = useState('public');
  const [donorName, setDonorName] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [loading, setLoading] = useState(false);

  const tiers = [
    { amount: 2, emoji: '☕', name: 'Coffee' },
    { amount: 5, emoji: '🎁', name: 'Gift' },
    { amount: 10, emoji: '🌟', name: 'Star' },
    { amount: 25, emoji: '💎', name: 'Diamond' },
    { amount: 50, emoji: '👑', name: 'Royalty' },
    { amount: 100, emoji: '🚀', name: 'Legend' }
  ];

  const currencySymbols = {
    usd: '$',
    zar: 'R',
    eur: '€',
    gbp: '£',
    ngn: '₦',
    kes: 'Ksh'
  };

  const handleTierSelect = (tier) => {
    setSelectedTier(tier);
    setCustomAmount('');
  };

  const handleCustomAmountChange = (e) => {
    setCustomAmount(e.target.value);
    setSelectedTier(null);
  };

  const handleSubmit = async () => {
    try {
      if (!selectedTier && !customAmount) {
        toast.error('Please select or enter an amount');
        return;
      }

      const amount = selectedTier ? selectedTier.amount : parseFloat(customAmount);
      
      if (amount < 0.50 || amount > 10000) {
        toast.error('Amount must be between $0.50 and $10,000');
        return;
      }

      setLoading(true);

      const token = localStorage.getItem('authToken');
      const userId = localStorage.getItem('userId');

      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/api/donate/${creatorId}?donor_id=${userId}`,
        {
          creator_id: creatorId,
          content_id: contentId,
          content_type: contentType,
          amount: amount,
          currency: currency,
          payment_method: 'stripe',
          message: message || null,
          donor_name: isAnonymous ? null : donorName,
          visibility: visibility
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      toast.success(`Tip of ${currencySymbols[currency]}${amount} sent! ❤️`);
      setIsOpen(false);
      setSelectedTier(null);
      setCustomAmount('');
      setMessage('');

      if (onDonationSuccess) {
        onDonationSuccess(response.data);
      }
    } catch (error) {
      console.error('Error sending tip:', error);
      toast.error(error.response?.data?.detail || 'Failed to send tip');
    } finally {
      setLoading(false);
    }
  };

  const amount = selectedTier ? selectedTier.amount : customAmount;
  const displayAmount = amount ? `${currencySymbols[currency]}${amount}` : 'Tip';

  return (
    <>
      <TipButtonContainer className={className}>
        <TipButton onClick={() => setIsOpen(true)}>
          <Heart size={compact ? 16 : 18} fill="currentColor" />
          {showLabel && <span>{compact ? 'Tip' : 'Send Tip'}</span>}
        </TipButton>
      </TipButtonContainer>

      <ModalOverlay isOpen={isOpen} onClick={() => setIsOpen(false)}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <ModalHeader>
            <Heart size={24} fill="currentColor" />
            Support Creator
          </ModalHeader>

          <Label style={{ marginBottom: '15px', marginTop: '0' }}>Select Amount</Label>
          <TierGrid>
            {tiers.map((tier, idx) => (
              <TierButton
                key={idx}
                selected={selectedTier?.amount === tier.amount}
                onClick={() => handleTierSelect(tier)}
              >
                <div>{tier.emoji}</div>
                <div>${tier.amount}</div>
              </TierButton>
            ))}
          </TierGrid>

          <CustomAmountContainer>
            <Label>Custom Amount</Label>
            <Input
              type="number"
              placeholder="Enter custom amount"
              value={customAmount}
              onChange={handleCustomAmountChange}
              min="0.50"
              max="10000"
              step="0.01"
            />
          </CustomAmountContainer>

          <div style={{ marginBottom: '20px' }}>
            <Label>Currency</Label>
            <CurrencySelect value={currency} onChange={(e) => setCurrency(e.target.value)}>
              <option value="usd">USD ($)</option>
              <option value="eur">EUR (€)</option>
              <option value="gbp">GBP (£)</option>
              <option value="zar">ZAR (R)</option>
              <option value="ngn">NGN (₦)</option>
              <option value="kes">KES (Ksh)</option>
            </CurrencySelect>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <Label>Visibility</Label>
            <VisibilityContainer>
              <CheckboxLabel>
                <input
                  type="radio"
                  name="visibility"
                  value="public"
                  checked={visibility === 'public'}
                  onChange={(e) => setVisibility(e.target.value)}
                />
                Public
              </CheckboxLabel>
              <CheckboxLabel>
                <input
                  type="radio"
                  name="visibility"
                  value="private"
                  checked={visibility === 'private'}
                  onChange={(e) => setVisibility(e.target.value)}
                />
                Private
              </CheckboxLabel>
              <CheckboxLabel>
                <input
                  type="checkbox"
                  checked={isAnonymous}
                  onChange={(e) => setIsAnonymous(e.target.checked)}
                />
                Anonymous
              </CheckboxLabel>
            </VisibilityContainer>
          </div>

          {!isAnonymous && (
            <div style={{ marginBottom: '20px' }}>
              <Label>Your Name (Optional)</Label>
              <Input
                type="text"
                placeholder="How should we credit you?"
                value={donorName}
                onChange={(e) => setDonorName(e.target.value)}
              />
            </div>
          )}

          <div style={{ marginBottom: '20px' }}>
            <Label>Message (Optional)</Label>
            <Textarea
              placeholder="Say something nice to the creator..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              maxLength="500"
            />
            <div style={{ fontSize: '0.8rem', color: '#999', marginTop: '4px' }}>
              {message.length}/500
            </div>
          </div>

          <ActionButtons>
            <SecondaryButton onClick={() => setIsOpen(false)}>
              Cancel
            </SecondaryButton>
            <PrimaryButton onClick={handleSubmit} disabled={loading || !amount}>
              {loading ? '🔄 Processing...' : `💖 Send ${displayAmount}`}
            </PrimaryButton>
          </ActionButtons>
        </ModalContent>
      </ModalOverlay>
    </>
  );
};

export default DonationButton;
