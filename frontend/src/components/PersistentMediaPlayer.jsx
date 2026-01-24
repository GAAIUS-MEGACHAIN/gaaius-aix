import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8000';

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const PlayerContainer = styled.div`
  position: fixed;
  bottom: 0;
  right: 0;
  width: ${props => (props.minimized ? '320px' : '100%')};
  height: ${props => (props.minimized ? '100px' : '120px')};
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-top: 1px solid rgba(0, 255, 136, 0.3);
  z-index: 9998;
  display: flex;
  flex-direction: ${props => (props.minimized ? 'column' : 'row')};
  align-items: center;
  padding: 12px;
  box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  gap: 12px;

  @media (max-width: 768px) {
    width: ${props => (props.minimized ? '280px' : '100%')};
    height: ${props => (props.minimized ? '80px' : '100px')};
    padding: 8px;
  }
`;

const ThumbnailContainer = styled.div`
  min-width: 80px;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #0f3460;
  position: relative;
  cursor: pointer;
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &:hover::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 255, 136, 0.2);
  }

  @media (max-width: 768px) {
    min-width: 60px;
    width: 60px;
    height: 60px;
  }
`;

const PlayIcon = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: rgba(0, 255, 136, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  cursor: pointer;

  &::after {
    content: '';
    width: 0;
    height: 0;
    border-left: 12px solid white;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
    margin-left: 3px;
  }
`;

const ThumbnailContainer_Hover = styled(ThumbnailContainer)`
  &:hover {
    ${PlayIcon} {
      opacity: 1;
    }
  }
`;

const MediaInfo = styled.div`
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow: hidden;

  @media (max-width: 768px) {
    flex: 0.8;
    gap: 4px;
  }
`;

const MediaTitle = styled.h4`
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #00ff88;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;

  &:hover {
    color: #00ffaa;
  }

  @media (max-width: 768px) {
    font-size: 12px;
  }
`;

const MediaSubtitle = styled.p`
  margin: 0;
  font-size: 12px;
  color: #aaa;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  @media (max-width: 768px) {
    font-size: 10px;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: #0f3460;
  border-radius: 2px;
  overflow: hidden;
  cursor: pointer;
  transition: height 0.3s ease;

  &:hover {
    height: 6px;
  }
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #00ff88, #00ffaa);
  width: ${props => `${props.progress || 0}%`};
  transition: width 0.1s linear;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
`;

const ControlsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;

  @media (max-width: 768px) {
    gap: 6px;
  }
`;

const TimeDisplay = styled.span`
  font-size: 11px;
  color: #aaa;
  min-width: 45px;
  text-align: center;
  font-variant-numeric: tabular-nums;

  @media (max-width: 768px) {
    font-size: 9px;
    min-width: 40px;
  }
`;

const ControlButton = styled.button`
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #00ff88;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.3s ease;
  flex-shrink: 0;

  &:hover {
    background: rgba(0, 255, 136, 0.2);
    border-color: rgba(0, 255, 136, 0.5);
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (max-width: 768px) {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
`;

const VolumeControl = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 255, 136, 0.05);
  padding: 4px 8px;
  border-radius: 6px;
  min-width: 80px;

  @media (max-width: 768px) {
    min-width: 70px;
    gap: 4px;
  }
`;

const VolumeSlider = styled.input`
  width: 50px;
  height: 4px;
  border-radius: 2px;
  background: #0f3460;
  outline: none;
  -webkit-appearance: none;
  appearance: none;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #00ff88;
    cursor: pointer;
    box-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
  }

  &::-moz-range-thumb {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #00ff88;
    cursor: pointer;
    border: none;
    box-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
  }

  @media (max-width: 768px) {
    width: 40px;

    &::-webkit-slider-thumb {
      width: 10px;
      height: 10px;
    }

    &::-moz-range-thumb {
      width: 10px;
      height: 10px;
    }
  }
`;

const MinimizeButton = styled(ControlButton)`
  background: rgba(100, 200, 255, 0.1);
  border-color: rgba(100, 200, 255, 0.3);
  color: #64c8ff;

  &:hover {
    background: rgba(100, 200, 255, 0.2);
    border-color: rgba(100, 200, 255, 0.5);
  }
`;

const CloseButton = styled(ControlButton)`
  background: rgba(255, 100, 100, 0.1);
  border-color: rgba(255, 100, 100, 0.3);
  color: #ff6464;

  &:hover {
    background: rgba(255, 100, 100, 0.2);
    border-color: rgba(255, 100, 100, 0.5);
  }
`;

const HiddenAudio = styled.audio`
  display: none;
`;

const MinimizedHeader = styled.div`
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px;
  gap: 8px;
`;

const MinimizedTitle = styled.div`
  flex: 1;
  font-size: 11px;
  color: #00ff88;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 600;
