import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Mail, Users, Send, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
  min-height: 100vh;
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.8rem;
  }
`;

const Button = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
  }
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  color: #333;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin: 15px 0;
`;

const StatBox = styled.div`
  background: ${props => props.color || '#f0f0f0'};
  padding: 15px;
  border-radius: 8px;
  text-align: center;

  & > div:first-child {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 5px;
  }

  & > div:last-child {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
  }
`;

const Badge = styled.span`
  display: inline-block;
  background: ${props => {
    switch(props.status) {
      case 'Sent': return '#4CAF50';
      case 'Draft': return '#FF9800';
      case 'Scheduled': return '#2196F3';
      default: return '#999';
    }
  }};
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  margin-top: 10px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;

  & > button {
    flex: 1;
  }
`;

const SmallButton = styled.button`
  background: #667EEA;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: all 0.3s;

  &:hover {
    background: #5568d3;
    transform: translateY(-1px);
  }
`;

const FormContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 600px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
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
    border-color: #667EEA;
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  min-height: 150px;
  resize: vertical;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #667EEA;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #667EEA;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #5568d3;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const NewsletterTab = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    subject: '',
    content: '',
    sendAt: ''
  });

  const mockCampaigns = [
    {
      id: 1,
      subject: 'Weekly Tech Updates - January 2026',
      subscribers: 12450,
      openRate: 34.5,
      clickRate: 8.2,
      sentDate: '2026-01-15',
      status: 'Sent',
      revenue: 2340.50
    },
    {
      id: 2,
      subject: 'New Features Release Announcement',
      subscribers: 11890,
      openRate: 41.2,
      clickRate: 12.8,
      sentDate: '2026-01-12',
      status: 'Sent',
      revenue: 3120.75
    },
    {
      id: 3,
      subject: 'Exclusive Offer - Limited Time',
      subscribers: 13200,
      openRate: 0,
      clickRate: 0,
      sentDate: '2026-01-20',
      status: 'Scheduled',
      revenue: 0
    },
    {
      id: 4,
      subject: 'Monthly Digest - Best Articles',
      subscribers: 12100,
      openRate: 0,
      clickRate: 0,
      sentDate: '2026-01-18',
      status: 'Draft',
      revenue: 0
    }
  ];

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/newsletter/campaigns`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setCampaigns(response.data.campaigns || mockCampaigns);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      setCampaigns(mockCampaigns);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();

    if (!formData.subject || !formData.content) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/newsletter/create`,
        {
          subject: formData.subject,
          content: formData.content,
          sendAt: formData.sendAt || null
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const newCampaign = {
        id: campaigns.length + 1,
        subject: formData.subject,
        subscribers: 0,
        openRate: 0,
        clickRate: 0,
        sentDate: new Date().toISOString().split('T')[0],
        status: formData.sendAt ? 'Scheduled' : 'Draft',
        revenue: 0
      };

      setCampaigns(prev => [newCampaign, ...prev]);
      setFormData({ subject: '', content: '', sendAt: '' });
      setShowCreateForm(false);
      toast.success('Campaign created successfully!');
      fetchCampaigns();
    } catch (error) {
      console.error('Error creating campaign:', error);
      toast.error('Failed to create campaign');
    }
  };

  if (loading) {
    return <Container><Title><Mail /> Loading campaigns...</Title></Container>;
  }

  const totalSubscribers = campaigns.reduce((sum, c) => sum + c.subscribers, 0);
  const avgOpenRate = campaigns.filter(c => c.status === 'Sent').length > 0
    ? (campaigns.filter(c => c.status === 'Sent').reduce((sum, c) => sum + c.openRate, 0) / campaigns.filter(c => c.status === 'Sent').length).toFixed(1)
    : 0;
  const totalRevenue = campaigns.reduce((sum, c) => sum + c.revenue, 0);

  return (
    <Container>
      <Header>
        <Title>
          <Mail /> Newsletter Management
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> New Campaign
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create Newsletter Campaign</h2>
          <form onSubmit={handleCreateCampaign}>
            <FormGroup>
              <Label>Subject Line *</Label>
              <Input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleInputChange}
                placeholder="e.g., Weekly Newsletter - January 2026"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Email Content *</Label>
              <Textarea
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                placeholder="Write your newsletter content here..."
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Schedule Send (Optional)</Label>
              <Input
                type="datetime-local"
                name="sendAt"
                value={formData.sendAt}
                onChange={handleInputChange}
              />
            </FormGroup>

            <SubmitButton type="submit">Create Campaign</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {campaigns.map(campaign => (
          <Card key={campaign.id}>
            <CardTitle>
              <Mail size={20} /> {campaign.subject}
            </CardTitle>

            <Badge status={campaign.status}>{campaign.status}</Badge>

            <StatsGrid>
              <StatBox color="#E8D5F2">
                <div>Subscribers</div>
                <div>{campaign.subscribers.toLocaleString()}</div>
              </StatBox>
              <StatBox color="#E8D5F2">
                <div>Open Rate</div>
                <div>{campaign.openRate}%</div>
              </StatBox>
              <StatBox color="#D5C9E8">
                <div>Click Rate</div>
                <div>{campaign.clickRate}%</div>
              </StatBox>
              <StatBox color="#D5C9E8">
                <div>Revenue</div>
                <div>${campaign.revenue.toFixed(2)}</div>
              </StatBox>
            </StatsGrid>

            <div style={{ marginTop: '15px', fontSize: '0.9rem', color: '#666' }}>
              <strong>Sent:</strong> {campaign.sentDate}
            </div>

            <ButtonGroup>
              <SmallButton>
                <Send size={16} /> {campaign.status === 'Draft' ? 'Send' : 'Resend'}
              </SmallButton>
              <SmallButton>
                <TrendingUp size={16} /> Analytics
              </SmallButton>
            </ButtonGroup>
          </Card>
        ))}
      </GridContainer>

      <Card style={{ background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)' }}>
        <h3>Newsletter Overview</h3>
        <StatsGrid>
          <StatBox color="#D5C9E8">
            <div>Total Subscribers</div>
            <div>{totalSubscribers.toLocaleString()}</div>
          </StatBox>
          <StatBox color="#D5C9E8">
            <div>Avg Open Rate</div>
            <div>{avgOpenRate}%</div>
          </StatBox>
          <StatBox color="#E8D5F2">
            <div>Total Revenue</div>
            <div>${totalRevenue.toFixed(2)}</div>
          </StatBox>
          <StatBox color="#E8D5F2">
            <div>Total Campaigns</div>
            <div>{campaigns.length}</div>
          </StatBox>
        </StatsGrid>
      </Card>
    </Container>
  );
};

export default NewsletterTab;
