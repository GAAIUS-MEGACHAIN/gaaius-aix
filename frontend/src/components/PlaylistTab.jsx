import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Music, Play, Trash2, Edit, Brain, ThumbsUp, ThumbsDown } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #A855F7 0%, #9333EA 100%);
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

const TrackList = styled.div`
  margin: 15px 0;
  max-height: 200px;
  overflow-y: auto;
`;

const Track = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 0.9rem;

  &:hover {
    background: #f0f0f0;
  }
`;

const TrackInfo = styled.div`
  flex: 1;
  overflow: hidden;

  & > div:first-child {
    font-weight: bold;
    color: #333;
  }

  & > div:last-child {
    font-size: 0.85rem;
    color: #999;
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
  background: #A855F7;
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
    background: #9333EA;
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
    border-color: #A855F7;
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
    border-color: #A855F7;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #A855F7;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #9333EA;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(168, 85, 247, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const RecommendationSection = styled.div`
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
`;

const RecommendationTitle = styled.h2`
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 1.8rem;
`;

const RecommendationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const RecommendationCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
`;

const RecTitle = styled.div`
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  font-size: 1rem;
`;

const RecMeta = styled.div`
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
  margin-bottom: 12px;

  & > div {
    height: 100%;
    background: linear-gradient(90deg, #A855F7 0%, #9333EA 100%);
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
    gap: 4px;
    transition: all 0.3s;
    background: #E5E7EB;
    color: #333;
    font-weight: 600;

    &:hover {
      background: #D1D5DB;
    }
  }
`;

const PlaylistTab = () => {
  const [playlists, setPlaylists] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  });

  const mockPlaylists = [
    {
      id: 1,
      title: 'Workout Mix 2026',
      description: 'High energy tracks for your gym sessions',
      tracks: 42,
      duration: '3h 24m',
      plays: 12340,
      followers: 567,
      songs: [
        { title: 'Energy Boost', artist: 'DJ Max', duration: '3:45' },
        { title: 'Running High', artist: 'Pulse Band', duration: '4:12' },
        { title: 'Feel Alive', artist: 'Thunder', duration: '3:28' }
      ]
    },
    {
      id: 2,
      title: 'Chill Vibes Evening',
      description: 'Relaxing music for your evening',
      tracks: 38,
      duration: '2h 56m',
      plays: 8920,
      followers: 423,
      songs: [
        { title: 'Sunset Moments', artist: 'Calm Waves', duration: '4:33' },
        { title: 'Peaceful Rain', artist: 'Nature Sounds', duration: '5:12' },
        { title: 'Moon Light', artist: 'Soft Echo', duration: '3:58' }
      ]
    },
    {
      id: 3,
      title: 'Party Hits 2026',
      description: 'Latest party bangers',
      tracks: 56,
      duration: '4h 12m',
      plays: 23450,
      followers: 892,
      songs: [
        { title: 'Drop It', artist: 'Bass Boosters', duration: '3:15' },
        { title: 'Dance Tonight', artist: 'Club Vibes', duration: '3:45' },
        { title: 'Here We Go', artist: 'Party Kings', duration: '3:22' }
      ]
    }
  ];

  useEffect(() => {
    fetchPlaylists();
    fetchRecommendations();
  }, []);

  const mockRecommendations = [
    {
      id: 1,
      title: 'Chill Vibes Playlist',
      type: 'Playlist',
      score: 92,
      reason: 'Based on your taste',
      feedback: null
    },
    {
      id: 2,
      title: 'Summer Hits 2026',
      type: 'Playlist',
      score: 88,
      reason: 'Trending now',
      feedback: null
    },
    {
      id: 3,
      title: 'Focus & Study',
      type: 'Playlist',
      score: 85,
      reason: 'Similar to your playlists',
      feedback: null
    },
    {
      id: 4,
      title: 'Deep House Sessions',
      type: 'Playlist',
      score: 81,
      reason: 'Popular in your genre',
      feedback: null
    }
  ];

  const fetchPlaylists = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/playlist/list`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setPlaylists(response.data.playlists || mockPlaylists);
    } catch (error) {
      console.error('Error fetching playlists:', error);
      setPlaylists(mockPlaylists);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/recommendation/playlists`,
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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreatePlaylist = async (e) => {
    e.preventDefault();

    if (!formData.title) {
      toast.error('Please enter playlist title');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/playlist/create`,
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
      toast.success('Playlist created!');
      fetchPlaylists();
    } catch (error) {
      console.error('Error creating playlist:', error);
      toast.error('Failed to create playlist');
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
    toast.success(liked ? 'Great! This helps us recommend better playlists' : 'Feedback recorded!');
  };

  if (loading) {
    return <Container><Title><Music /> Loading playlists...</Title></Container>;
  }

  return (
    <Container>
      <Header>
        <Title>
          <Music /> My Playlists
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> New Playlist
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create New Playlist</h2>
          <form onSubmit={handleCreatePlaylist}>
            <FormGroup>
              <Label>Playlist Title *</Label>
              <Input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., Workout Mix 2026"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Describe your playlist..."
              />
            </FormGroup>

            <SubmitButton type="submit">Create Playlist</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {playlists.map(playlist => (
          <Card key={playlist.id}>
            <CardTitle>
              <Music size={20} /> {playlist.title}
            </CardTitle>

            <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '15px' }}>
              {playlist.description}
            </div>

            <StatsGrid>
              <StatBox color="#E9D5FF">
                <div>Tracks</div>
                <div>{playlist.tracks}</div>
              </StatBox>
              <StatBox color="#E9D5FF">
                <div>Duration</div>
                <div>{playlist.duration}</div>
              </StatBox>
              <StatBox color="#DDD6FE">
                <div>Plays</div>
                <div>{(playlist.plays / 1000).toFixed(1)}K</div>
              </StatBox>
              <StatBox color="#DDD6FE">
                <div>Followers</div>
                <div>{playlist.followers}</div>
              </StatBox>
            </StatsGrid>

            <div style={{ marginTop: '15px' }}>
              <strong>Top Tracks:</strong>
              <TrackList>
                {playlist.songs.map((song, idx) => (
                  <Track key={idx}>
                    <TrackInfo>
                      <div>{song.title}</div>
                      <div>{song.artist}</div>
                    </TrackInfo>
                    <div style={{ fontSize: '0.85rem', color: '#999' }}>{song.duration}</div>
                  </Track>
                ))}
              </TrackList>
            </div>

            <ButtonGroup>
              <SmallButton>
                <Play size={16} /> Play
              </SmallButton>
              <SmallButton>
                <Edit size={16} /> Edit
              </SmallButton>
              <SmallButton>
                <Trash2 size={16} /> Delete
              </SmallButton>
            </ButtonGroup>
          </Card>
        ))}
      </GridContainer>

      <RecommendationSection>
        <RecommendationTitle>
          <Brain size={20} /> Recommended Playlists
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

export default PlaylistTab;
