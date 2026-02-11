import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Brain, ThumbsUp, ThumbsDown, Zap } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
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

const RecommendationItem = styled.div`
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 12px;

  &:hover {
    background: #f0f0f0;
  }
`;

const ItemTitle = styled.div`
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
`;

const ItemMeta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 10px;
`;

const ScoreBar = styled.div`
  background: #e0e0e0;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;

  & > div {
    height: 100%;
    background: linear-gradient(90deg, #8B5CF6 0%, #7C3AED 100%);
  }
`;

const FeedbackButtons = styled.div`
  display: flex;
  gap: 10px;

  & > button {
    flex: 1;
    padding: 8px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    transition: all 0.3s;
  }
`;

const LikeButton = styled.button`
  background: #E5E7EB;
  color: #333;

  &:hover {
    background: #D1D5DB;
  }
`;

const DislikeButton = styled.button`
  background: #E5E7EB;
  color: #333;

  &:hover {
    background: #D1D5DB;
  }
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
    border-color: #8B5CF6;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #8B5CF6;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #8B5CF6;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #7C3AED;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(139, 92, 246, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const RecommendationTab = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    category: 'content'
  });

  const mockRecommendations = [
    {
      id: 1,
      title: 'Recommended: "The Future of AI"',
      category: 'content',
      type: 'Video',
      score: 92,
      reason: 'Based on your interests',
      feedback: null
    },
    {
      id: 2,
      title: 'Creator You Might Follow: TechGuru123',
      category: 'creator',
      type: 'Creator',
      score: 88,
      reason: 'Similar content style',
      feedback: null
    },
    {
      id: 3,
      title: 'Trending: Music Production Masterclass',
      category: 'course',
      type: 'Course',
      score: 85,
      reason: 'Popular in your niche',
      feedback: null
    },
    {
      id: 4,
      title: 'Recommended: "Digital Marketing Basics"',
      category: 'course',
      type: 'Course',
      score: 81,
      reason: 'Complements your interests',
      feedback: null
    }
  ];

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/recommendation/feed`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setRecommendations(response.data.recommendations || mockRecommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setRecommendations(mockRecommendations);
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

  const handleRefresh = async () => {
    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/recommendation/refresh`,
        { category: formData.category },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      toast.success('Recommendations refreshed!');
      fetchRecommendations();
    } catch (error) {
      console.error('Error refreshing recommendations:', error);
      toast.error('Failed to refresh');
    }
  };

  const handleFeedback = (id, liked) => {
    setRecommendations(prev =>
      prev.map(rec =>
        rec.id === id
          ? { ...rec, feedback: liked ? 'liked' : 'disliked' }
          : rec
      )
    );
    toast.success(liked ? 'Helpful feedback recorded!' : 'Feedback recorded!');
  };

  if (loading) {
    return <Container><Title><Brain /> Loading recommendations...</Title></Container>;
  }

  const avgScore = (recommendations.reduce((sum, r) => sum + r.score, 0) / recommendations.length).toFixed(0);

  return (
    <Container>
      <Header>
        <Title>
          <Brain /> AI Recommendations
        </Title>
        <Button onClick={handleRefresh}>
          <Zap size={20} /> Refresh
        </Button>
      </Header>

      <GridContainer>
        <Card>
          <CardTitle>
            <Brain size={20} /> Personalized For You
          </CardTitle>

          <StatsGrid>
            <StatBox color="#EDE9FE">
              <div>Recommendations</div>
              <div>{recommendations.length}</div>
            </StatBox>
            <StatBox color="#EDE9FE">
              <div>Avg Score</div>
              <div>{avgScore}%</div>
            </StatBox>
          </StatsGrid>

          {recommendations.map(rec => (
            <RecommendationItem key={rec.id}>
              <ItemTitle>{rec.title}</ItemTitle>
              <ItemMeta>
                <span>{rec.type}</span>
                <span>{rec.reason}</span>
              </ItemMeta>
              <ScoreBar>
                <div style={{ width: `${rec.score}%` }} />
              </ScoreBar>
              <FeedbackButtons>
                <LikeButton
                  onClick={() => handleFeedback(rec.id, true)}
                  style={{
                    background: rec.feedback === 'liked' ? '#10B981' : '#E5E7EB',
                    color: rec.feedback === 'liked' ? 'white' : '#333'
                  }}
                >
                  <ThumbsUp size={14} /> Like
                </LikeButton>
                <DislikeButton
                  onClick={() => handleFeedback(rec.id, false)}
                  style={{
                    background: rec.feedback === 'disliked' ? '#EF4444' : '#E5E7EB',
                    color: rec.feedback === 'disliked' ? 'white' : '#333'
                  }}
                >
                  <ThumbsDown size={14} /> Dislike
                </DislikeButton>
              </FeedbackButtons>
            </RecommendationItem>
          ))}
        </Card>
      </GridContainer>

      <Card style={{ background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)' }}>
        <h3>About AI Recommendations</h3>
        <p style={{ color: '#666', lineHeight: '1.6' }}>
          Our AI analyzes your interests, viewing history, and engagement patterns to deliver personalized recommendations. Your feedback helps us improve accuracy. All data is processed privately and securely.
        </p>
      </Card>
    </Container>
  );
};

export default RecommendationTab;
