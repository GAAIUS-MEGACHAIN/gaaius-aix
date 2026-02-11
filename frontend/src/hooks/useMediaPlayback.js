import { useMedia } from '@/contexts/MediaContext';

/**
 * Hook for content pages to easily start/manage media playback
 * Usage in video/music/livestream pages:
 * 
 * const { startPlaying } = useMediaPlayback();
 * 
 * // When video loads:
 * startPlaying({
 *   id: videoId,
 *   type: 'video',
 *   title: 'Video Title',
 *   url: 'https://...',
 *   thumbnail: 'https://...',
 *   duration: 120,
 *   creator: 'Creator Name'
 * });
 */

export const useMediaPlayback = () => {
  const media = useMedia();

  return {
    // Start playing new media
    startPlaying: (mediaData) => {
      media.playMedia(mediaData);
    },

    // Get current playing info
    getCurrentMedia: () => media.currentMedia,
    
    // Check if something is playing
    isPlayingNow: () => media.isPlaying,

    // Get current playback position
    getProgress: () => ({
      currentTime: media.currentTime,
      duration: media.duration,
      percent: (media.currentTime / media.duration) * 100 || 0,
    }),

    // Control playback
    play: () => media.resume(),
    pause: () => media.pause(),
    togglePlay: () => media.togglePlayPause(),
    stop: () => media.stop(),

    // Seek
    seek: (time) => media.seek(time),
    skipForward: (seconds = 10) => media.skip(seconds),
    skipBackward: (seconds = 10) => media.skip(-seconds),

    // Volume
    setVolume: (vol) => media.setPlayerVolume(vol),
    toggleMute: () => media.toggleMute(),
    isMuted: () => media.isMuted,

    // Playback rate
    setPlaybackSpeed: (rate) => media.setPlayerPlaybackRate(rate),
    getPlaybackSpeed: () => media.playbackRate,

    // Quality
    setQuality: (qual) => media.setPlayerQuality(qual),
    getQuality: () => media.quality,

    // UI
    minimizePlayer: () => media.toggleMinimize(),
    isMinimized: () => media.isMinimized,

    // Utility
    formatTime: (seconds) => media.getTimeDisplay(seconds),
    saveProgress: () => media.savePlaybackProgress(),
  };
};

/**
 * HOC to wrap content components with media playback capability
 */
export const withMediaPlayback = (Component) => {
  return (props) => {
    const mediaPlayback = useMediaPlayback();
    return <Component {...props} mediaPlayback={mediaPlayback} />;
  };
};
