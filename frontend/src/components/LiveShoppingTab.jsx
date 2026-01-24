import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ShoppingCart, Users, DollarSign, Zap, Eye } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #22c55e 0%, #15803d 100%);
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

const Badge = styled.span`
  display: inline-block;
  background: rgba(34, 197, 94, 0.3);
  border: 1px solid rgba(34, 197, 94, 0.5);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin: 10px 0;
`;

const LiveShoppingTab = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  const mockSessions = [
    {
      session_id: '1',
      title: 'Fashion Friday Live Sale',
      viewers: 342,
      products: 18,
      revenue: 1240.50,
      status: 'live'
    },
    {
      session_id: '2',
      title: 'Electronics Showcase',
      viewers: 156,
      products: 12,
      revenue: 2840.75,
      status: 'live'
    },
    {
      session_id: '3',
      title: 'Home Decor Special',
      viewers: 89,
      products: 24,
      revenue: 1680.25,
      status: 'scheduled'
    }
  ];

  return (
    <Container>
      <Header>
        <Title>
          <ShoppingCart size={32} />
          Live Shopping
        </Title>
      </Header>

      <GridContainer>
        {mockSessions.map((session) => (
          <Card key={session.session_id}>
            <h3 style={{ margin: '0 0 10px 0' }}>{session.title}</h3>
            <Badge style={{ background: session.status === 'live' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(107, 114, 128, 0.3)' }}>
              {session.status === 'live' ? '🔴 LIVE' : '📅 Scheduled'}
            </Badge>
            <StatRow>
              <span>
                <Eye size={16} style={{ display: 'inline', marginRight: '5px' }} />
                Viewers: {session.viewers}
              </span>
            </StatRow>
            <StatRow>
              <span>Products: {session.products}</span>
            </StatRow>
            <StatRow style={{ fontSize: '16px', fontWeight: 'bold', marginTop: '15px' }}>
              <span>
                <DollarSign size={16} style={{ display: 'inline', marginRight: '5px' }} />
                ${session.revenue}
              </span>
            </StatRow>
            <Button style={{ marginTop: '15px' }}>
              {session.status === 'live' ? 'Go Live' : 'Start Session'}
            </Button>
            <Button style={{ marginTop: '10px' }}>Analytics</Button>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default LiveShoppingTab;
