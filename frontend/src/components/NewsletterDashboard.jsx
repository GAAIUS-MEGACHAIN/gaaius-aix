import React, { useState, useEffect, useCallback, useRef } from 'react';
import styled from 'styled-components';
import {
  Mail, Settings, Users, TrendingUp, BarChart3, Zap, 
  Plus, Edit2, Trash2, Send, Clock, CheckCircle, AlertCircle,
  Upload, Download, Search, Filter, Eye, Copy, Play, Pause,
  X, ArrowRight, Calendar, Tag, Layers, Code, Palette,
  LogOut
} from 'lucide-react';

// ============ STYLED COMPONENTS ============

const Container = styled.div`
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  color: #fff;
`;

const Sidebar = styled.div`
  background: rgba(15, 12, 41, 0.8);
  backdrop-filter: blur(10px);
  padding: 24px 16px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
  font-size: 18px;
  font-weight: 700;
  color: #fff;

  svg {
    width: 28px;
    height: 28px;
    color: #a78bfa;
  }
`;

const NavMenu = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
`;

const NavItem = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  background: ${props => props.active ? 'rgba(167, 139, 250, 0.2)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'rgba(167, 139, 250, 0.5)' : 'transparent'};
  color: ${props => props.active ? '#a78bfa' : '#cbd5e1'};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 14px;

  svg {
    width: 18px;
    height: 18px;
  }

  &:hover {
    background: rgba(167, 139, 250, 0.15);
    color: #a78bfa;
  }
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const TopBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const PageTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #fff;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;

  &::-webkit-scrollbar {
    width: 8px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
`;

const MetricCard = styled.div`
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(167, 139, 250, 0.6);
    transform: translateY(-4px);
  }
`;

const MetricIcon = styled.div`
  width: 48px;
  height: 48px;
  background: rgba(167, 139, 250, 0.25);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;

  svg {
    width: 24px;
    height: 24px;
    color: #a78bfa;
  }
`;

const MetricLabel = styled.p`
  font-size: 12px;
  text-transform: uppercase;
  color: #a0aec0;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
`;

const MetricValue = styled.p`
  font-size: 28px;
  font-weight: 700;
  color: #fff;
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const SectionTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: #fff;
`;

