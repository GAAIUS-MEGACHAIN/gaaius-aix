import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Area, AreaChart
} from 'recharts';
import { 
  TrendingUp, Users, DollarSign, Zap, Eye, Heart, Share2,
  Calendar, Download, Settings, Bell, Search, Filter,
  ArrowUp, ArrowDown, MoreVertical, ChevronRight, Star,
  Sparkles, Flame, Crown, Gift, Target
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

// ============================================================================
// MODERN ENTERPRISE STYLED COMPONENTS
// ============================================================================

const DashboardContainer = styled.div`
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  min-height: 100vh;
  padding: 0;
  font-family: 'Manrope', sans-serif;
  overflow-x: hidden;
`;

// ============================================================================
// HEADER STYLES
// ============================================================================

const Header = styled.div`
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
  
  svg {
    width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
`;

const SearchBox = styled.div`
  position: relative;
  width: 300px;
  
  input {
    width: 100%;
    background: rgba(148, 163, 184, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 10px;
    padding: 10px 15px 10px 40px;
    color: #e2e8f0;
    font-size: 14px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:focus {
      outline: none;
      background: rgba(148, 163, 184, 0.15);
      border-color: #f472b6;
      box-shadow: 0 0 20px rgba(244, 114, 182, 0.2);
    }
    
    &::placeholder {
      color: rgba(226, 232, 240, 0.5);
    }
  }
`;

const SearchIcon = styled(Search)`
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: rgba(226, 232, 240, 0.5);
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const IconButton = styled.button`
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  
  &:hover {
    background: rgba(244, 114, 182, 0.1);
    border-color: #f472b6;
    transform: translateY(-2px);
  }
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const NotificationBadge = styled.div`
  position: absolute;
  top: -5px;
  right: -5px;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  box-shadow: 0 0 10px rgba(244, 114, 182, 0.5);
`;

const UserProfile = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    background: rgba(244, 114, 182, 0.1);
    border: 1px solid rgba(244, 114, 182, 0.2);
  }
`;

const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 0 10px rgba(244, 114, 182, 0.3);
`;

// ============================================================================
// MAIN CONTENT STYLES
// ============================================================================

const MainContent = styled.div`
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
`;

const SectionTitle = styled.h2`
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 30px;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 15px;
  
  svg {
    width: 32px;
    height: 32px;
    color: #f472b6;
    filter: drop-shadow(0 0 10px rgba(244, 114, 182, 0.3));
  }
`;

// ============================================================================
// METRICS CARDS
// ============================================================================

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const MetricCard = styled.div`
  background: linear-gradient(135deg, rgba(244, 114, 182, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%);
  border: 1px solid rgba(244, 114, 182, 0.2);
  border-radius: 14px;
  padding: 24px;
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-8px);
    border-color: #f472b6;
    box-shadow: 0 20px 50px rgba(244, 114, 182, 0.15);
    
    &::before {
      opacity: 0.5;
    }
  }
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(244, 114, 182, 0.3) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
  }
`;

const MetricTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
`;

const MetricLabel = styled.span`
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(226, 232, 240, 0.7);
`;

const MetricIcon = styled.div`
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(244, 114, 182, 0.3);
  
  svg {
    width: 22px;
    height: 22px;
    color: white;
  }
`;

const MetricValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
`;

const MetricChange = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: ${props => props.positive ? '#10b981' : '#ef4444'};
  position: relative;
  z-index: 1;
  
  svg {
    width: 16px;
    height: 16px;
  }
`;

// ============================================================================
// CHARTS STYLES
// ============================================================================

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const ChartCard = styled.div`
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  padding: 24px;
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    border-color: rgba(244, 114, 182, 0.2);
    box-shadow: 0 10px 30px rgba(244, 114, 182, 0.1);
  }
  
  h3 {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
`;

const FullWidthCard = styled(ChartCard)`
  grid-column: 1 / -1;
`;

// ============================================================================
// TABLE STYLES
// ============================================================================

const TableContainer = styled.div`
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  
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
      font-size: 14px;
    }
    
    tbody tr {
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      
      &:hover {
        background: rgba(244, 114, 182, 0.05);
      }
      
      &:last-child td {
        border-bottom: none;
      }
    }
  }
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => {
    switch(props.status) {
      case 'active': return 'rgba(16, 185, 129, 0.2)';
      case 'pending': return 'rgba(245, 158, 11, 0.2)';
      case 'completed': return 'rgba(59, 130, 246, 0.2)';
      case 'paused': return 'rgba(107, 114, 128, 0.2)';
      default: return 'rgba(148, 163, 184, 0.2)';
    }
  }};
  color: ${props => {
    switch(props.status) {
      case 'active': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'completed': return '#3b82f6';
      case 'paused': return '#6b7280';
      default: return '#94a3b8';
    }
  }};
  border: 1px solid currentColor;
  text-transform: uppercase;
