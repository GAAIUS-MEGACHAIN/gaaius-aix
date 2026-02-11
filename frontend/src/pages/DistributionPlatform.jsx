/**
 * DISTRIBUTION PLATFORM - FRONTEND COMPONENT
 * React component for music/video distribution platform
 * Integrated with Menu and Dashboard
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import styled from 'styled-components';

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const DistributionContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  min-height: 100vh;
`;

const TabsContainer = styled.div`
  display: flex;
  gap: 1rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 2rem;
  overflow-x: auto;
`;

const Tab = styled.button`
  padding: 1rem 2rem;
  background: ${props => props.active ? '#00d4ff' : 'transparent'};
  color: ${props => props.active ? '#1e3c72' : '#fff'};
  border: none;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.active ? '#00d4ff' : 'rgba(255, 255, 255, 0.1)'};
  }
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  background: ${props => props.danger ? '#ff4757' : '#00d4ff'};
  color: ${props => props.danger ? '#fff' : '#1e3c72'};
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: #1e3c72;
  }
  
  input, textarea, select {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    
    &:focus {
      outline: none;
      border-color: #00d4ff;
    }
  }
`;

const FileInput = styled.input`
  padding: 0.75rem;
`;

const UploadArea = styled.div`
  border: 3px dashed #00d4ff;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(0, 212, 255, 0.05);
  }
  
  &.active {
    background: rgba(0, 212, 255, 0.1);
    border-color: #00a8cc;
  }
`;

const ProjectGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
`;

const ProjectCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  
  h3 {
    margin: 0 0 0.5rem 0;
    color: #1e3c72;
  }
  
  .artist {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }
  
  .status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: bold;
    margin: 0.5rem 0;
    
    &.draft {
      background: #ffeaa7;
      color: #d63031;
    }
    
    &.pending {
      background: #dfe6e9;
      color: #636e72;
    }
    
    &.approved {
      background: #74b9ff;
      color: #0984e3;
    }
    
    &.distributed {
      background: #55efc4;
      color: #00b894;
    }
    
    &.rejected {
      background: #fab1a0;
      color: #d63031;
    }
  }
`;

const PlatformList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
`;

const PlatformBadge = styled.span`
  background: #e0e0e0;
  color: #1e3c72;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: bold;
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  
  .value {
    font-size: 2rem;
    font-weight: bold;
    margin: 0.5rem 0;
  }
  
  .label {
    font-size: 0.9rem;
    opacity: 0.9;
  }
`;

const DistributionUrls = styled.div`
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
  
  h4 {
    margin-top: 0;
    color: #1e3c72;
  }
  
  a {
    display: block;
    color: #00d4ff;
    text-decoration: none;
    word-break: break-all;
    margin: 0.5rem 0;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const Alert = styled.div`
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  background: ${props => {
    if (props.type === 'success') return '#c8e6c9';
    if (props.type === 'error') return '#ffcdd2';
    if (props.type === 'warning') return '#fff9c4';
    return '#e3f2fd';
  }};
  color: ${props => {
    if (props.type === 'success') return '#1b5e20';
    if (props.type === 'error') return '#b71c1c';
    if (props.type === 'warning') return '#f57f17';
    return '#01579b';
  }};
`;

// ============================================================================
// DISTRIBUTION PLATFORM COMPONENT
// ============================================================================

const DistributionPlatform = ({ userId }) => {
  // State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [artistProfile, setArtistProfile] = useState(null);
  const [royalties, setRoyalties] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  
  // Form state
  const [uploadForm, setUploadForm] = useState({
    title: '',
    description: '',
    artist_name: '',
    content_type: 'music',
    platforms: [],
    metadata: {}
  });
  
  const [selectedFiles, setSelectedFiles] = useState({
    audio: null,
    video: null,
    cover: null
  });

  // Initialize
  useEffect(() => {
    initializeArtist();
  }, [userId]);

  // Fetch data based on active tab
  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchArtistProfile();
      fetchProjects();
      fetchRoyalties();
    }
  }, [activeTab]);

  // Initialize artist profile
  const initializeArtist = async () => {
    try {
      const response = await axios.get(
        `/api/v1/distribution/artist/profile/${userId}`
      );
      setArtistProfile(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        // Create new profile
        createArtistProfile();
      }
    }
  };

  // Create artist profile
  const createArtistProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/v1/distribution/artist/profile', {
        user_id: userId,
        email: `${userId}@example.com`,
        name: 'Artist'
      });
      setArtistProfile(response.data);
      showAlert('Artist profile created successfully!', 'success');
    } catch (error) {
      showAlert(error.response?.data?.detail || 'Error creating profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Fetch artist profile
  const fetchArtistProfile = async () => {
    try {
      const response = await axios.get(
        `/api/v1/distribution/artist/profile/${userId}`
      );
      setArtistProfile(response.data);
    } catch (error) {
      console.error('Error fetching artist profile:', error);
    }
  };

  // Fetch projects
  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `/api/v1/distribution/project/list/${userId}`
      );
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch royalties
  const fetchRoyalties = async () => {
    try {
      const response = await axios.get(
        `/api/v1/distribution/royalties/${userId}`
      );
      setRoyalties(response.data);
    } catch (error) {
      console.error('Error fetching royalties:', error);
    }
  };

  // Handle file selection
  const handleFileSelect = (fileType) => (e) => {
    setSelectedFiles({
      ...selectedFiles,
      [fileType]: e.target.files[0]
    });
  };

  // Handle form input
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setUploadForm({
      ...uploadForm,
      [name]: value
    });
  };

  // Handle platform selection
  const handlePlatformToggle = (platform) => {
    const updated = uploadForm.platforms.includes(platform)
      ? uploadForm.platforms.filter(p => p !== platform)
      : [...uploadForm.platforms, platform];
    setUploadForm({
      ...uploadForm,
      platforms: updated
    });
  };

  // Upload project
  const handleUploadProject = async (e) => {
    e.preventDefault();
    
    if (!uploadForm.title || uploadForm.platforms.length === 0) {
      showAlert('Please fill all required fields', 'error');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      
      // Add form fields
      formData.append('user_id', userId);
      formData.append('title', uploadForm.title);
      formData.append('description', uploadForm.description);
      formData.append('artist_name', uploadForm.artist_name);
      formData.append('content_type', uploadForm.content_type);
      formData.append('platforms', JSON.stringify(uploadForm.platforms));
      formData.append('metadata', JSON.stringify(uploadForm.metadata));
      
      // Add files
      if (selectedFiles.audio) formData.append('audio_file', selectedFiles.audio);
      if (selectedFiles.video) formData.append('video_file', selectedFiles.video);
      if (selectedFiles.cover) formData.append('cover_art', selectedFiles.cover);
      
      const response = await axios.post(
        '/api/v1/distribution/project/upload',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      showAlert(response.data.message, 'success');
      
      // Reset form
      setUploadForm({
        title: '',
        description: '',
        artist_name: '',
        content_type: 'music',
        platforms: [],
        metadata: {}
      });
      setSelectedFiles({ audio: null, video: null, cover: null });
      
      // Refresh projects
      await fetchProjects();
    } catch (error) {
      showAlert(error.response?.data?.detail || 'Upload failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Request payout
  const handleRequestPayout = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/v1/distribution/payout/request', {
        user_id: userId,
        stripe_account_id: 'acct_xxxxx'  // Would be from user's Stripe connection
      });
      showAlert(response.data.message, 'success');
      await fetchRoyalties();
    } catch (error) {
      showAlert(error.response?.data?.detail || 'Payout request failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Upgrade to pro
  const handleUpgradePro = async () => {
    try {
      setLoading(true);
      // In real app, would handle Stripe payment
      const response = await axios.post('/api/v1/distribution/artist/upgrade-pro', {
        user_id: userId,
        stripe_token: 'tok_xxxxx'  // Would be from Stripe
      });
      showAlert(response.data.message, 'success');
      await fetchArtistProfile();
    } catch (error) {
      showAlert(error.response?.data?.detail || 'Upgrade failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Show alert
  const showAlert = (message, type = 'info') => {
    setAlert({ message, type });
    setTimeout(() => setAlert(null), 5000);
  };

  // ========================================================================
  // RENDER SECTIONS
  // ========================================================================

  const renderDashboard = () => (
    <>
      <h2>📊 Distribution Dashboard</h2>
      
      {artistProfile && (
        <>
          <StatGrid>
            <StatCard>
              <div className="label">Total Projects</div>
              <div className="value">{artistProfile.total_projects}</div>
            </StatCard>
            <StatCard>
              <div className="label">Total Revenue</div>
              <div className="value">${artistProfile.total_revenue}</div>
            </StatCard>
            <StatCard>
              <div className="label">This Month</div>
              <div className="value">{artistProfile.projects_this_month}</div>
            </StatCard>
            <StatCard>
              <div className="label">Account Type</div>
              <div className="value">{artistProfile.is_pro ? '⭐ PRO' : 'FREE'}</div>
            </StatCard>
          </StatGrid>

          {!artistProfile.is_pro && (
            <Card>
              <h3>Upgrade to Pro - Unlimited Distributions, 0% Commission</h3>
              <p>Pro members keep 100% of earnings and can upload unlimited content.</p>
              <Button onClick={handleUpgradePro} disabled={loading}>
                🚀 Upgrade to Pro ($9.99/month)
              </Button>
            </Card>
          )}
        </>
      )}

      {royalties && (
        <Card>
          <h3>💰 Royalties & Earnings</h3>
          <p>Total Earned: <strong>${royalties.total_net_earned}</strong></p>
          <p>Pending Payout: <strong>${royalties.pending_payments}</strong></p>
          {royalties.pending_payments > 0 && (
            <Button onClick={handleRequestPayout} disabled={loading}>
              Request Payout
            </Button>
          )}
        </Card>
      )}
    </>
  );

  const renderUpload = () => (
    <>
      <h2>📤 Upload for Distribution</h2>
      
      <Card>
        <form onSubmit={handleUploadProject}>
          <FormGroup>
            <label>Content Title *</label>
            <input
              type="text"
              name="title"
              value={uploadForm.title}
              onChange={handleFormChange}
              placeholder="Song title, album, movie title..."
              required
            />
          </FormGroup>

          <FormGroup>
            <label>Description</label>
            <textarea
              name="description"
              value={uploadForm.description}
              onChange={handleFormChange}
              placeholder="Describe your content..."
              rows="3"
            />
          </FormGroup>

          <FormGroup>
            <label>Artist / Creator Name</label>
            <input
              type="text"
              name="artist_name"
              value={uploadForm.artist_name}
              onChange={handleFormChange}
              placeholder="Your name or band name"
            />
          </FormGroup>

          <FormGroup>
            <label>Content Type *</label>
            <select 
              name="content_type"
              value={uploadForm.content_type}
              onChange={handleFormChange}
            >
              <option value="music">🎵 Music</option>
              <option value="music_video">🎬 Music Video</option>
              <option value="movie">🎥 Movie</option>
              <option value="documentary">📽️ Documentary</option>
            </select>
          </FormGroup>

          <FormGroup>
            <label>Audio File (MP3, WAV, FLAC, ALAC)</label>
            <FileInput
              type="file"
              accept="audio/*"
              onChange={handleFileSelect('audio')}
            />
            {selectedFiles.audio && <p>✓ {selectedFiles.audio.name}</p>}
          </FormGroup>

          <FormGroup>
            <label>Video File (MP4, WebM) - Optional</label>
            <FileInput
              type="file"
              accept="video/*"
              onChange={handleFileSelect('video')}
            />
            {selectedFiles.video && <p>✓ {selectedFiles.video.name}</p>}
          </FormGroup>

          <FormGroup>
            <label>Cover Art (JPG, PNG)</label>
            <FileInput
              type="file"
              accept="image/*"
              onChange={handleFileSelect('cover')}
            />
            {selectedFiles.cover && <p>✓ {selectedFiles.cover.name}</p>}
          </FormGroup>

          <FormGroup>
            <label>Distribute To *</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
              {[
                { id: 'spotify', name: '🎵 Spotify' },
                { id: 'apple_music', name: '🍎 Apple Music' },
                { id: 'youtube_music', name: '🎬 YouTube Music' },
                { id: 'soundcloud', name: '☁️ SoundCloud' },
                { id: 'tidal', name: '🎧 Tidal' },
                { id: 'amazon_music', name: '📦 Amazon Music' }
              ].map(platform => (
                <label key={platform.id} style={{ display: 'flex', alignItems: 'center' }}>
                  <input
                    type="checkbox"
                    checked={uploadForm.platforms.includes(platform.id)}
                    onChange={() => handlePlatformToggle(platform.id)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  {platform.name}
                </label>
              ))}
            </div>
          </FormGroup>

          <Button type="submit" disabled={loading}>
            {loading ? '⏳ Uploading...' : '🚀 Upload & Distribute'}
          </Button>
        </form>
      </Card>
    </>
  );

  const renderProjects = () => (
    <>
      <h2>📚 My Distributions</h2>
      
      {projects.length === 0 ? (
        <Card>
          <p>No distributions yet. <strong>Upload your first content!</strong></p>
        </Card>
      ) : (
        <ProjectGrid>
          {projects.map(project => (
            <ProjectCard key={project.id}>
              <h3>{project.title}</h3>
              <div className="artist">{project.content_type.toUpperCase()}</div>
              <span className={`status ${project.status.toLowerCase()}`}>
                {project.status.replace('_', ' ').toUpperCase()}
              </span>
              {project.distributed && (
                <PlatformList>
                  {Array(project.platforms).fill(0).map((_, i) => (
                    <PlatformBadge key={i}>📱 Platform</PlatformBadge>
                  ))}
                </PlatformList>
              )}
              <div style={{ fontSize: '0.9rem', marginTop: '1rem', color: '#666' }}>
                <p>Created: {new Date(project.created).toLocaleDateString()}</p>
              </div>
            </ProjectCard>
          ))}
        </ProjectGrid>
      )}
    </>
  );

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <DistributionContainer>
      <TabsContainer>
        <Tab
          active={activeTab === 'dashboard'}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </Tab>
        <Tab
          active={activeTab === 'upload'}
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload
        </Tab>
        <Tab
          active={activeTab === 'projects'}
          onClick={() => setActiveTab('projects')}
        >
          📚 My Distributions
        </Tab>
      </TabsContainer>

      {alert && (
        <Alert type={alert.type}>
          {alert.message}
        </Alert>
      )}

      {loading && (
        <div style={{ textAlign: 'center', color: 'white', padding: '2rem' }}>
          <p>⏳ Loading...</p>
        </div>
      )}

      {activeTab === 'dashboard' && renderDashboard()}
      {activeTab === 'upload' && renderUpload()}
      {activeTab === 'projects' && renderProjects()}
    </DistributionContainer>
  );
};

export default DistributionPlatform;
