import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Users, Play, Heart, Share2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #F97316 0%, #FB923C 100%);
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

const CreatorName = styled.div`
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 10px;
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

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;

  & > button {
    flex: 1;
    min-width: 80px;
  }
`;

const SmallButton = styled.button`
  background: #F97316;
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
    background: #ea580c;
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
    border-color: #F97316;
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
    border-color: #F97316;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #F97316;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #ea580c;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(249, 115, 22, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const DuetTab = () => {
  const [duets, setDuets] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  });

  const mockDuets = [
    {
      id: 1,
      title: 'Dance Challenge - Wave',
      creator1: 'Sarah Chen',
      creator2: 'Marcus Johnson',
      views: 245678,
      likes: 12340,
      shares: 890,
      duration: '0:45',
      status: 'Published'
    },
    {
      id: 2,
      title: 'Singing Duet - Harmony',
      creator1: 'Emma Wilson',
      creator2: 'James Lee',
      views: 189234,
      likes: 8945,
      shares: 567,
      duration: '2:15',
      status: 'Published'
    },
    {
      id: 3,
      title: 'Comedy Bit - Reactions',
      creator1: 'Alex Kumar',
      creator2: 'Taylor Brown',
      views: 125450,
      likes: 6234,
      shares: 345,
      duration: '1:30',
      status: 'Drafting'
    }
  ];

  useEffect(() => {
    fetchDuets();
  }, []);

  const fetchDuets = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/duet/list`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setDuets(response.data.duets || mockDuets);
    } catch (error) {
      console.error('Error fetching duets:', error);
      setDuets(mockDuets);
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

  const handleCreateDuet = async (e) => {
    e.preventDefault();

    if (!formData.title) {
      toast.error('Please enter duet title');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/duet/create`,
        {
          title: formData.title,
          description: formData.description
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setFormData({ title: '', description: '' });
      setShowCreateForm(false);
      toast.success('Duet created! Start collaborating.');
      fetchDuets();
    } catch (error) {
      console.error('Error creating duet:', error);
      toast.error('Failed to create duet');
    }
  };

  if (loading) {
    return <Container><Title><Users /> Loading duets...</Title></Container>;
  }

  return (
    <Container>
      <Header>
        <Title>
          <Users /> Duets & Collaborations
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> Start Duet
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create New Duet</h2>
          <form onSubmit={handleCreateDuet}>
            <FormGroup>
              <Label>Duet Title *</Label>
              <Input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., Dance Challenge - Wave"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Describe your duet idea..."
              />
            </FormGroup>

            <SubmitButton type="submit">Create Duet</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {duets.map(duet => (
          <Card key={duet.id}>
            <CardTitle>
              <Users size={20} /> {duet.title}
            </CardTitle>

            <CreatorName>
              {duet.creator1} × {duet.creator2}
            </CreatorName>

            <StatsGrid>
              <StatBox color="#FED7AA">
                <div>Views</div>
                <div>{(duet.views / 1000).toFixed(0)}K</div>
              </StatBox>
              <StatBox color="#FED7AA">
                <div>Likes</div>
                <div>{(duet.likes / 1000).toFixed(1)}K</div>
              </StatBox>
              <StatBox color="#FDBA74">
                <div>Shares</div>
                <div>{duet.shares.toLocaleString()}</div>
              </StatBox>
              <StatBox color="#FDBA74">
                <div>Duration</div>
                <div>{duet.duration}</div>
              </StatBox>
            </StatsGrid>

            <div style={{ marginTop: '15px', padding: '10px', background: '#FEF3C7', borderRadius: '6px', fontSize: '0.85rem', color: '#92400E' }}>
              <strong>Status:</strong> {duet.status}
            </div>

            <ButtonGroup>
              <SmallButton>
                <Play size={16} /> Play
              </SmallButton>
              <SmallButton>
                <Heart size={16} /> Like
              </SmallButton>
              <SmallButton>
                <Share2 size={16} /> Share
              </SmallButton>
            </ButtonGroup>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default DuetTab;
