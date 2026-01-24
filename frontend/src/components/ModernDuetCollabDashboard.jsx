import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Play, Pause, Video, Users, Plus, Edit, Trash2, Share2,
  Download, Eye, Heart, Filter, Search, Sparkles, Zap,
  MessageCircle, Calendar, Clock, TrendingUp
} from 'lucide-react';

// ============================================================================
// MODERN DUET & COLLAB DASHBOARD STYLES
// ============================================================================

const DashboardContainer = styled.div`
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  min-height: 100vh;
  padding: 40px;
  font-family: 'Manrope', sans-serif;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
  }
`;

const SecondaryButton = styled(Button)`
  background: rgba(148, 163, 184, 0.1);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.2);
`;

// ============================================================================
// TABS
// ============================================================================

const TabsContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
`;

const Tab = styled.button`
  background: transparent;
  border: none;
  color: ${props => props.active ? '#6366f1' : 'rgba(226, 232, 240, 0.6)'};
  padding: 12px 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  border-bottom: 2px solid ${props => props.active ? '#6366f1' : 'transparent'};
  
  &:hover {
    color: #e2e8f0;
  }
`;

// ============================================================================
// SESSION CARDS
// ============================================================================

const SessionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const SessionCard = styled.div`
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 14px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  
  &:hover {
    transform: translateY(-8px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 20px 50px rgba(99, 102, 241, 0.15);
  }
`;

const SessionPreview = styled.div`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  svg {
    width: 60px;
    height: 60px;
    opacity: 0.5;
  }
`;

const PlayButton = styled.button`
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
  }
`;

const SessionStatus = styled.span`
  position: absolute;
  top: 12px;
  right: 12px;
  background: ${props => props.live ? 'rgba(239, 68, 68, 0.9)' : 'rgba(99, 102, 241, 0.9)'};
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: white;
    ${props => props.live && `
      animation: pulse 2s infinite;
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
    `}
  }
`;

const SessionInfo = styled.div`
  padding: 20px;
`;

const SessionTitle = styled.h3`
  font-size: 16px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 8px;
`;

const SessionStats = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
`;

const StatBadge = styled.span`
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: rgba(226, 232, 240, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const Collaborators = styled.div`
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
`;

const Avatar = styled.div`
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  font-size: 11px;
`;

const SessionActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

const IconButton = styled.button`
  flex: 1;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: #e2e8f0;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  
  &:hover {
    background: rgba(99, 102, 241, 0.2);
    border-color: #6366f1;
    color: #6366f1;
  }
`;

// ============================================================================
// EFFECTS SHOWCASE
// ============================================================================

const EffectsContainer = styled.div`
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  padding: 30px;
  margin-bottom: 40px;
`;

const EffectsTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 12px;
  
  svg {
    color: #6366f1;
  }
`;

const EffectsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
`;

const EffectCard = styled.div`
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    border-color: #6366f1;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
  }
  
  .icon {
    font-size: 32px;
    margin-bottom: 8px;
  }
  
  .name {
    font-size: 12px;
    font-weight: 600;
    color: rgba(226, 232, 240, 0.8);
  }
