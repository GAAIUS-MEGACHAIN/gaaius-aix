import { useCallback } from 'react';

/**
 * Hook for playing media and persisting it across navigation
 * @returns {Object} Object with playMedia and stopMedia functions
 */
export const useMediaPlayer = () => {
  const playMedia = useCallback((mediaData) => {
    // Save to localStorage so player knows to display
    const mediaObject = {
      id: mediaData.id || `media-${Date.now()}`,
      title: mediaData.title || 'Unknown Title',
      artist: mediaData.artist || mediaData.creator || 'Unknown Artist',
      creator: mediaData.creator || 'Unknown Creator',
      type: mediaData.type || 'music', // music, podcast, audiobook, etc
      url: mediaData.url || mediaData.media_url || '',
      thumbnail: mediaData.thumbnail || mediaData.image_url || 'https://via.placeholder.com/80',
      duration: mediaData.duration || 0,
      contentType: mediaData.contentType || 'MUSIC', // MUSIC, VIDEO, LIVESTREAM, PODCAST
      timestamp: new Date().toISOString(),
    };

    // Save to localStorage for persistence
    localStorage.setItem('currentMedia', JSON.stringify(mediaObject));

    // Dispatch event so other components can react
    window.dispatchEvent(
      new CustomEvent('mediaPlayerUpdate', { detail: mediaObject })
    );

    return mediaObject;
  }, []);

  const stopMedia = useCallback(() => {
    localStorage.removeItem('currentMedia');
    window.dispatchEvent(new CustomEvent('mediaPlayerStop'));
  }, []);

  const updateMediaProgress = useCallback((mediaId, currentTime, duration) => {
    // Save progress to localStorage
    const progress = {
      mediaId,
      currentTime,
      duration,
      lastUpdated: new Date().toISOString(),
    };
    localStorage.setItem(`progress-${mediaId}`, JSON.stringify(progress));
  }, []);

  const getMediaProgress = useCallback((mediaId) => {
    const progress = localStorage.getItem(`progress-${mediaId}`);
    return progress ? JSON.parse(progress) : null;
  }, []);

  return {
    playMedia,
    stopMedia,
    updateMediaProgress,
    getMediaProgress,
  };
};

export default useMediaPlayer;
