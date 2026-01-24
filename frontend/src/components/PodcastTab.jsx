import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Podcast, Play, Upload, Search, Download, Share, Disc3, Clock, Users, TrendingUp, Heart, Zap, Plus, X, Radio, Rss } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
`;

const Section = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
`;

const Title = styled.h2`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  color: #667eea;
`;

const Tabs = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
`;

const Tab = styled.button`
  padding: 12px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: ${props => props.active ? '#667eea' : '#999'};
  border-bottom: 3px solid ${props => props.active ? '#667eea' : 'transparent'};
  transition: all 0.3s;
  
  &:hover {
    color: #667eea;
  }
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
`;

const Input = styled.input`
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const PodcastGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
`;

const PodcastCard = styled.div`
  background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  border: 1px solid #e0e0e0;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    border-color: #667eea;
  }
`;

const PodcastImage = styled.div`
  width: 100%;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
`;

const PodcastInfo = styled.div`
  padding: 16px;
`;

const PodcastTitle = styled.h3`
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 700;
  color: #333;
`;

const PodcastAuthor = styled.p`
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #666;
`;

const PodcastStats = styled.div`
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
`;

const Stat = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ff9800;
  font-weight: 600;
  margin-bottom: 12px;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: #f0f0f0;
  color: #333;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  
  &:hover {
    background: #667eea;
    color: white;
  }
`;

const EpisodeCard = styled.div`
  background: #f9f9f9;
  border-left: 4px solid #667eea;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.3s;
  
  &:hover {
    background: #f0f0f0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const EpisodeTitle = styled.h4`
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
`;

const EpisodeMeta = styled.div`
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
`;

const EpisodeDescription = styled.p`
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
`;

const EpisodeActions = styled.div`
  display: flex;
  gap: 8px;
`;

const EpisodeButton = styled.button`
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  background: white;
  border: 1px solid #ddd;
  color: #333;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
`;

const UploadForm = styled.div`
  background: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
`;

const FormGroup = styled.div`
  margin-bottom: 12px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #333;
`;

const FormInput = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  box-sizing: border-box;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const FormTextarea = styled.textarea`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const FileInput = styled.input`
  display: none;
`;

const FileButtonWrapper = styled.label`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 2px dashed #667eea;
  border-radius: 6px;
  background: rgba(102, 126, 234, 0.05);
  color: #667eea;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
  }
`;

const RSSInput = styled.div`
  display: flex;
  gap: 8px;
`;

const NewBadge = styled.span`
  display: inline-block;
  background: #ff4757;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  margin-left: 8px;
`;