`;

// ============================================================================
// DUET & COLLAB DASHBOARD COMPONENT
// ============================================================================

const DuetCollabDashboard = () => {
  const [activeTab, setActiveTab] = useState('sessions');

  const mockSessions = [
    {
      id: 1,
      title: 'Summer Vibes Collab',
      duration: '45 min',
      views: 2340,
      collaborators: ['JD', 'JS', 'MJ'],
      status: 'completed',
      date: '2024-01-20'
    },
    {
      id: 2,
      title: 'Live Duet Session',
      duration: '30 min',
      views: 5600,
      collaborators: ['JD', 'AM', 'SL'],
      status: 'live',
      date: '2024-01-20'
    },
    {
      id: 3,
      title: 'Trending Mashup',
      duration: '25 min',
      views: 8900,
      collaborators: ['JD', 'JS'],
      status: 'completed',
      date: '2024-01-19'
    },
    {
      id: 4,
      title: 'Behind the Scenes',
      duration: '15 min',
      views: 1240,
      collaborators: ['JD', 'MJ', 'AM', 'SL'],
      status: 'completed',
      date: '2024-01-18'
    },
    {
      id: 5,
      title: 'Music Production Collab',
      duration: '60 min',
      views: 3400,
      collaborators: ['JD', 'JS', 'MJ'],
      status: 'scheduled',
      date: '2024-01-22'
    },
    {
      id: 6,
      title: 'Comedy Skit',
      duration: '20 min',
      views: 6700,
      collaborators: ['JD', 'TW'],
      status: 'completed',
      date: '2024-01-17'
    },
  ];

  const effects = [
    { icon: '✨', name: 'Sparkle' },
    { icon: '🌈', name: 'Rainbow' },
    { icon: '🎬', name: 'Cinema' },
    { icon: '🎨', name: 'Paint' },
    { icon: '💫', name: 'Glow' },
    { icon: '🎭', name: 'Drama' },
    { icon: '❄️', name: 'Frost' },
    { icon: '🔥', name: 'Fire' },
    { icon: '🌊', name: 'Wave' },
    { icon: '🎪', name: 'Vintage' },
    { icon: '🚀', name: 'Retro' },
    { icon: '⚡', name: 'Energy' },
  ];

  return (
    <DashboardContainer>
      {/* HEADER */}
      <Header>
        <Title>
          <Video size={32} />
          Duet & Collab Studio
        </Title>
        <ActionButtons>
          <SecondaryButton>
            <Download size={18} />
            Export
          </SecondaryButton>
          <Button>
            <Plus size={18} />
            New Session
          </Button>
        </ActionButtons>
      </Header>

      {/* TABS */}
      <TabsContainer>
        <Tab active={activeTab === 'sessions'} onClick={() => setActiveTab('sessions')}>
          Sessions
        </Tab>
        <Tab active={activeTab === 'effects'} onClick={() => setActiveTab('effects')}>
          Effects
        </Tab>
        <Tab active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')}>
          Analytics
        </Tab>
      </TabsContainer>

      {/* SESSIONS TAB */}
      {activeTab === 'sessions' && (
        <SessionsGrid>
          {mockSessions.map((session) => (
            <SessionCard key={session.id}>
              <SessionPreview>
                <Video size={60} />
                <SessionStatus live={session.status === 'live'}>
                  {session.status === 'live' ? '🔴 Live' : 'Completed'}
                </SessionStatus>
                {session.status === 'live' && (
                  <PlayButton>
                    <Play size={24} fill="white" />
                  </PlayButton>
                )}
              </SessionPreview>
              <SessionInfo>
                <SessionTitle>{session.title}</SessionTitle>
                <SessionStats>
                  <StatBadge>⏱️ {session.duration}</StatBadge>
                  <StatBadge>👁️ {session.views.toLocaleString()}</StatBadge>
                </SessionStats>
                <Collaborators>
                  {session.collaborators.map((collab, idx) => (
                    <Avatar key={idx} title={collab}>{collab}</Avatar>
                  ))}
                </Collaborators>
                <SessionActions>
                  <IconButton title="View">
                    <Eye size={14} />
                    View
                  </IconButton>
                  <IconButton title="Edit">
                    <Edit size={14} />
                    Edit
                  </IconButton>
                  <IconButton title="Share">
                    <Share2 size={14} />
                    Share
                  </IconButton>
                </SessionActions>
              </SessionInfo>
            </SessionCard>
          ))}
        </SessionsGrid>
      )}

      {/* EFFECTS TAB */}
      {activeTab === 'effects' && (
        <EffectsContainer>
          <EffectsTitle>
            <Sparkles size={20} />
            Professional Effects (12 Available)
          </EffectsTitle>
          <EffectsGrid>
            {effects.map((effect, idx) => (
              <EffectCard key={idx}>
                <div className="icon">{effect.icon}</div>
                <div className="name">{effect.name}</div>
              </EffectCard>
            ))}
          </EffectsGrid>
        </EffectsContainer>
      )}

      {/* ANALYTICS TAB */}
      {activeTab === 'analytics' && (
        <div style={{ 
          background: 'linear-gradient(135deg, rgba(148, 163, 184, 0.05) 0%, rgba(15, 23, 42, 0.5) 100%)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          borderRadius: '14px',
          padding: '40px',
          textAlign: 'center'
        }}>
          <h3 style={{ fontSize: '20px', marginBottom: '20px', color: '#e2e8f0' }}>
            📊 Collaboration Analytics
          </h3>
          <p style={{ color: 'rgba(226, 232, 240, 0.6)' }}>
            Detailed session performance, collaborator insights, and engagement metrics
          </p>
        </div>
      )}
    </DashboardContainer>
  );
};

export default DuetCollabDashboard;
