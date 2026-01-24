import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  X,
  Maximize2,
  Minimize2,
  SkipBack,
  SkipForward,
  Settings,
} from 'lucide-react';
import { useMedia } from '@/contexts/MediaContext';

const FloatingPlayerContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
`;

const PlayerWrapper = styled.div`
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  transition: all 0.3s ease;
  user-select: none;

  &:hover {
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
  }
`;

const MinimizedPlayer = styled(PlayerWrapper)`
  width: 300px;
  cursor: grab;
  &:active {
    cursor: grabbing;
  }
`;

const MaximizedPlayer = styled(PlayerWrapper)`
  width: 420px;
`;

const PlayerThumbnail = styled.div`
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 aspect ratio */
  background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
  overflow: hidden;

  img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const PlayingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;

  ${PlayerThumbnail}:hover & {
    opacity: 1;
  }
`;

const PlayButton = styled.button`
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #1a1a2e;

  &:hover {
    background: rgba(255, 255, 255, 1);
    transform: scale(1.1);
  }

  &:active {
    transform: scale(0.95);
  }
`;

const PlayerInfo = styled.div`
  padding: 12px;
  background: linear-gradient(180deg, #1a1a2e 0%, #0f3460 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const MediaTitle = styled.h3`
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const CreatorName = styled.p`
  margin: 0;
  font-size: 12px;
  color: #a8b3ff;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  position: relative;

  &:hover {
    height: 6px;
  }
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%);
  transition: width 0.1s linear;
  border-radius: 2px;
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const ControlButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 16px;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
  }

  &:active {
    transform: scale(0.95);
  }

  &.active {
    background: rgba(0, 212, 255, 0.3);
    border-color: #00d4ff;
    color: #00d4ff;
  }
`;

const PlayPauseButton = styled(ControlButton)`
  flex: 1;
  font-size: 20px;
`;

const TimeDisplay = styled.span`
  font-size: 11px;
  color: #a8b3ff;
  font-weight: 500;
`;

const VolumeControl = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
`;

const VolumeSlider = styled.input`
  width: 60px;
  height: 4px;
  cursor: pointer;
  appearance: none;
  background: linear-gradient(
    to right,
    #00d4ff 0%,
    #00d4ff ${(props) => props.value * 100}%,
    rgba(255, 255, 255, 0.1) ${(props) => props.value * 100}%,
    rgba(255, 255, 255, 0.1) 100%
  );
  border-radius: 2px;
  outline: none;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #00d4ff;
    cursor: pointer;
    box-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
  }

  &::-moz-range-thumb {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #00d4ff;
    cursor: pointer;
    border: none;
    box-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
  }
`;

const QualityMenu = styled.div`
  position: absolute;
  bottom: 40px;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  z-index: 10000;
`;

const QualityOption = styled.button`
  background: none;
  border: none;
  color: #fff;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 12px;
  text-align: left;
  width: 100%;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(0, 212, 255, 0.2);
  }

  &.active {
    background: rgba(0, 212, 255, 0.4);
    color: #00d4ff;
  }
`;

const DragHandle = styled.div`
  cursor: grab;
  user-select: none;

  &:active {
    cursor: grabbing;
  }