const PodcastTab = () => {
  const [tab, setTab] = useState('browse');
  const [podcasts, setPodcasts] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [episodes, setEpisodes] = useState([]);
  const [selectedPodcast, setSelectedPodcast] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [showRSSForm, setShowRSSForm] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    title: '',
    description: '',
    file: null
  });
  const [rssUrl, setRssUrl] = useState('');

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api';
  const token = localStorage.getItem('gaaius_token');

  useEffect(() => {
    loadPodcasts();
    loadSubscriptions();
  }, []);

  const loadPodcasts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/v1/podcasts/list`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPodcasts(response.data.podcasts || []);
    } catch (error) {
      toast.error('Failed to load podcasts');
    } finally {
      setLoading(false);
    }
  };

  const loadSubscriptions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/v1/podcasts/subscriptions/list`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSubscriptions(response.data.subscriptions || []);
    } catch (error) {
      toast.error('Failed to load subscriptions');
    }
  };

  const loadEpisodes = async (podcastId) => {
    try {
      const response = await axios.get(`${API_BASE}/v1/podcasts/${podcastId}/episodes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEpisodes(response.data.episodes || []);
    } catch (error) {
      toast.error('Failed to load episodes');
    }
  };

  const handleSubscribe = async (podcastId) => {
    try {
      await axios.post(`${API_BASE}/v1/podcasts/${podcastId}/subscribe`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Subscribed to podcast');
      loadSubscriptions();
    } catch (error) {
      toast.error('Failed to subscribe');
    }
  };

  const handleUploadEpisode = async () => {
    if (!uploadForm.title || !uploadForm.file) {
      toast.error('Please fill all fields');
      return;
    }
    try {
      await axios.post(`${API_BASE}/v1/podcasts/episodes/upload`, {
        podcast_id: selectedPodcast.id,
        title: uploadForm.title,
        description: uploadForm.description,
        file: uploadForm.file.name
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Episode uploaded successfully');
      setUploadForm({ title: '', description: '', file: null });
      setShowUploadForm(false);
      loadEpisodes(selectedPodcast.id);
    } catch (error) {
      toast.error('Failed to upload episode');
    }
  };

  const handleImportRSS = async () => {
    if (!rssUrl) {
      toast.error('Please enter an RSS feed URL');
      return;
    }
    try {
      await axios.post(`${API_BASE}/v1/podcasts/rss/import`, {
        feed_url: rssUrl
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('RSS feed imported successfully');
      setRssUrl('');
      setShowRSSForm(false);
    } catch (error) {
      toast.error('Failed to import RSS feed');
    }
  };

  const playEpisode = (episode) => {
    toast.success(`Playing: ${episode.title}`);
  };

  const likeEpisode = async (episodeId) => {
    try {
      await axios.post(`${API_BASE}/v1/podcasts/episodes/${episodeId}/like`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Episode liked');
    } catch (error) {
      toast.error('Failed to like episode');
    }
  };

  const downloadEpisode = (episode) => {
    toast.success(`Downloading: ${episode.title}`);
  };

  return (
    <Container>
      <Section>
        <Header>
          <Title>
            <Podcast size={32} />
            Podcast Platform
          </Title>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button onClick={() => setShowRSSForm(!showRSSForm)}>
              <Rss size={16} />
              {showRSSForm ? 'Cancel' : 'Import RSS'}
            </Button>
            <Button onClick={() => setShowUploadForm(!showUploadForm)}>
              <Upload size={16} />
              {showUploadForm ? 'Cancel' : 'Upload Episode'}
            </Button>
          </div>
        </Header>

        <Tabs>
          <Tab active={tab === 'browse'} onClick={() => setTab('browse')}>
            <TrendingUp size={16} style={{ display: 'inline' }} /> Browse
          </Tab>
          <Tab active={tab === 'subscriptions'} onClick={() => { setTab('subscriptions'); loadSubscriptions(); }}>
            <Heart size={16} style={{ display: 'inline' }} /> My Subscriptions
          </Tab>
          <Tab active={tab === 'listening'} onClick={() => setTab('listening')}>
            <Radio size={16} style={{ display: 'inline' }} /> Listening History
          </Tab>
        </Tabs>

        {showRSSForm && (
          <UploadForm>
            <h4 style={{ margin: '0 0 12px 0', color: '#333' }}>Import RSS Feed</h4>
            <RSSInput>
              <FormInput 
                placeholder="https://example.com/feed.xml"
                value={rssUrl}
                onChange={(e) => setRssUrl(e.target.value)}
              />
              <Button onClick={handleImportRSS}>Import</Button>
            </RSSInput>
          </UploadForm>
        )}

        {showUploadForm && (
          <UploadForm>
            <h4 style={{ margin: '0 0 12px 0', color: '#333' }}>Upload New Episode</h4>
            <FormGroup>
              <Label>Episode Title</Label>
              <FormInput 
                placeholder="Enter episode title"
                value={uploadForm.title}
                onChange={(e) => setUploadForm({...uploadForm, title: e.target.value})}
              />
            </FormGroup>
            <FormGroup>
              <Label>Description</Label>
              <FormTextarea 
                placeholder="Episode description"
                value={uploadForm.description}
                onChange={(e) => setUploadForm({...uploadForm, description: e.target.value})}
              />
            </FormGroup>
            <FormGroup>
              <Label>Audio File</Label>
              <FileButtonWrapper htmlFor="file-input">
                <Upload size={14} />
                {uploadForm.file ? uploadForm.file.name : 'Choose file'}
              </FileButtonWrapper>
              <FileInput 
                id="file-input"
                type="file"
                accept="audio/*"
                onChange={(e) => setUploadForm({...uploadForm, file: e.target.files[0]})}
              />
            </FormGroup>
            <Button onClick={handleUploadEpisode}>Upload Episode</Button>
          </UploadForm>
        )}

        {tab === 'browse' && (
          <>
            <SearchBar>
              <Input 
                placeholder="Search podcasts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Button><Search size={16} /></Button>
            </SearchBar>

            <PodcastGrid>
              {podcasts.map(podcast => (
                <PodcastCard key={podcast.id}>
                  <PodcastImage></PodcastImage>
                  <PodcastInfo>
                    <PodcastTitle>
                      {podcast.title}
                      {podcast.new_episodes > 0 && <NewBadge>{podcast.new_episodes} NEW</NewBadge>}
                    </PodcastTitle>
                    <PodcastAuthor>{podcast.author}</PodcastAuthor>
                    <Rating>
                       {podcast.rating} ({podcast.episodes_count} episodes)
                    </Rating>
                    <PodcastStats>
                      <Stat><Users size={12} /> {(podcast.subscribers / 1000).toFixed(0)}K</Stat>
                      <Stat><Disc3 size={12} /> {podcast.category}</Stat>
                    </PodcastStats>
                    <CardActions>
                      <ActionButton onClick={() => { setSelectedPodcast(podcast); loadEpisodes(podcast.id); setTab('episodes'); }}>
                        <Play size={14} /> Play
                      </ActionButton>
                      <ActionButton onClick={() => handleSubscribe(podcast.id)}>
                        <Heart size={14} /> Subscribe
                      </ActionButton>
                    </CardActions>
                  </PodcastInfo>
                </PodcastCard>
              ))}
            </PodcastGrid>
          </>
        )}

        {tab === 'subscriptions' && (
          <>
            <div style={{ marginBottom: '16px', color: '#667eea', fontWeight: 600 }}>
              {subscriptions.length} subscriptions
            </div>
            <PodcastGrid>
              {subscriptions.map(sub => (
                <PodcastCard key={sub.id}>
                  <PodcastImage></PodcastImage>
                  <PodcastInfo>
                    <PodcastTitle>{sub.title}</PodcastTitle>
                    <PodcastAuthor>{sub.author}</PodcastAuthor>
                    <Rating> {sub.rating}</Rating>
                    <PodcastStats>
                      <Stat>Unread: {sub.unread_episodes}</Stat>
                      <Stat>Last: {sub.last_listened}</Stat>
                    </PodcastStats>
                    <CardActions>
                      <ActionButton onClick={() => { setSelectedPodcast(sub); loadEpisodes(sub.id); }}>
                        <Play size={14} /> Listen
                      </ActionButton>
                    </CardActions>
                  </PodcastInfo>
                </PodcastCard>
              ))}
            </PodcastGrid>
          </>
        )}

        {tab === 'listening' && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            <Radio size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
            <p>Your listening history will appear here</p>
          </div>
        )}

        {tab === 'episodes' && selectedPodcast && (
          <>
            <div style={{ marginBottom: '16px' }}>
              <button onClick={() => { setTab('browse'); setSelectedPodcast(null); }} style={{ background: 'none', border: 'none', color: '#667eea', cursor: 'pointer', fontSize: '14px', fontWeight: 600 }}>
                 Back to Browse
              </button>
              <h3 style={{ margin: '8px 0 0 0', color: '#333', fontSize: '20px' }}>{selectedPodcast.title}</h3>
            </div>
            {episodes.map(ep => (
              <EpisodeCard key={ep.id}>
                <EpisodeTitle>{ep.title}</EpisodeTitle>
                <EpisodeMeta>
                  <span>{ep.published_ago}</span>
                  <span><Clock size={12} style={{ display: 'inline' }} /> {ep.duration_formatted}</span>
                  <span> {ep.rating}</span>
                </EpisodeMeta>
                <EpisodeDescription>{ep.description}</EpisodeDescription>
                <EpisodeActions>
                  <EpisodeButton onClick={() => playEpisode(ep)}>
                    <Play size={12} /> Play
                  </EpisodeButton>
                  <EpisodeButton onClick={() => likeEpisode(ep.id)}>
                    <Heart size={12} /> Like
                  </EpisodeButton>
                  <EpisodeButton onClick={() => downloadEpisode(ep)}>
                    <Download size={12} /> Download
                  </EpisodeButton>
                  <EpisodeButton onClick={() => toast.success('Shared')}>
                    <Share size={12} /> Share
                  </EpisodeButton>
                </EpisodeActions>
              </EpisodeCard>
            ))}
          </>
        )}
      </Section>
    </Container>
  );
};

export default PodcastTab;
