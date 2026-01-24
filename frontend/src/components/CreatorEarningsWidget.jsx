import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Heart, TrendingUp, Users, DollarSign } from 'lucide-react';
import axios from 'axios';

const WidgetContainer = styled.div`
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.05) 0%, rgba(244, 63, 94, 0.05) 100%);
  border: 2px solid rgba(236, 72, 153, 0.2);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;

  h3 {
    margin: 0;
    color: #333;
    font-size: 1.2rem;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const StatCard = styled.div`
  background: white;
  padding: 15px;
  border-radius: 10px;
  border-left: 4px solid ${props => props.color || '#EC4899'};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .label {
    font-size: 0.85rem;
    color: #999;
    margin-bottom: 5px;
    text-transform: uppercase;
    font-weight: 600;
  }

  .value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
  }

  .icon {
    float: right;
    opacity: 0.2;
  }
`;

const ProgressSection = styled.div`
  background: white;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 15px;

  .title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;

  .fill {
    height: 100%;
    background: linear-gradient(90deg, #EC4899 0%, #F43F5E 100%);
    transition: width 0.3s ease;
  }
`;

const TopDonors = styled.div`
  background: white;
  padding: 15px;
  border-radius: 10px;

  .title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
  }
`;

const DonorItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }

  .donor-name {
    font-weight: 500;
    color: #333;
  }

  .donor-amount {
    font-weight: 600;
    color: #EC4899;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #999;

  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const CreatorEarningsWidget = ({ creatorId }) => {
  const [earnings, setEarnings] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEarnings();
  }, [creatorId]);

  const fetchEarnings = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');

      const [earningsRes, statsRes] = await Promise.all([
        axios.get(
          `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/api/creator/${creatorId}/earnings`,
          { headers: { Authorization: `Bearer ${token}` } }
        ),
        axios.get(
          `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/api/creator/${creatorId}/stats`,
          { headers: { Authorization: `Bearer ${token}` } }
        )
      ]);

      setEarnings(earningsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <WidgetContainer>
        <Header>
          <Heart size={20} color="#EC4899" />
          <h3>Creator Earnings</h3>
        </Header>
        <LoadingSpinner>Loading earnings...</LoadingSpinner>
      </WidgetContainer>
    );
  }

  if (!earnings) {
    return null;
  }

  const monthlyGoal = 1000; // Example goal
  const monthlyProgress = (parseFloat(earnings.monthly_earned) / monthlyGoal) * 100;

  return (
    <WidgetContainer>
      <Header>
        <Heart size={20} color="#EC4899" fill="#EC4899" />
        <h3>Creator Earnings</h3>
      </Header>

      <StatsGrid>
        <StatCard color="#EC4899">
          <div className="label">Total Earned</div>
          <div className="value">${earnings.total_earned}</div>
          <DollarSign className="icon" size={24} />
        </StatCard>

        <StatCard color="#F43F5E">
          <div className="label">Total Tips</div>
          <div className="value">{earnings.total_tips}</div>
          <Heart className="icon" size={24} />
        </StatCard>

        <StatCard color="#8B5CF6">
          <div className="label">Total Donors</div>
          <div className="value">{earnings.total_donors}</div>
          <Users className="icon" size={24} />
        </StatCard>

        <StatCard color="#06B6D4">
          <div className="label">Monthly Earned</div>
          <div className="value">${earnings.monthly_earned}</div>
          <TrendingUp className="icon" size={24} />
        </StatCard>
      </StatsGrid>

      {earnings.monthly_recurring && parseFloat(earnings.monthly_recurring) > 0 && (
        <ProgressSection>
          <div className="title">Monthly Recurring Revenue</div>
          <div className="value" style={{ marginBottom: '8px' }}>
            ${earnings.monthly_recurring} / month from {earnings.recurring_donors} subscribers
          </div>
        </ProgressSection>
      )}

      <ProgressSection>
        <div className="title">Monthly Goal Progress</div>
        <ProgressBar>
          <div className="fill" style={{ width: `${Math.min(monthlyProgress, 100)}%` }} />
        </ProgressBar>
        <div style={{ fontSize: '0.85rem', color: '#999', marginTop: '8px' }}>
          ${earnings.monthly_earned} / ${monthlyGoal} ({monthlyProgress.toFixed(0)}%)
        </div>
      </ProgressSection>

      {stats && stats.top_donors && stats.top_donors.length > 0 && (
        <TopDonors>
          <div className="title">🏆 Top Supporters</div>
          {stats.top_donors.slice(0, 5).map((donor, idx) => (
            <DonorItem key={idx}>
              <span className="donor-name">Supporter #{idx + 1}</span>
              <span className="donor-amount">${donor.total_donated}</span>
            </DonorItem>
          ))}
        </TopDonors>
      )}
    </WidgetContainer>
  );
};

export default CreatorEarningsWidget;