`;

/**
 * Floating Media Player Component
 * Persists across all pages while user navigates
 */
const FloatingMediaPlayer = () => {
  const {
    currentMedia,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMinimized,
    isMuted,
    playbackRate,
    quality,
    togglePlayPause,
    seek,
    stop,
    toggleMinimize,
    setPlayerVolume,
    toggleMute,
    setPlayerPlaybackRate,
    setPlayerQuality,
    skip,
    getTimeDisplay,
  } = useMedia();

  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [showQualityMenu, setShowQualityMenu] = useState(false);

  // Handle dragging
  const handleMouseDown = (e) => {
    if (isMinimized && e.target.closest('[data-no-drag]') === null) {
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y,
      });
    }
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e) => {
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y,
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  // Handle progress bar click
  const handleProgressClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    seek(percent * duration);
  };

  if (!currentMedia) return null;

  const progressPercent = (currentTime / duration) * 100 || 0;
  const PlayerComponent = isMinimized ? MinimizedPlayer : MaximizedPlayer;

  return (
    <FloatingPlayerContainer
      style={{
        right: isMinimized ? `${position.x}px` : '20px',
        bottom: isMinimized ? `${position.y}px` : '20px',
      }}
    >
      <PlayerWrapper
        as={PlayerComponent}
        onMouseDown={handleMouseDown}
      >
        {!isMinimized && (
          <>
            {/* Thumbnail Section */}
            <PlayerThumbnail>
              {currentMedia.thumbnail && (
                <img src={currentMedia.thumbnail} alt={currentMedia.title} />
              )}
              <PlayingOverlay>
                <PlayButton onClick={() => togglePlayPause()}>
                  {isPlaying ? (
                    <Pause size={24} fill="currentColor" />
                  ) : (
                    <Play size={24} fill="currentColor" />
                  )}
                </PlayButton>
              </PlayingOverlay>
            </PlayerThumbnail>

            {/* Media Info */}
            <PlayerInfo>
              <MediaTitle title={currentMedia.title}>
                {currentMedia.title}
              </MediaTitle>
              {currentMedia.creator && (
                <CreatorName>{currentMedia.creator}</CreatorName>
              )}
            </PlayerInfo>

            {/* Progress Bar */}
            <ProgressBar onClick={handleProgressClick}>
              <ProgressFill style={{ width: `${progressPercent}%` }} />
            </ProgressBar>
          </>
        )}

        {/* Controls */}
        <Controls>
          <ControlButton
            onClick={() => skip(-10)}
            title="Rewind 10s"
            data-no-drag
          >
            <SkipBack size={16} />
          </ControlButton>

          <PlayPauseButton
            onClick={() => togglePlayPause()}
            title={isPlaying ? 'Pause' : 'Play'}
            data-no-drag
          >
            {isPlaying ? (
              <Pause size={20} fill="currentColor" />
            ) : (
              <Play size={20} fill="currentColor" />
            )}
          </PlayPauseButton>

          <ControlButton
            onClick={() => skip(10)}
            title="Forward 10s"
            data-no-drag
          >
            <SkipForward size={16} />
          </ControlButton>

          <VolumeControl data-no-drag>
            <ControlButton
              onClick={() => toggleMute()}
              className={isMuted ? 'active' : ''}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted || volume === 0 ? (
                <VolumeX size={16} />
              ) : (
                <Volume2 size={16} />
              )}
            </ControlButton>
            <VolumeSlider
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={(e) => setPlayerVolume(parseFloat(e.target.value))}
              title="Volume"
            />
          </VolumeControl>

          <ControlButton
            onClick={() => setShowQualityMenu(!showQualityMenu)}
            title="Quality"
            style={{ position: 'relative' }}
            data-no-drag
          >
            <Settings size={16} />
            {showQualityMenu && (
              <QualityMenu>
                {['auto', '360p', '480p', '720p', '1080p', '4k'].map((q) => (
                  <QualityOption
                    key={q}
                    className={quality === q ? 'active' : ''}
                    onClick={() => {
                      setPlayerQuality(q);
                      setShowQualityMenu(false);
                    }}
                  >
                    {q.toUpperCase()}
                  </QualityOption>
                ))}
              </QualityMenu>
            )}
          </ControlButton>

          <ControlButton
            onClick={() => toggleMinimize()}
            title={isMinimized ? 'Restore' : 'Minimize'}
            data-no-drag
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </ControlButton>

          <ControlButton
            onClick={() => stop()}
            title="Close"
            data-no-drag
          >
            <X size={16} />
          </ControlButton>
        </Controls>

        {/* Time Display */}
        {!isMinimized && (
          <div
            style={{
              padding: '8px 12px',
              background: 'rgba(0, 0, 0, 0.2)',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              textAlign: 'center',
              fontSize: '12px',
              color: '#a8b3ff',
            }}
          >
            <TimeDisplay>
              {getTimeDisplay(currentTime)} / {getTimeDisplay(duration)}
            </TimeDisplay>
          </div>
        )}
      </PlayerWrapper>
    </FloatingPlayerContainer>
  );
};

export default FloatingMediaPlayer;
