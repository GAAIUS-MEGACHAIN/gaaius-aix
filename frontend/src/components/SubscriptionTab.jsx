import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { CreditCard, Plus, Users, DollarSign, Zap } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #f59e0b 0%, #92400e 100%);
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

const TierBadge = styled.span`
  display: inline-block;
  background: rgba(245, 158, 11, 0.3);
  border: 1px solid rgba(245, 158, 11, 0.5);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin: 10px 0;
`;

const StatRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 8px 0;
`;

const SubscriptionTab = () => {
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(false);

  const mockTiers = [
    {
      tier_id: '1',
      name: 'Basic',
      price: 4.99,
      members: 2341,
      features: ['Exclusive content', 'Ad-free'],
      monthlyRevenue: 11679.59
    },
    {
      tier_id: '2',
      name: 'Pro',
      price: 9.99,
      members: 567,
      features: ['Everything in Basic', 'Early access', 'Discord'],
      monthlyRevenue: 5660.33
    },
    {
      tier_id: '3',
      name: 'Premium',
      price: 24.99,
      members: 123,
      features: ['Everything in Pro', 'Monthly call', 'Custom requests'],
      monthlyRevenue: 3068.77
    }
  ];

  return (
    <Container>
      <Header>
        <Title>
          <CreditCard size={32} />
          Subscriptions
        </Title>
        <Button style={{ width: 'auto' }}>
          <Plus size={16} style={{ display: 'inline', marginRight: '5px' }} />
          New Tier
        </Button>
      </Header>

      <GridContainer>
        {mockTiers.map((tier) => (
          <Card key={tier.tier_id}>
            <h3 style={{ margin: '0 0 5px 0' }}>{tier.name}</h3>
            <TierBadge>${tier.price}/month</TierBadge>
            <StatRow>
              <span>
                <Users size={16} style={{ display: 'inline', marginRight: '5px' }} />
                Members: {tier.members}
              </span>
            </StatRow>
            <div style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.7)', margin: '12px 0' }}>
              <div style={{ fontWeight: '600', marginBottom: '8px' }}>Features:</div>
              {tier.features.map((feature, idx) => (
                <div key={idx} style={{ marginLeft: '8px', marginBottom: '4px' }}>
                  • {feature}
                </div>
              ))}
            </div>
            <StatRow style={{ marginTop: '15px', fontSize: '15px', fontWeight: 'bold' }}>
              <span>
                <DollarSign size={16} style={{ display: 'inline', marginRight: '5px' }} />
                ${tier.monthlyRevenue.toFixed(2)}/mo
              </span>
            </StatRow>
            <Button style={{ marginTop: '15px' }}>Manage Tier</Button>
            <Button style={{ marginTop: '10px' }}>Analytics</Button>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default SubscriptionTab;
