#!/usr/bin/env python3
# Write VideoEditorTab.jsx with recommendations

content = '''import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Tv, Scissors, Music, Edit, Download, Brain, ThumbsUp, ThumbsDown } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
  border-radius: 12px;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  justify-content: space-between;
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
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
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

const StatusBadge = styled.span`
  display: inline-block;
  background: rgba(34, 197, 94, 0.3);
  border: 1px solid rgba(34, 197, 94, 0.5);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin: 10px 0;
  color: rgba(134, 239, 172, 0.9);
`;

const RecommendationSection = styled.div`
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
`;

const RecommendationTitle = styled.h3`
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 18px;
`;

const RecommendationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
`;

const RecommendationCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 15px;
  color: #333;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
`;

const RecTitle = styled.div`
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
`;

const RecMeta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
`;

const ScoreBar = styled.div`
  background: #e0e0e0;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 10px;

  & > div {
    height: 100%;
    background: linear-gradient(90deg, #ef4444 0%, #991b1b 100%);
  }
`;

const FeedbackButtons = styled.div`
  display: flex;
  gap: 8px;

  & > button {
    flex: 1;
    padding: 6px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: all 0.3s;
    background: #E5E7EB;
    color: #333;

    &:hover {
      background: #D1D5DB;
    }
  }
`;

const VideoEditorTab = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  });

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api';
  const token = localStorage.getItem('gaaius_token');

  const mockRecommendations = [
    {
      id: 1,
      title: 'Advanced Color Grading Tutorial',
      type: 'Tutorial',
      score: 92,
      reason: 'Based on your edits',
      feedback: null
    },
    {
      id: 2,
      title: 'Motion Graphics Effects Pack',
      type: 'Resource',
      score: 88,
      reason: 'Trending in video editing',
      feedback: null
    },
    {
      id: 3,
      title: 'Pro Audio Mixing Guide',
      type: 'Tutorial',
      score: 85,
      reason: 'Complements your projects',
      feedback: null
    },
    {
      id: 4,
      title: '4K Export Optimization',
      type: 'Guide',
      score: 81,
      reason: 'Based on your project types',
      feedback: null
    }
  ];

  useEffect(() => {
    fetchProjects();
    fetchRecommendations();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/v1/video/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Failed to load video projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(
        `${API_BASE}/v1/recommendation/videos`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setRecommendations(response.data.recommendations || mockRecommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setRecommendations(mockRecommendations);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        `${API_BASE}/v1/video/projects`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Video project created!');
      setFormData({ title: '', description: '' });
      setShowCreateForm(false);
      fetchProjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleRecommendationFeedback = (id, liked) => {
    setRecommendations(prev =>
      prev.map(rec =>
        rec.id === id
          ? { ...rec, feedback: liked ? 'liked' : 'disliked' }
          : rec
      )
    );
    toast.success(liked ? 'Great! This helps us recommend better content' : 'Feedback recorded!');
  };

  return (
    <Container>
      <Header>
        <Title>
          <Tv size={32} />
          Video Editor
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)} style={{ width: 'auto' }}>
          {showCreateForm ? 'Cancel' : '+ New Project'}
        </Button>
      </Header>

      {showCreateForm && (
        <Card style={{ background: 'rgba(255, 255, 255, 0.15)' }}>
          <form onSubmit={handleCreateProject}>
            <input
              type="text"
              placeholder="Project Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              style={{
                width: '100%',
                padding: '10px',
                marginBottom: '10px',
                borderRadius: '8px',
                border: 'none',
                color: 'black'
              }}
              required
            />
            <textarea
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              style={{
                width: '100%',
                padding: '10px',
                marginBottom: '10px',
                borderRadius: '8px',
                border: 'none',
                color: 'black',
                minHeight: '60px'
              }}
            />
            <Button type="submit" style={{ background: 'rgba(239, 68, 68, 0.3)' }}>
              Create Project
            </Button>
          </form>
        </Card>
      )}

      <GridContainer>
        {projects.length === 0 && !loading ? (
          <Card style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
            <Title style={{ fontSize: '20px', justifyContent: 'center' }}>
              <Tv size={24} />
              No Projects Yet
            </Title>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Create your first video project to begin editing
            </p>
          </Card>
        ) : (
          projects.map((project) => (
            <Card key={project.project_id}>
              <h3 style={{ margin: '0 0 10px 0' }}>{project.title}</h3>
              <StatusBadge>
                {project.status === 'processing' ? 'Processing' : 'Ready'}
              </StatusBadge>
              <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)', marginTop: '10px' }}>
                <div style={{ margin: '8px 0' }}>
                  <Scissors size={14} style={{ display: 'inline', marginRight: '5px' }} />
                  Segments: {project.segments_count || 0}
                </div>
                <div style={{ margin: '8px 0' }}>
                  <Music size={14} style={{ display: 'inline', marginRight: '5px' }} />
                  Audio Tracks: {project.audio_tracks || 0}
                </div>
                <div style={{ margin: '8px 0' }}>
                  Duration: {project.duration || 'N/A'}
                </div>
              </div>
              <Button style={{ marginTop: '15px' }}>
                <Edit size={14} style={{ display: 'inline', marginRight: '5px' }} />
                Edit Project
              </Button>
              <Button style={{ marginTop: '10px' }}>
                <Download size={14} style={{ display: 'inline', marginRight: '5px' }} />
                Export
              </Button>
            </Card>
          ))
        )}
      </GridContainer>

      <RecommendationSection>
        <RecommendationTitle>
          <Brain size={20} /> Recommended For You
        </RecommendationTitle>
        <RecommendationGrid>
          {recommendations.map((rec) => (
            <RecommendationCard key={rec.id}>
              <RecTitle>{rec.title}</RecTitle>
              <RecMeta>
                <span>{rec.type}</span>
                <span>{rec.reason}</span>
              </RecMeta>
              <ScoreBar>
                <div style={{ width: `${rec.score}%` }} />
              </ScoreBar>
              <FeedbackButtons>
                <button
                  onClick={() => handleRecommendationFeedback(rec.id, true)}
                  style={{
                    background: rec.feedback === 'liked' ? '#10B981' : '#E5E7EB',
                    color: rec.feedback === 'liked' ? 'white' : '#333'
                  }}
                >
                  <ThumbsUp size={12} /> Like
                </button>
                <button
                  onClick={() => handleRecommendationFeedback(rec.id, false)}
                  style={{
                    background: rec.feedback === 'disliked' ? '#EF4444' : '#E5E7EB',
                    color: rec.feedback === 'disliked' ? 'white' : '#333'
                  }}
                >
                  <ThumbsDown size={12} /> Dislike
                </button>
              </FeedbackButtons>
            </RecommendationCard>
          ))}
        </RecommendationGrid>
      </RecommendationSection>
    </Container>
  );
};

export default VideoEditorTab;
'''

with open('f:\\gaaius-aiX\\gaaius-ai\\frontend\\src\\components\\VideoEditorTab.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("VideoEditorTab.jsx created successfully")
