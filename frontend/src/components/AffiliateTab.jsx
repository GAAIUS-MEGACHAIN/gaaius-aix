import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Copy, TrendingUp, Users, DollarSign, Link } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
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

const LinkBox = styled.div`
  background: #f0f0f0;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  word-break: break-all;
  font-size: 0.9rem;
  color: #666;
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
  background: #FF6B35;
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
    background: #ff5520;
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
    border-color: #FF6B35;
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
    border-color: #FF6B35;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #FF6B35;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #ff5520;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const AffiliateTab = () => {
  const [affiliates, setAffiliates] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    commission: 10,
    description: ''
  });

  const mockAffiliates = [
    {
      id: 1,
      name: 'Tech Influencer Co',
      email: 'contact@techinfluencer.com',
      link: 'https://affiliate.platform.com/ref/tech123',
      clicks: 4523,
      conversions: 287,
      revenue: 5750.50,
      commission: 15,
      status: 'Active',
      joinedDate: '2024-01-15'
    },
    {
      id: 2,
      name: 'Creator Network',
      email: 'partners@creatornetwork.io',
      link: 'https://affiliate.platform.com/ref/creator456',
      clicks: 3201,
      conversions: 156,
      revenue: 2340.75,
      commission: 10,
      status: 'Active',
      joinedDate: '2024-02-20'
    },
    {
      id: 3,
      name: 'Marketing Hub',
      email: 'sales@marketinghub.com',
      link: 'https://affiliate.platform.com/ref/mktg789',
      clicks: 5890,
      conversions: 412,
      revenue: 8270.00,
      commission: 12,
      status: 'Active',
      joinedDate: '2024-01-05'
    }
  ];

  useEffect(() => {
    fetchAffiliates();
  }, []);

  const fetchAffiliates = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/affiliate/links`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setAffiliates(response.data.affiliates || mockAffiliates);
    } catch (error) {
      console.error('Error fetching affiliates:', error);
      setAffiliates(mockAffiliates);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'commission' ? parseInt(value) : value
    }));
  };

  const handleCreateAffiliate = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.email) {
      toast.error('Please fill in required fields');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/affiliate/create`,
        {
          name: formData.name,
          email: formData.email,
          commission: formData.commission,
          description: formData.description
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const newAffiliate = {
        id: affiliates.length + 1,
        ...formData,
        link: `https://affiliate.platform.com/ref/${formData.name.replace(/\s+/g, '').toLowerCase()}${Date.now()}`,
        clicks: 0,
        conversions: 0,
        revenue: 0,
        status: 'Pending',
        joinedDate: new Date().toISOString().split('T')[0]
      };

      setAffiliates(prev => [newAffiliate, ...prev]);
      setFormData({ name: '', email: '', commission: 10, description: '' });
      setShowCreateForm(false);
      toast.success('Affiliate program created!');
      fetchAffiliates();
    } catch (error) {
      console.error('Error creating affiliate:', error);
      toast.error('Failed to create affiliate program');
    }
  };

  const copyLink = (link) => {
    navigator.clipboard.writeText(link);
    toast.success('Link copied to clipboard!');
  };

  const conversionRate = (clicks) => {
    if (!clicks) return '0%';
    const rate = (affiliates.length > 0 ? (affiliates[0]?.conversions || 0) / clicks : 0) * 100;
    return `${rate.toFixed(2)}%`;
  };

  if (loading) {
    return <Container><Title><Link /> Loading affiliates...</Title></Container>;
  }

  return (
    <Container>
      <Header>
        <Title>
          <Link /> Affiliate Marketing
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> New Affiliate
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create Affiliate Program</h2>
          <form onSubmit={handleCreateAffiliate}>
            <FormGroup>
              <Label>Affiliate Name *</Label>
              <Input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Marketing Agency Name"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Email Address *</Label>
              <Input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="contact@affiliate.com"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Commission Rate (%)</Label>
              <Input
                type="number"
                name="commission"
                value={formData.commission}
                onChange={handleInputChange}
                min="1"
                max="50"
              />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="About your affiliate program..."
              />
            </FormGroup>

            <SubmitButton type="submit">Create Affiliate Program</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {affiliates.map(affiliate => (
          <Card key={affiliate.id}>
            <CardTitle>
              <Users size={20} /> {affiliate.name}
            </CardTitle>

            <StatsGrid>
              <StatBox color="#FFE5D9">
                <div>Total Clicks</div>
                <div>{affiliate.clicks.toLocaleString()}</div>
              </StatBox>
              <StatBox color="#FFE5D9">
                <div>Conversions</div>
                <div>{affiliate.conversions.toLocaleString()}</div>
              </StatBox>
              <StatBox color="#FFD9CC">
                <div>Commission Rate</div>
                <div>{affiliate.commission}%</div>
              </StatBox>
              <StatBox color="#FFD9CC">
                <div>Conv. Rate</div>
                <div>
                  {affiliate.clicks > 0 
                    ? ((affiliate.conversions / affiliate.clicks) * 100).toFixed(2) 
                    : 0}%
                </div>
              </StatBox>
            </StatsGrid>

            <StatBox color="#FFC4A6" style={{ marginTop: '15px', textAlign: 'left' }}>
              <div style={{ fontSize: '0.85rem' }}>Total Revenue Generated</div>
              <div style={{ fontSize: '1.8rem' }}>${affiliate.revenue.toFixed(2)}</div>
            </StatBox>

            <LinkBox>
              <Link size={16} />
              {affiliate.link}
            </LinkBox>

            <ButtonGroup>
              <SmallButton onClick={() => copyLink(affiliate.link)}>
                <Copy size={16} /> Copy Link
              </SmallButton>
              <SmallButton>
                <TrendingUp size={16} /> Analytics
              </SmallButton>
            </ButtonGroup>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default AffiliateTab;