`;

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const PersistentMediaPlayer = ({ userId, onMediaChange }) => {
  const audioRef = useRef(null);
  const [minimized, setMinimized] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentMedia, setCurrentMedia] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isVisible, setIsVisible] = useState(false);

  // Get current media from localStorage
  useEffect(() => {
    const savedMedia = localStorage.getItem('currentMedia');
    if (savedMedia) {
      try {
        const media = JSON.parse(savedMedia);
        setCurrentMedia(media);
        setIsVisible(true);
      } catch (error) {
        console.error('Error parsing saved media:', error);
      }
    }
  }, []);

  // Load audio source when media changes
  useEffect(() => {
    if (currentMedia && audioRef.current) {
      if (currentMedia.type === 'music' || currentMedia.type === 'podcast') {
        audioRef.current.src = currentMedia.url || '';
      }
    }
  }, [currentMedia]);

  // Handle play/pause
  const handlePlayPause = useCallback(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play().catch(err => console.error('Play error:', err));
        setIsPlaying(true);
      }
    }
  }, [isPlaying]);

  // Handle time update
  const handleTimeUpdate = useCallback(() => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);

      // Track playback in backend
      if (currentMedia && userId) {
        axios.post(
          `${BACKEND_URL}/api/media/tracking/update`,
          {
            media_id: currentMedia.id,
            user_id: userId,
            current_time: audioRef.current.currentTime,
            duration: audioRef.current.duration,
            content_type: currentMedia.type,
          },
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        ).catch(err => console.error('Tracking error:', err));
      }
    }
  }, [currentMedia, userId]);

  // Handle metadata loaded
  const handleMetadataLoaded = useCallback(() => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  }, []);

  // Handle ended
  const handleEnded = useCallback(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, []);

  // Handle progress bar click
  const handleProgressClick = useCallback((e) => {
    if (audioRef.current && duration) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = x / rect.width;
      const newTime = percentage * duration;
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  }, [duration]);

  // Handle volume change
  const handleVolumeChange = useCallback((e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  }, []);

  // Format time display
  const formatTime = (time) => {
    if (!time || isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Handle minimize
  const handleMinimize = () => {
    setMinimized(!minimized);
  };

  // Handle close
  const handleClose = () => {
    setIsVisible(false);
    setIsPlaying(false);
    localStorage.removeItem('currentMedia');
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
    }
  };

  // Handle thumbnail click to restore to full player
  const handleThumbnailClick = () => {
    if (onMediaChange) {
      onMediaChange(currentMedia);
    }
  };

  if (!isVisible || !currentMedia) {
    return null;
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <>
      <HiddenAudio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleMetadataLoaded}
        onEnded={handleEnded}
        volume={volume}
      />

      <PlayerContainer minimized={minimized}>
        {minimized ? (
          // Minimized View
          <MinimizedHeader>
            <MinimizedTitle>{currentMedia.title}</MinimizedTitle>
            <ControlButton onClick={handlePlayPause} title={isPlaying ? 'Pause' : 'Play'}>
              {isPlaying ? '⏸' : '▶'}
            </ControlButton>
            <MinimizeButton onClick={handleMinimize} title="Expand">
              ⬆
            </MinimizeButton>
            <CloseButton onClick={handleClose} title="Close">
              ✕
            </CloseButton>
          </MinimizedHeader>
        ) : (
          // Full View
          <>
            {/* Thumbnail */}
            <ThumbnailContainer_Hover onClick={handleThumbnailClick} title="Open player">
              <img
                src={currentMedia.thumbnail || 'https://via.placeholder.com/80'}
                alt={currentMedia.title}
              />
              <PlayIcon />
            </ThumbnailContainer_Hover>

            {/* Media Info */}
            <MediaInfo>
              <MediaTitle title={currentMedia.title}>{currentMedia.title}</MediaTitle>
              <MediaSubtitle title={currentMedia.artist || currentMedia.creator}>
                {currentMedia.artist || currentMedia.creator || 'Unknown'}
              </MediaSubtitle>
              <ProgressBar onClick={handleProgressClick}>
                <ProgressFill progress={progress} />
              </ProgressBar>
            </MediaInfo>

            {/* Controls */}
            <ControlsContainer>
              <TimeDisplay>
                {formatTime(currentTime)} / {formatTime(duration)}
              </TimeDisplay>

              <ControlButton onClick={handlePlayPause} title={isPlaying ? 'Pause' : 'Play'}>
                {isPlaying ? '⏸' : '▶'}
              </ControlButton>

              <VolumeControl>
                <span style={{ fontSize: '14px' }}>🔊</span>
                <VolumeSlider
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={volume}
                  onChange={handleVolumeChange}
                  title="Volume"
                />
              </VolumeControl>

              <MinimizeButton onClick={handleMinimize} title="Minimize">
                ⬇
              </MinimizeButton>

              <CloseButton onClick={handleClose} title="Close player">
                ✕
              </CloseButton>
            </ControlsContainer>
          </>
        )}
      </PlayerContainer>
    </>
  );
};

export default PersistentMediaPlayer;