`;

// ============================================================================
// TIER CARD STYLES
// ============================================================================

const TierCardsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const TierCard = styled.div`
  background: linear-gradient(135deg, rgba(${props => props.bgColor ? props.bgColor : '244, 114, 182'}, 0.1) 0%, rgba(${props => props.bgColor ? props.bgColor : '236, 72, 153'}, 0.05) 100%);
  border: 2px solid rgba(${props => props.bgColor ? props.bgColor : '244, 114, 182'}, 0.2);
  border-radius: 14px;
  padding: 24px;
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-8px);
    border-color: rgba(${props => props.bgColor ? props.bgColor : '244, 114, 182'}, 0.6);
    box-shadow: 0 20px 50px rgba(${props => props.bgColor ? props.bgColor : '244, 114, 182'}, 0.15);
  }
  
  ${props => props.featured && `
    border: 2px solid rgba(244, 114, 182, 0.8);
    box-shadow: 0 0 30px rgba(244, 114, 182, 0.3);
  `}
`;

const TierBadge = styled.div`
  display: inline-block;
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(244, 114, 182, 0.3);
`;

const TierName = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: #e2e8f0;
  margin: 12px 0;
`;

const TierPrice = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  margin: 12px 0;
  
  span {
    font-size: 14px;
    color: rgba(226, 232, 240, 0.6);
  }
`;

const TierStats = styled.div`
  display: flex;
  gap: 8px;
  margin: 16px 0;
  flex-wrap: wrap;