const ActionBar = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;

  svg {
    width: 16px;
    height: 16px;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(167, 139, 250, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  &.secondary {
    background: rgba(167, 139, 250, 0.15);
    border: 1px solid rgba(167, 139, 250, 0.3);
    color: #a78bfa;

    &:hover {
      border-color: rgba(167, 139, 250, 0.6);
      background: rgba(167, 139, 250, 0.25);
    }
  }

  &.danger {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;

    &:hover {
      background: rgba(239, 68, 68, 0.25);
    }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;

  th {
    text-align: left;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    color: #a0aec0;
    letter-spacing: 0.5px;
  }

  td {
    padding: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 14px;
    color: #cbd5e1;

    &:first-child {
      border-left: 2px solid transparent;
    }
  }

  tr:hover td {
    background: rgba(167, 139, 250, 0.05);
  }

  tr:hover td:first-child {
    border-left-color: #a78bfa;
  }
`;

const CampaignStatus = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: ${props => {
    if (props.status === 'sent') return 'rgba(34, 197, 94, 0.15)';
    if (props.status === 'scheduled') return 'rgba(59, 130, 246, 0.15)';
    if (props.status === 'draft') return 'rgba(107, 114, 128, 0.15)';
    if (props.status === 'failed') return 'rgba(239, 68, 68, 0.15)';
    return 'rgba(107, 114, 128, 0.15)';
  }};
  color: ${props => {
    if (props.status === 'sent') return '#22c55e';
    if (props.status === 'scheduled') return '#3b82f6';
    if (props.status === 'draft') return '#9ca3af';
    if (props.status === 'failed') return '#ef4444';
    return '#9ca3af';
  }};
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;

  svg {
    width: 14px;
    height: 14px;
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
`;

const ModalContent = styled.div`
  background: linear-gradient(135deg, #1a1633 0%, #2d1b4e 100%);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    font-size: 22px;
    font-weight: 700;
    color: #fff;
  }

  button {
    background: none;
    border: none;
    color: #a0aec0;
    cursor: pointer;
    padding: 4px;
    transition: all 0.3s ease;

    &:hover {
      color: #fff;
    }
  }
`;

const FormGroup = styled.div`
  margin-bottom: 20px;

  label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #cbd5e1;
  }

  input,
  textarea,
  select {
    width: 100%;
    padding: 12px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #fff;
    font-size: 14px;
    font-family: inherit;
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-color: rgba(167, 139, 250, 0.6);
      background: rgba(255, 255, 255, 0.08);
      box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
    }

    &::placeholder {
      color: #64748b;
    }
  }

  textarea {
    min-height: 120px;
    resize: vertical;
  }
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

const TemplateEditor = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 2px dashed rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
`;

const VariableHint = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;

  span {
    background: rgba(167, 139, 250, 0.1);
    border: 1px solid rgba(167, 139, 250, 0.3);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: #a78bfa;
    font-family: 'Monaco', monospace;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(167, 139, 250, 0.2);
      border-color: rgba(167, 139, 250, 0.6);
    }
  }
`;

const TagsContainer = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const TagStyled = styled.span`
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(167, 139, 250, 0.15);
  border: 1px solid rgba(167, 139, 250, 0.3);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: #a78bfa;

  button {
    background: none;
    border: none;
    color: #a78bfa;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;

    &:hover {
      color: #fff;
    }
  }
`;

const ImportDropZone = styled.div`
  border: 2px dashed rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(167, 139, 250, 0.05);

  &:hover {
    border-color: rgba(167, 139, 250, 0.6);
    background: rgba(167, 139, 250, 0.1);
  }

  svg {
    width: 40px;
    height: 40px;
    color: #a78bfa;
    margin-bottom: 12px;
  }

  p {
    font-size: 14px;
    color: #cbd5e1;
    margin-bottom: 4px;
  }

  span {
    font-size: 12px;
    color: #64748b;
  }
`;

const AnalyticsChart = styled.div`
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  padding: 20px;
  height: 300px;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  justify-content: center;
`;

const ChartBar = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 60px;

  div {
    width: 40px;
    background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
    border-radius: 6px 6px 0 0;
    height: ${props => props.height}%;
    min-height: 20px;
    transition: all 0.3s ease;

    &:hover {
      height: ${props => props.height + 10}%;
      filter: brightness(1.1);
    }
  }

  span {
    font-size: 11px;
    color: #a0aec0;
    text-align: center;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;

  svg {
    width: 64px;
    height: 64px;
    color: rgba(167, 139, 250, 0.3);
    margin-bottom: 16px;
  }

  p {
    font-size: 16px;
    color: #a0aec0;
    margin-bottom: 24px;
  }
`;

// ============ NEWSLETTER DASHBOARD COMPONENT ============

export default function NewsletterDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [campaigns, setCampaigns] = useState([]);
  const [subscribers, setSubscribers] = useState([]);
  const [analytics, setAnalytics] = useState({
    subscribers: 0,
    campaigns_created: 0,
    total_sent: 0,
    total_opens: 0,
    total_clicks: 0,
    avg_open_rate: 0,
    avg_click_rate: 0,
    unsubscribes: 0
  });
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [showSubscriberModal, setShowSubscriberModal] = useState(false);
  const [showAutomationModal, setShowAutomationModal] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    subject: '',
    preview_text: '',
    html_content: '',
    segment_type: 'all',
    tags: []
  });
  const [newSubscriber, setNewSubscriber] = useState({
    email: '',
    name: '',
    phone: '',
    tags: []
  });
  const [newTag, setNewTag] = useState('');
  const [selectedSubscribers, setSelectedSubscribers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const fileInputRef = useRef(null);

  // Fetch analytics
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch('/api/newsletter/analytics/overview?user_id=demo_user');
        const data = await response.json();
        setAnalytics(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      }
    };

    fetchAnalytics();
  }, []);

  const addTag = (e) => {
    e.preventDefault();
    if (newTag.trim() && !newCampaign.tags.includes(newTag.trim())) {
      setNewCampaign(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tag) => {
    setNewCampaign(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const addSubscriberTag = (e) => {
    e.preventDefault();
    if (newTag.trim() && !newSubscriber.tags.includes(newTag.trim())) {
      setNewSubscriber(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeSubscriberTag = (tag) => {
    setNewSubscriber(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const handleCreateCampaign = async () => {
    if (!newCampaign.name || !newCampaign.subject || !newCampaign.html_content) {
      alert('Please fill all required fields');
      return;
    }

    try {
      const response = await fetch('/api/newsletter/campaigns?user_id=demo_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newCampaign.name,
          template: {
            name: newCampaign.name,
            subject: newCampaign.subject,
            preview_text: newCampaign.preview_text,
            html_content: newCampaign.html_content,
            text_content: newCampaign.html_content.replace(/<[^>]*>/g, ''),
            variables: newCampaign.variables || []
          },
          segment: {
            segment_type: newCampaign.segment_type,
            tags: newCampaign.tags.length > 0 ? newCampaign.tags : undefined
          }
        })
      });

      const data = await response.json();
      setCampaigns(prev => [...prev, { id: data.id, ...newCampaign }]);
      setShowCampaignModal(false);
      setNewCampaign({
        name: '',
        subject: '',
        preview_text: '',
        html_content: '',
        segment_type: 'all',
        tags: []
      });
    } catch (error) {
      console.error('Failed to create campaign:', error);
    }
  };

  const handleAddSubscriber = async () => {
    if (!newSubscriber.email || !newSubscriber.name) {
      alert('Please fill email and name');
      return;
    }

    try {
      const response = await fetch('/api/newsletter/subscribers?user_id=demo_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSubscriber)
      });

      const data = await response.json();
      setSubscribers(prev => [...prev, { id: data.id, ...newSubscriber, status: 'active' }]);
      setShowSubscriberModal(false);
      setNewSubscriber({
        email: '',
        name: '',
        phone: '',
        tags: []
      });
    } catch (error) {
      console.error('Failed to add subscriber:', error);
    }
  };

  const handleImportCSV = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/newsletter/subscribers/import?user_id=demo_user', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      alert(`Imported ${data.imported} subscribers`);
    } catch (error) {
      console.error('Failed to import CSV:', error);
    }
  };

  const handleSendCampaign = async (campaignId) => {
    try {
      const response = await fetch(`/api/newsletter/campaigns/${campaignId}/send?user_id=demo_user`, {
        method: 'POST'
      });

      const data = await response.json();
      setCampaigns(prev => prev.map(c => 
        c.id === campaignId ? { ...c, status: 'sent' } : c
      ));
      alert(`Campaign sent to ${data.sent} subscribers`);
    } catch (error) {
      console.error('Failed to send campaign:', error);
    }
  };

  const filteredSubscribers = subscribers.filter(s =>
    s.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container>
      <Sidebar>
        <Logo>
          <Mail />
          Newsletter
        </Logo>

        <NavMenu>
          <NavItem
            active={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          >
            <BarChart3 />
            Dashboard
          </NavItem>
          <NavItem
            active={activeTab === 'campaigns'}
            onClick={() => setActiveTab('campaigns')}
          >
            <Mail />
            Campaigns
          </NavItem>
          <NavItem
            active={activeTab === 'subscribers'}
            onClick={() => setActiveTab('subscribers')}
          >
            <Users />
            Subscribers
          </NavItem>
          <NavItem
            active={activeTab === 'templates'}
            onClick={() => setActiveTab('templates')}
          >
            <Palette />
            Templates
          </NavItem>
          <NavItem
            active={activeTab === 'automation'}
            onClick={() => setActiveTab('automation')}
          >
            <Zap />
            Automation
          </NavItem>
          <NavItem
            active={activeTab === 'settings'}
            onClick={() => setActiveTab('settings')}
          >
            <Settings />
            Settings
          </NavItem>
        </NavMenu>
      </Sidebar>

      <MainContent>
        <TopBar>
          <PageTitle>
            {activeTab === 'dashboard' && 'Analytics Dashboard'}
            {activeTab === 'campaigns' && 'Email Campaigns'}
            {activeTab === 'subscribers' && 'Subscriber List'}
            {activeTab === 'templates' && 'Email Templates'}
            {activeTab === 'automation' && 'Automation Workflows'}
            {activeTab === 'settings' && 'Settings'}
          </PageTitle>
          <UserInfo>
            <span>Welcome Back!</span>
            <Button className="secondary"><LogOut size={16} /></Button>
          </UserInfo>
        </TopBar>

        <Content>
          {/* DASHBOARD TAB */}
          {activeTab === 'dashboard' && (
            <>
              <MetricsGrid>
                <MetricCard>
                  <MetricIcon><Users /></MetricIcon>
                  <MetricLabel>Total Subscribers</MetricLabel>
                  <MetricValue>{analytics.subscribers}</MetricValue>
                </MetricCard>
                <MetricCard>
                  <MetricIcon><Mail /></MetricIcon>
                  <MetricLabel>Campaigns Created</MetricLabel>
                  <MetricValue>{analytics.campaigns_created}</MetricValue>
                </MetricCard>
                <MetricCard>
                  <MetricIcon><Send /></MetricIcon>
                  <MetricLabel>Total Emails Sent</MetricLabel>
                  <MetricValue>{analytics.total_sent}</MetricValue>
                </MetricCard>
                <MetricCard>
                  <MetricIcon><Eye /></MetricIcon>
                  <MetricLabel>Open Rate</MetricLabel>
                  <MetricValue>{analytics.avg_open_rate}%</MetricValue>
                </MetricCard>
                <MetricCard>
                  <MetricIcon><ArrowRight /></MetricIcon>
                  <MetricLabel>Click Rate</MetricLabel>
                  <MetricValue>{analytics.avg_click_rate}%</MetricValue>
                </MetricCard>
                <MetricCard>
                  <MetricIcon><TrendingUp /></MetricIcon>
                  <MetricLabel>Total Opens</MetricLabel>
                  <MetricValue>{analytics.total_opens}</MetricValue>
                </MetricCard>
              </MetricsGrid>

              <div>
                <SectionTitle>Campaign Performance</SectionTitle>
                <AnalyticsChart>
                  <ChartBar height={75}>
                    <div />
                    <span>Sent</span>
                  </ChartBar>
                  <ChartBar height={45}>
                    <div />
                    <span>Opens</span>
                  </ChartBar>
                  <ChartBar height={22}>
                    <div />
                    <span>Clicks</span>
                  </ChartBar>
                  <ChartBar height={8}>
                    <div />
                    <span>Unsub</span>
                  </ChartBar>
                </AnalyticsChart>
              </div>
            </>
          )}

          {/* CAMPAIGNS TAB */}
          {activeTab === 'campaigns' && (
            <>
              <SectionHeader>
                <SectionTitle>Email Campaigns</SectionTitle>
                <Button onClick={() => setShowCampaignModal(true)}>
                  <Plus size={16} />
                  New Campaign
                </Button>
              </SectionHeader>

              {campaigns.length === 0 ? (
                <EmptyState>
                  <Mail />
                  <p>No campaigns yet. Create your first campaign to get started.</p>
                  <Button onClick={() => setShowCampaignModal(true)}>
                    <Plus size={16} />
                    Create Campaign
                  </Button>
                </EmptyState>
              ) : (
                <Table>
                  <thead>
                    <tr>
                      <th>Campaign Name</th>
                      <th>Status</th>
                      <th>Recipients</th>
                      <th>Opens</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {campaigns.map(campaign => (
                      <tr key={campaign.id}>
                        <td><strong>{campaign.name}</strong></td>
                        <td><CampaignStatus status={campaign.status || 'draft'}>{campaign.status || 'Draft'}</CampaignStatus></td>
                        <td>450</td>
                        <td>125 (28%)</td>
                        <td>
                          <ActionBar>
                            <Button className="secondary" onClick={() => handleSendCampaign(campaign.id)}>
                              <Send size={14} />
                            </Button>
                            <Button className="secondary">
                              <Edit2 size={14} />
                            </Button>
                            <Button className="secondary danger">
                              <Trash2 size={14} />
                            </Button>
                          </ActionBar>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </>
          )}

          {/* SUBSCRIBERS TAB */}
          {activeTab === 'subscribers' && (
            <>
              <SectionHeader>
                <div style={{ flex: 1 }}>
                  <SectionTitle style={{ marginBottom: '12px' }}>Subscriber List</SectionTitle>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{ flex: 1, position: 'relative' }}>
                      <Search style={{ position: 'absolute', left: '12px', top: '12px', width: '16px', height: '16px', color: '#a0aec0' }} />
                      <input
                        type="text"
                        placeholder="Search subscribers..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                          width: '100%',
                          paddingLeft: '36px',
                          paddingRight: '12px',
                          paddingTop: '10px',
                          paddingBottom: '10px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px',
                          color: '#fff',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                  </div>
                </div>
                <ActionBar>
                  <Button onClick={() => setShowSubscriberModal(true)}>
                    <Plus size={16} />
                    Add Subscriber
                  </Button>
                  <Button className="secondary" onClick={() => fileInputRef.current?.click()}>
                    <Upload size={16} />
                    Import CSV
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleImportCSV}
                    style={{ display: 'none' }}
                  />
                  <Button className="secondary">
                    <Download size={16} />
                    Export
                  </Button>
                </ActionBar>
              </SectionHeader>

              {filteredSubscribers.length === 0 ? (
                <EmptyState>
                  <Users />
                  <p>No subscribers yet. Add your first subscriber or import from CSV.</p>
                  <Button onClick={() => setShowSubscriberModal(true)}>
                    <Plus size={16} />
                    Add Subscriber
                  </Button>
                </EmptyState>
              ) : (
                <Table>
                  <thead>
                    <tr>
                      <th>Email</th>
                      <th>Name</th>
                      <th>Tags</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSubscribers.map(subscriber => (
                      <tr key={subscriber.email}>
                        <td>{subscriber.email}</td>
                        <td>{subscriber.name}</td>
                        <td>
                          <TagsContainer>
                            {subscriber.tags?.map(tag => (
                              <TagStyled key={tag}>{tag}</TagStyled>
                            ))}
                          </TagsContainer>
                        </td>
                        <td><CampaignStatus status={subscriber.status}>{subscriber.status}</CampaignStatus></td>
                        <td>
                          <ActionBar>
                            <Button className="secondary"><Edit2 size={14} /></Button>
                            <Button className="secondary danger"><Trash2 size={14} /></Button>
                          </ActionBar>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </>
          )}

          {/* TEMPLATES TAB */}
          {activeTab === 'templates' && (
            <>
              <SectionHeader>
                <SectionTitle>Email Templates</SectionTitle>
                <Button>
                  <Plus size={16} />
                  New Template
                </Button>
              </SectionHeader>

              <EmptyState>
                <Palette />
                <p>No custom templates yet. Create professional email templates to use in campaigns.</p>
                <Button>
                  <Plus size={16} />
                  Create Template
                </Button>
              </EmptyState>
            </>
          )}

          {/* AUTOMATION TAB */}
          {activeTab === 'automation' && (
            <>
              <SectionHeader>
                <SectionTitle>Automation Workflows</SectionTitle>
                <Button onClick={() => setShowAutomationModal(true)}>
                  <Plus size={16} />
                  New Workflow
                </Button>
              </SectionHeader>

              <EmptyState>
                <Zap />
                <p>No automation workflows yet. Create workflows to send emails automatically based on triggers.</p>
                <Button onClick={() => setShowAutomationModal(true)}>
                  <Plus size={16} />
                  Create Workflow
                </Button>
              </EmptyState>
            </>
          )}

          {/* SETTINGS TAB */}
          {activeTab === 'settings' && (
            <>
              <SectionTitle>SMTP Configuration</SectionTitle>

              <FormGroup>
                <label>SMTP Host</label>
                <input type="text" placeholder="smtp.gmail.com" />
              </FormGroup>

              <FormRow>
                <FormGroup>
                  <label>SMTP Port</label>
                  <input type="number" placeholder="587" />
                </FormGroup>
                <FormGroup>
                  <label>Use TLS</label>
                  <input type="checkbox" />
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <label>Email Address</label>
                  <input type="email" placeholder="your-email@gmail.com" />
                </FormGroup>
                <FormGroup>
                  <label>Display Name</label>
                  <input type="text" placeholder="Newsletter" />
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <label>Username</label>
                  <input type="text" placeholder="username" />
                </FormGroup>
                <FormGroup>
                  <label>Password</label>
                  <input type="password" placeholder="••••••••" />
                </FormGroup>
              </FormRow>

              <ActionBar>
                <Button>Save Configuration</Button>
                <Button className="secondary">Test Connection</Button>
              </ActionBar>
            </>
          )}
        </Content>
      </MainContent>

      {/* CREATE CAMPAIGN MODAL */}
      {showCampaignModal && (
        <Modal onClick={() => setShowCampaignModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <h2>Create Email Campaign</h2>
              <button onClick={() => setShowCampaignModal(false)}>
                <X size={20} />
              </button>
            </ModalHeader>

            <FormGroup>
              <label>Campaign Name *</label>
              <input
                type="text"
                placeholder="My Awesome Campaign"
                value={newCampaign.name}
                onChange={(e) => setNewCampaign(prev => ({ ...prev, name: e.target.value }))}
              />
            </FormGroup>

            <FormGroup>
              <label>Email Subject *</label>
              <input
                type="text"
                placeholder="Hello {{name}}, check this out!"
                value={newCampaign.subject}
                onChange={(e) => setNewCampaign(prev => ({ ...prev, subject: e.target.value }))}
              />
              <VariableHint>
                <span onClick={() => setNewCampaign(prev => ({ ...prev, subject: prev.subject + ' {{name}}' }))}>{{name}}</span>
                <span onClick={() => setNewCampaign(prev => ({ ...prev, subject: prev.subject + ' {{email}}' }))}>{{email}}</span>
                <span onClick={() => setNewCampaign(prev => ({ ...prev, subject: prev.subject + ' {{company}}' }))}>{{company}}</span>
              </VariableHint>
            </FormGroup>

            <FormGroup>
              <label>Preview Text</label>
              <input
                type="text"
                placeholder="This text appears in inbox preview"
                value={newCampaign.preview_text}
                onChange={(e) => setNewCampaign(prev => ({ ...prev, preview_text: e.target.value }))}
              />
            </FormGroup>

            <FormGroup>
              <label>Email Content (HTML) *</label>
              <TemplateEditor>
                <textarea
                  placeholder="<h1>Hello {{name}}</h1><p>Welcome to our newsletter!</p>"
                  value={newCampaign.html_content}
                  onChange={(e) => setNewCampaign(prev => ({ ...prev, html_content: e.target.value }))}
                />
              </TemplateEditor>
            </FormGroup>

            <FormGroup>
              <label>Segment By Tags</label>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                <input
                  type="text"
                  placeholder="Add tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addTag(e)}
                />
                <Button onClick={addTag}>Add</Button>
              </div>
              {newCampaign.tags.length > 0 && (
                <TagsContainer>
                  {newCampaign.tags.map(tag => (
                    <TagStyled key={tag}>
                      {tag}
                      <button onClick={() => removeTag(tag)}>×</button>
                    </TagStyled>
                  ))}
                </TagsContainer>
              )}
            </FormGroup>

            <ActionBar>
              <Button onClick={handleCreateCampaign}>Create Campaign</Button>
              <Button className="secondary" onClick={() => setShowCampaignModal(false)}>Cancel</Button>
            </ActionBar>
          </ModalContent>
        </Modal>
      )}

      {/* ADD SUBSCRIBER MODAL */}
      {showSubscriberModal && (
        <Modal onClick={() => setShowSubscriberModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <h2>Add Subscriber</h2>
              <button onClick={() => setShowSubscriberModal(false)}>
                <X size={20} />
              </button>
            </ModalHeader>

            <FormGroup>
              <label>Email *</label>
              <input
                type="email"
                placeholder="subscriber@example.com"
                value={newSubscriber.email}
                onChange={(e) => setNewSubscriber(prev => ({ ...prev, email: e.target.value }))}
              />
            </FormGroup>

            <FormGroup>
              <label>Name *</label>
              <input
                type="text"
                placeholder="John Doe"
                value={newSubscriber.name}
                onChange={(e) => setNewSubscriber(prev => ({ ...prev, name: e.target.value }))}
              />
            </FormGroup>

            <FormGroup>
              <label>Phone</label>
              <input
                type="tel"
                placeholder="+1 (555) 123-4567"
                value={newSubscriber.phone}
                onChange={(e) => setNewSubscriber(prev => ({ ...prev, phone: e.target.value }))}
              />
            </FormGroup>

            <FormGroup>
              <label>Tags</label>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                <input
                  type="text"
                  placeholder="Add tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addSubscriberTag(e)}
                />
                <Button onClick={addSubscriberTag}>Add</Button>
              </div>
              {newSubscriber.tags.length > 0 && (
                <TagsContainer>
                  {newSubscriber.tags.map(tag => (
                    <TagStyled key={tag}>
                      {tag}
                      <button onClick={() => removeSubscriberTag(tag)}>×</button>
                    </TagStyled>
                  ))}
                </TagsContainer>
              )}
            </FormGroup>

            <ActionBar>
              <Button onClick={handleAddSubscriber}>Add Subscriber</Button>
              <Button className="secondary" onClick={() => setShowSubscriberModal(false)}>Cancel</Button>
            </ActionBar>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
}