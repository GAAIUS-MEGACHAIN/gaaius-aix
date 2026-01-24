import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Heart, DollarSign, Users, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #EC4899 0%, #F43F5E 100%);
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

const DonationTier = styled.div`
  background: ${props => props.color || '#f0f0f0'};
  padding: 15px;
  border-radius: 8px;
  margin: 10px 0;
`;

const TierName = styled.div`
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
`;

const TierAmount = styled.div`
  font-size: 1.3rem;
  color: #EC4899;
  font-weight: bold;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin: 10px 0;

  & > div {
    height: 100%;
    background: linear-gradient(90deg, #EC4899 0%, #F43F5E 100%);
    transition: width 0.3s;
  }
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
  background: #EC4899;
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
    background: #d81b60;
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
    border-color: #EC4899;
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  min-height: 100px;
  resize: vertical;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #EC4899;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #EC4899;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #d81b60;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(236, 72, 153, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const DonationTab = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    title: '',
    goal: 1000,
    description: ''
  });

  const mockCampaigns = [
    {
      id: 1,
      title: 'Community Support Fund',
      goal: 5000,
      raised: 3840.50,
      donors: 234,
      tiers: [
        { name: '$5 Supporter', count: 145 },
        { name: '$10 Helper', count: 67 },
        { name: '$25 Champion', count: 18 },
        { name: '$50+ Hero', count: 4 }
      ],
      status: 'Active'
    },
    {
      id: 2,
      title: 'Emergency Relief Campaign',
      goal: 10000,
      raised: 8750.75,
      donors: 567,
      tiers: [
        { name: '$1 Friend', count: 234 },
        { name: '$5 Supporter', count: 189 },
        { name: '$10 Helper', count: 98 },
        { name: '$50+ Hero', count: 46 }
      ],
      status: 'Active'
    },
    {
      id: 3,
      title: 'Creator Sustainability',
      goal: 3000,
      raised: 2100.25,
      donors: 156,
      tiers: [
        { name: '$3 Subscriber', count: 89 },
        { name: '$10 Fan', count: 45 },
        { name: '$25 Supporter', count: 18 },
        { name: '$100+ VIP', count: 4 }
      ],
      status: 'Active'
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
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/donation/campaigns`,
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
      [name]: name === 'goal' ? parseFloat(value) : value
    }));
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();

    if (!formData.title || !formData.goal) {
      toast.error('Please fill in required fields');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/donation/create`,
        {
          title: formData.title,
          goal: formData.goal,
          description: formData.description
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const newCampaign = {
        id: campaigns.length + 1,
        title: formData.title,
        goal: formData.goal,
        raised: 0,
        donors: 0,
        tiers: [],
        status: 'Active'
      };

      setCampaigns(prev => [newCampaign, ...prev]);
      setFormData({ title: '', goal: 1000, description: '' });
      setShowCreateForm(false);
      toast.success('Donation campaign created!');
      fetchCampaigns();
    } catch (error) {
      console.error('Error creating campaign:', error);
      toast.error('Failed to create campaign');
    }
  };

  if (loading) {
    return <Container><Title><Heart /> Loading campaigns...</Title></Container>;
  }

  const totalRaised = campaigns.reduce((sum, c) => sum + c.raised, 0);
  const totalDonors = campaigns.reduce((sum, c) => sum + c.donors, 0);
  const totalGoal = campaigns.reduce((sum, c) => sum + c.goal, 0);

  return (
    <Container>
      <Header>
        <Title>
          <Heart /> Donation Campaigns
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> New Campaign
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create Donation Campaign</h2>
          <form onSubmit={handleCreateCampaign}>
            <FormGroup>
              <Label>Campaign Title *</Label>
              <Input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., Community Support Fund"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Fundraising Goal ($) *</Label>
              <Input
                type="number"
                name="goal"
                value={formData.goal}
                onChange={handleInputChange}
                min="100"
                step="100"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Tell donors what you're raising funds for..."
              />
            </FormGroup>

            <SubmitButton type="submit">Create Campaign</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {campaigns.map(campaign => {
          const progress = (campaign.raised / campaign.goal) * 100;
          return (
            <Card key={campaign.id}>
              <CardTitle>
                <Heart size={20} /> {campaign.title}
              </CardTitle>

              <StatsGrid>
                <StatBox color="#FCE7F3">
                  <div>Amount Raised</div>
                  <div>${campaign.raised.toFixed(2)}</div>
                </StatBox>
                <StatBox color="#FCE7F3">
                  <div>Goal</div>
                  <div>${campaign.goal.toFixed(2)}</div>
                </StatBox>
                <StatBox color="#FBCFE8">
                  <div>Donors</div>
                  <div>{campaign.donors.toLocaleString()}</div>
                </StatBox>
                <StatBox color="#FBCFE8">
                  <div>Progress</div>
                  <div>{progress.toFixed(0)}%</div>
                </StatBox>
              </StatsGrid>

              <ProgressBar>
                <div style={{ width: `${Math.min(progress, 100)}%` }} />
              </ProgressBar>

              <div style={{ margin: '15px 0' }}>
                <strong>Donation Tiers:</strong>
                {campaign.tiers.map((tier, idx) => (
                  <DonationTier key={idx} color="#FCE7F3">
                    <TierName>{tier.name}</TierName>
                    <TierAmount>{tier.count} donors</TierAmount>
                  </DonationTier>
                ))}
              </div>

              <ButtonGroup>
                <SmallButton>
                  <Heart size={16} /> Share Campaign
                </SmallButton>
                <SmallButton>
                  <TrendingUp size={16} /> Analytics
                </SmallButton>
              </ButtonGroup>
            </Card>
          );
        })}
      </GridContainer>

      <Card style={{ background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%)' }}>
        <h3>Donation Overview</h3>
        <StatsGrid>
          <StatBox color="#FBCFE8">
            <div>Total Raised</div>
            <div>${totalRaised.toFixed(2)}</div>
          </StatBox>
          <StatBox color="#FBCFE8">
            <div>Total Goal</div>
            <div>${totalGoal.toFixed(2)}</div>
          </StatBox>
          <StatBox color="#FCE7F3">
            <div>Total Donors</div>
            <div>{totalDonors.toLocaleString()}</div>
          </StatBox>
          <StatBox color="#FCE7F3">
            <div>Campaign Count</div>
            <div>{campaigns.length}</div>
          </StatBox>
        </StatsGrid>
      </Card>
    </Container>
  );
};

export default DonationTab;