`;

const StatBadge = styled.span`
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.8);
`;

// ============================================================================
// MODERN CREATOR DASHBOARD COMPONENT
// ============================================================================

const ModernCreatorDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    subscribers: 1250,
    revenue: 5840,
    engagement: 2340,
    views: 84500,
    conversionRate: 8.4,
    
    subscribersTrend: [
      { month: 'Jan', subs: 800 },
      { month: 'Feb', subs: 950 },
      { month: 'Mar', subs: 1050 },
      { month: 'Apr', subs: 1150 },
      { month: 'May', subs: 1250 },
    ],
    
    revenueTrend: [
      { month: 'Jan', revenue: 2400 },
      { month: 'Feb', revenue: 3210 },
      { month: 'Mar', revenue: 4290 },
      { month: 'Apr', revenue: 5100 },
      { month: 'May', revenue: 5840 },
    ],
    
    tierDistribution: [
      { name: 'Free', value: 450 },
      { name: 'Basic', value: 380 },
      { name: 'Pro', value: 250 },
      { name: 'VIP', value: 120 },
      { name: 'Elite', value: 50 },
    ],
    
    recentTransactions: [
      { id: 1, user: 'John Doe', tier: 'Pro', amount: 29.99, date: '2024-01-20', status: 'completed' },
      { id: 2, user: 'Jane Smith', tier: 'Basic', amount: 9.99, date: '2024-01-20', status: 'completed' },
      { id: 3, user: 'Mike Johnson', tier: 'Elite', amount: 99.99, date: '2024-01-19', status: 'completed' },
      { id: 4, user: 'Sarah Lee', tier: 'VIP', amount: 49.99, date: '2024-01-19', status: 'pending' },
      { id: 5, user: 'Tom Wilson', tier: 'Free', amount: 0, date: '2024-01-18', status: 'active' },
    ],
    
    tiers: [
      { name: 'Free', price: 0, subscribers: 450, features: '3 videos/month', color: '148, 163, 184' },
      { name: 'Basic', price: 9.99, subscribers: 380, features: 'Unlimited videos', color: '59, 130, 246' },
      { name: 'Pro', price: 29.99, subscribers: 250, features: '1080p + extras', color: '168, 85, 247', featured: true },
      { name: 'VIP', price: 49.99, subscribers: 120, features: 'Priority support', color: '244, 63, 94' },
      { name: 'Elite', price: 99.99, subscribers: 50, features: '1-on-1 sessions', color: '245, 158, 11' },
    ],
  });

  const colors = ['#f472b6', '#ec4899', '#f43f5e', '#fb7185', '#fda4af'];

  return (
    <DashboardContainer>
      {/* ====== HEADER ====== */}
      <Header>
        <HeaderLeft>
          <Logo>
            <Sparkles size={24} />
            GAAIUS Creator
          </Logo>
          <SearchBox>
            <SearchIcon />
            <input type="text" placeholder="Search creators, content, stats..." />
          </SearchBox>
        </HeaderLeft>
        
        <HeaderRight>
          <IconButton title="Notifications">
            <Bell size={20} />
            <NotificationBadge>3</NotificationBadge>
          </IconButton>
          
          <IconButton title="Settings">
            <Settings size={20} />
          </IconButton>
          
          <UserProfile>
            <Avatar>JD</Avatar>
            <span>John Doe</span>
          </UserProfile>
        </HeaderRight>
      </Header>

      {/* ====== MAIN CONTENT ====== */}
      <MainContent>
        {/* SECTION: Dashboard Overview */}
        <SectionTitle>
          <TrendingUp /> Dashboard Overview
        </SectionTitle>

        {/* METRICS GRID */}
        <MetricsGrid>
          <MetricCard>
            <MetricTop>
              <MetricLabel>Total Subscribers</MetricLabel>
              <MetricIcon>
                <Users />
              </MetricIcon>
            </MetricTop>
            <MetricValue>{dashboardData.subscribers.toLocaleString()}</MetricValue>
            <MetricChange positive>
              <ArrowUp size={16} />
              +12.5% from last month
            </MetricChange>
          </MetricCard>

          <MetricCard>
            <MetricTop>
              <MetricLabel>Monthly Revenue</MetricLabel>
              <MetricIcon>
                <DollarSign />
              </MetricIcon>
            </MetricTop>
            <MetricValue>${dashboardData.revenue.toLocaleString()}</MetricValue>
            <MetricChange positive>
              <ArrowUp size={16} />
              +14.2% from last month
            </MetricChange>
          </MetricCard>

          <MetricCard>
            <MetricTop>
              <MetricLabel>Total Views</MetricLabel>
              <MetricIcon>
                <Eye />
              </MetricIcon>
            </MetricTop>
            <MetricValue>{(dashboardData.views / 1000).toFixed(0)}K</MetricValue>
            <MetricChange positive>
              <ArrowUp size={16} />
              +23.8% from last month
            </MetricChange>
          </MetricCard>

          <MetricCard>
            <MetricTop>
              <MetricLabel>Engagement Rate</MetricLabel>
              <MetricIcon>
                <Zap />
              </MetricIcon>
            </MetricTop>
            <MetricValue>{dashboardData.conversionRate}%</MetricValue>
            <MetricChange positive={false}>
              <ArrowDown size={16} />
              -2.1% from last month
            </MetricChange>
          </MetricCard>
        </MetricsGrid>

        {/* SECTION: Subscription Tiers */}
        <SectionTitle>
          <Crown /> Subscription Tiers
        </SectionTitle>

        <TierCardsGrid>
          {dashboardData.tiers.map((tier, idx) => (
            <TierCard key={idx} bgColor={tier.color} featured={tier.featured}>
              <TierBadge>{tier.name}</TierBadge>
              <TierName>{tier.name}</TierName>
              <TierPrice>${tier.price}<span>/month</span></TierPrice>
              <TierStats>
                <StatBadge>👥 {tier.subscribers} subs</StatBadge>
                <StatBadge>✨ {tier.features}</StatBadge>
              </TierStats>
            </TierCard>
          ))}
        </TierCardsGrid>

        {/* SECTION: Analytics Charts */}
        <SectionTitle>
          <Target /> Analytics & Performance
        </SectionTitle>

        <ChartsGrid>
          <ChartCard>
            <h3>
              Subscriber Growth
              <Filter size={16} />
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={dashboardData.subscribersTrend}>
                <defs>
                  <linearGradient id="colorSubs" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f472b6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f472b6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis dataKey="month" stroke="rgba(226, 232, 240, 0.5)" />
                <YAxis stroke="rgba(226, 232, 240, 0.5)" />
                <Tooltip 
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(244, 114, 182, 0.3)',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
                <Area type="monotone" dataKey="subs" stroke="#f472b6" fillOpacity={1} fill="url(#colorSubs)" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard>
            <h3>
              Revenue Trend
              <Filter size={16} />
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dashboardData.revenueTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis dataKey="month" stroke="rgba(226, 232, 240, 0.5)" />
                <YAxis stroke="rgba(226, 232, 240, 0.5)" />
                <Tooltip 
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <FullWidthCard>
            <h3>
              Tier Distribution
              <Filter size={16} />
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dashboardData.tierDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#f472b6"
                  dataKey="value"
                >
                  {dashboardData.tierDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(244, 114, 182, 0.3)',
                    borderRadius: '8px',
                    color: '#e2e8f0'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </FullWidthCard>
        </ChartsGrid>

        {/* SECTION: Recent Transactions */}
        <SectionTitle>
          <TrendingUp /> Recent Transactions
        </SectionTitle>

        <TableContainer>
          <table>
            <thead>
              <tr>
                <th>Subscriber</th>
                <th>Tier</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.recentTransactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.user}</td>
                  <td>{transaction.tier}</td>
                  <td>${transaction.amount.toFixed(2)}</td>
                  <td>{transaction.date}</td>
                  <td>
                    <StatusBadge status={transaction.status}>
                      {transaction.status}
                    </StatusBadge>
                  </td>
                  <td>
                    <IconButton style={{ width: '30px', height: '30px' }}>
                      <MoreVertical size={16} />
                    </IconButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableContainer>
      </MainContent>
    </DashboardContainer>
  );
};

export default ModernCreatorDashboard;
