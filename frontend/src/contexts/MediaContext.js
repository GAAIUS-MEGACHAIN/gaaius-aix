import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';

/**
 * Global Media Context for persistent player across all pages
 * Manages current playing media, playback state, and persistence
 */

const MediaContext = createContext(null);

export const MediaProvider = ({ children }) => {
  // Current media state
  const [currentMedia, setCurrentMedia] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMinimized, setIsMinimized] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [quality, setQuality] = useState('auto');
  const [isMuted, setIsMuted] = useState(false);

  // Player ref for actual playback control
  const playerRef = useRef(null);
  const mediaRef = useRef(null);

  // Load persisted state on mount
  useEffect(() => {
    const savedState = localStorage.getItem('mediaPlayerState');
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        setCurrentMedia(state.currentMedia);
        setVolume(state.volume || 0.8);
        setPlaybackRate(state.playbackRate || 1);
        setQuality(state.quality || 'auto');
      } catch (e) {
        console.error('Failed to load saved media state:', e);
      }
    }
  }, []);

  // Save state to localStorage on changes
  useEffect(() => {
    if (currentMedia) {
      const stateToSave = {
        currentMedia: {
          ...currentMedia,
          currentTime, // Save progress
        },
        volume,
        playbackRate,
        quality,
      };
      localStorage.setItem('mediaPlayerState', JSON.stringify(stateToSave));
    }
  }, [currentMedia, volume, playbackRate, quality, currentTime]);

  /**
   * Play a new media item
   * @param {Object} media - Media object with id, type, title, url, thumbnail, duration
   */
  const playMedia = useCallback((media) => {
    if (!media) return;

    setCurrentMedia({
      id: media.id,
      type: media.type, // 'video', 'music', 'livestream', 'movie', 'podcast', 'event'
      title: media.title,
      url: media.url,
      thumbnail: media.thumbnail,
      contentId: media.contentId,
      creator: media.creator,
      duration: media.duration || 0,
    });

    setCurrentTime(0);
    setIsPlaying(true);
    setIsMinimized(false);

    // Track playback start in backend (optional)
    trackPlaybackStart(media);
  }, []);

  /**
   * Resume playback of current media
   */
  const resume = useCallback(() => {
    setIsPlaying(true);
  }, []);

  /**
   * Pause playback
   */
  const pause = useCallback(() => {
    setIsPlaying(false);
  }, []);

  /**
   * Toggle play/pause
   */
  const togglePlayPause = useCallback(() => {
    setIsPlaying((prev) => !prev);
  }, []);

  /**
   * Seek to specific time
   */
  const seek = useCallback((time) => {
    const clampedTime = Math.max(0, Math.min(time, duration));
    setCurrentTime(clampedTime);
  }, [duration]);

  /**
   * Stop and clear current media
   */
  const stop = useCallback(() => {
    setCurrentMedia(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    localStorage.removeItem('mediaPlayerState');
  }, []);

  /**
   * Toggle minimize/restore
   */
  const toggleMinimize = useCallback(() => {
    setIsMinimized((prev) => !prev);
  }, []);

  /**
   * Set volume (0-1)
   */
  const setPlayerVolume = useCallback((vol) => {
    const clampedVolume = Math.max(0, Math.min(vol, 1));
    setVolume(clampedVolume);
    if (clampedVolume > 0) setIsMuted(false);
  }, []);

  /**
   * Toggle mute
   */
  const toggleMute = useCallback(() => {
    setIsMuted((prev) => !prev);
  }, []);

  /**
   * Set playback rate (0.5, 0.75, 1, 1.25, 1.5, 2)
   */
  const setPlayerPlaybackRate = useCallback((rate) => {
    const validRates = [0.5, 0.75, 1, 1.25, 1.5, 2];
    if (validRates.includes(rate)) {
      setPlaybackRate(rate);
    }
  }, []);

  /**
   * Change quality
   */
  const setPlayerQuality = useCallback((qual) => {
    const validQualities = ['auto', '360p', '480p', '720p', '1080p', '4k'];
    if (validQualities.includes(qual)) {
      setQuality(qual);
    }
  }, []);

  /**
   * Skip forward/backward
   */
  const skip = useCallback((seconds) => {
    seek(currentTime + seconds);
  }, [currentTime, seek]);

  /**
   * Get time display format (MM:SS)
   */
  const getTimeDisplay = useCallback((time) => {
    if (!time || isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, []);

  /**
   * Track playback start in backend
   */
  const trackPlaybackStart = useCallback(async (media) => {
    try {
      const token = localStorage.getItem('gaaius_token');
      if (!token) return;

      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/media/track-playback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          mediaId: media.id,
          type: media.type,
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (e) {
      console.error('Failed to track playback:', e);
    }
  }, []);

  /**
   * Save playback progress to backend
   */
  const savePlaybackProgress = useCallback(async () => {
    if (!currentMedia) return;

    try {
      const token = localStorage.getItem('gaaius_token');
      if (!token) return;

      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/media/save-progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          mediaId: currentMedia.id,
          currentTime,
          duration,
          type: currentMedia.type,
        }),
      });
    } catch (e) {
      console.error('Failed to save progress:', e);
    }
  }, [currentMedia, currentTime, duration]);

  const value = {
    // State
    currentMedia,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMinimized,
    playbackRate,
    quality,
    isMuted,

    // Methods
    playMedia,
    resume,
    pause,
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
    savePlaybackProgress,

    // Refs
    playerRef,
    mediaRef,

    // Setters for internal use
    setCurrentTime,
    setDuration,
  };

  return <MediaContext.Provider value={value}>{children}</MediaContext.Provider>;
};

/**
 * Hook to use media context
 */
export const useMedia = () => {
  const context = useContext(MediaContext);
  if (!context) {
    throw new Error('useMedia must be used within MediaProvider');
  }
  return context;
};
