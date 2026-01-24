/**
 * PHASE 8: Netflix-Grade Movies Frontend
 * Advanced UI components for movies streaming platform
 * - Professional streaming player
 * - Dynamic recommendations
 * - User engagement (ratings, comments, bookmarks)
 * - Content filtering and search
 * - Advanced moderation indicators
 * - Enterprise-grade performance
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const MoviesPlatformContainer = {
  container: `
    min-h-screen bg-black text-white overflow-hidden
    font-sans tracking-wide
  `,
  navBar: `
    fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-black via-black to-transparent
    h-20 flex items-center px-8 border-b border-gray-800
    backdrop-blur-xl bg-opacity-95
  `,
  tabButtons: `
    flex gap-8 h-full items-center
  `,
  tabButton: (isActive) => `
    relative h-full flex items-center px-4 font-medium transition-all
    ${isActive 
      ? 'text-red-500 font-bold' 
      : 'text-gray-400 hover:text-white'}
    after:${isActive ? 'absolute bottom-0 left-0 right-0 h-1 bg-red-500' : ''}
  `,
  mainContent: `
    pt-20 pb-20 px-8
  `,
  heroSection: `
    relative w-full h-96 mb-12 rounded-2xl overflow-hidden
    bg-gradient-to-r from-red-600 to-red-900
    shadow-2xl
  `,
  gridContainer: `
    grid grid-cols-5 gap-6 mb-12
    lg:grid-cols-4 md:grid-cols-3 sm:grid-cols-2
  `,
  movieCard: `
    group relative rounded-xl overflow-hidden
    h-72 cursor-pointer transition-all duration-300
    hover:scale-105 hover:shadow-2xl hover:z-10
    bg-gray-900
  `,
  movieImage: `
    w-full h-full object-cover
  `,
  movieOverlay: `
    absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent
    opacity-0 group-hover:opacity-100 transition-opacity duration-300
    flex flex-col justify-end p-4
  `,
  movieTitle: `
    font-bold text-lg mb-2
  `,
  movieMeta: `
    text-xs text-gray-300 space-y-1
  `,
  ratingBadge: `
    inline-flex items-center gap-2 px-3 py-1
    bg-yellow-500 text-black rounded-full font-bold text-xs
  `,
  moderationBadge: (level) => {
    const colors = {
      'safe': 'bg-green-500 text-white',
      'low_risk': 'bg-blue-500 text-white',
      'medium_risk': 'bg-yellow-600 text-white',
      'high_risk': 'bg-red-600 text-white',
      'blocked': 'bg-red-900 text-white'
    };
    return `inline-flex items-center px-3 py-1 rounded-full font-bold text-xs ${colors[level] || colors['safe']}`;
  },
  playerContainer: `
    fixed inset-0 z-40 bg-black bg-opacity-95 flex items-center justify-center
    p-4
  `,
  playerWindow: `
    w-full max-w-6xl rounded-2xl overflow-hidden
    shadow-2xl
  `,
  videoPlayer: `
    w-full aspect-video bg-black
  `,
  playerControls: `
    bg-gray-900 p-4 space-y-4
  `,
  seekBar: `
    w-full h-2 bg-gray-700 rounded-full cursor-pointer
    hover:h-3 transition-all
  `,
  controls: `
    flex items-center gap-4 justify-between
  `,
  engagementSection: `
    flex gap-6 items-center
  `,
  engagementButton: `
    flex items-center gap-2 px-4 py-2
    bg-gray-800 hover:bg-red-600 rounded-lg
    transition-colors duration-200 font-medium
  `,
  commentSection: `
    mt-6 space-y-4 max-h-96 overflow-y-auto
  `,
  comment: `
    bg-gray-900 p-4 rounded-lg
    border-l-2 border-red-500
  `,
  recommendationsSection: `
    mt-12 space-y-6
  `,
  recommendationCategory: `
    space-y-4
  `,
  categoryTitle: `
    text-2xl font-bold mb-4
    bg-gradient-to-r from-red-500 to-red-600
    bg-clip-text text-transparent
  `,
  loadingSpinner: `
    flex items-center justify-center p-8
  `,
  spinner: `
    w-12 h-12 border-4 border-red-500 border-t-transparent
    rounded-full animate-spin
  `,
  searchBar: `
    flex items-center gap-4 flex-1 max-w-md
    bg-gray-900 rounded-lg px-4 py-2 border border-gray-700
    focus-within:border-red-500 transition-colors
  `,
  filterSection: `
    flex gap-4 items-center py-6 border-b border-gray-800
    overflow-x-auto pb-4
  `,
  filterChip: (isActive) => `
    px-4 py-2 rounded-full whitespace-nowrap font-medium
    ${isActive 
      ? 'bg-red-500 text-white' 
      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}
    transition-all cursor-pointer
  `,
};

// ============================================================================
// MOVIES TAB COMPONENT
// ============================================================================

const MoviesTab = () => {
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [recommendationType, setRecommendationType] = useState('personalized');
  const [filteredMovies, setFilteredMovies] = useState([]);
  const [activeGenreFilter, setActiveGenreFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState({
    personalized: [],
    trending: [],
    mostWatched: [],
    topRated: []
  });
  const videoRef = useRef(null);

  // Fetch movies on mount
  useEffect(() => {
    fetchFeaturedMovies();
    fetchRecommendations();
  }, []);

  const fetchFeaturedMovies = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/movies/featured', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setMovies(data.movies || []);
      setFilteredMovies(data.movies || []);
    } catch (error) {
      console.error('Failed to fetch movies:', error);
    }
    setLoading(false);
  };

  const fetchRecommendations = async () => {
    try {
      const types = ['personalized', 'trending', 'most_watched', 'top_rated'];
      const recs = {};
      
      for (const type of types) {
        const response = await fetch(`/api/movies/recommendations?type=${type}&limit=20`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        recs[type] = data.recommendations || [];
      }
      
      setRecommendations(recs);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };

  const handleMovieClick = async (movie) => {
    setSelectedMovie(movie);
    // Fetch full details
    try {
      const response = await fetch(`/api/movies/${movie.movie_id}/details`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const details = await response.json();
      setSelectedMovie(details);
    } catch (error) {
      console.error('Failed to fetch movie details:', error);
    }
  };

  const handleRateMovie = async (rating) => {
    if (!selectedMovie) return;
    try {
      const response = await fetch(`/api/movies/${selectedMovie.movie_id}/rate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rating })
      });
      const data = await response.json();
      // Update local state
      setSelectedMovie(prev => ({
        ...prev,
        stats: { ...prev.stats, average_rating: data.average_rating }
      }));
    } catch (error) {
      console.error('Failed to rate movie:', error);
    }
  };

  const handleLikeMovie = async () => {
    if (!selectedMovie) return;
    try {
      const response = await fetch(`/api/movies/${selectedMovie.movie_id}/like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        setSelectedMovie(prev => ({
          ...prev,
          stats: {
            ...prev.stats,
            likes: prev.stats.likes + 1
          }
        }));
      }
    } catch (error) {
      console.error('Failed to like movie:', error);
    }
  };

  const handleAddComment = async (comment) => {
    if (!selectedMovie) return;
    try {
      const response = await fetch(`/api/movies/${selectedMovie.movie_id}/comment`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ comment })
      });
      if (response.ok) {
        // Refresh comments
        const detailsResponse = await fetch(`/api/movies/${selectedMovie.movie_id}/details`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const details = await detailsResponse.json();
        setSelectedMovie(details);
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const filterMovies = useCallback((movies, genre, search) => {
    return movies.filter(movie => {
      const matchesGenre = genre === 'all' || (movie.genre && movie.genre.includes(genre));
      const matchesSearch = search === '' || 
        movie.title.toLowerCase().includes(search.toLowerCase()) ||
        (movie.description && movie.description.toLowerCase().includes(search.toLowerCase()));
      return matchesGenre && matchesSearch;
    });
  }, []);

  useEffect(() => {
    const filtered = filterMovies(movies, activeGenreFilter, searchQuery);
    setFilteredMovies(filtered);
  }, [movies, activeGenreFilter, searchQuery, filterMovies]);

  const genres = useMemo(() => {
    const allGenres = new Set();
    movies.forEach(movie => {
      if (movie.genre) {
        movie.genre.forEach(g => allGenres.add(g));
      }
    });
    return ['all', ...Array.from(allGenres)];
  }, [movies]);

  return (
    <div className={MoviesPlatformContainer.container}>
      {/* Featured Hero */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={MoviesPlatformContainer.heroSection}
      >
        <div className="absolute inset-0 bg-black opacity-40"></div>
        <div className="absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-black to-transparent">
          <h1 className="text-5xl font-black mb-2">Now Streaming</h1>
          <p className="text-gray-300 text-lg">Premium movies and trailers</p>
        </div>
      </motion.div>

      {/* Filter Section */}
      <div className={MoviesPlatformContainer.filterSection}>
        <div className={MoviesPlatformContainer.searchBar}>
          <span className="text-gray-400">🔍</span>
          <input
            type="text"
            placeholder="Search movies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 bg-transparent outline-none"
          />
        </div>
        
        <div className="flex gap-2 overflow-x-auto">
          {genres.map(genre => (
            <button
              key={genre}
              onClick={() => setActiveGenreFilter(genre)}
              className={MoviesPlatformContainer.filterChip(activeGenreFilter === genre)}
            >
              {genre.charAt(0).toUpperCase() + genre.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Movies Grid */}
      {loading ? (
        <div className={MoviesPlatformContainer.loadingSpinner}>
          <div className={MoviesPlatformContainer.spinner}></div>
        </div>
      ) : (
        <>
          <div className={MoviesPlatformContainer.gridContainer}>
            {filteredMovies.map(movie => (
              <motion.div
                key={movie.movie_id}
                whileHover={{ scale: 1.05 }}
                onClick={() => handleMovieClick(movie)}
                className={MoviesPlatformContainer.movieCard}
              >
                <div className={MoviesPlatformContainer.movieImage}>
                  <div className="w-full h-full bg-gradient-to-br from-red-600 to-red-900 flex items-center justify-center text-4xl">
                    🎬
                  </div>
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  className={MoviesPlatformContainer.movieOverlay}
                >
                  <h3 className={MoviesPlatformContainer.movieTitle}>{movie.title}</h3>
                  <div className={MoviesPlatformContainer.movieMeta}>
                    <div>⭐ {movie.rating?.toFixed(1) || 'N/A'} / 5</div>
                    <div>👁️ {movie.view_count || 0} views</div>
                    <div>📽️ {movie.duration_minutes || 'N/A'} min</div>
                    <div>{movie.genre?.join(', ') || 'Unknown'}</div>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </>
      )}

      {/* Movie Player Modal */}
      <AnimatePresence>
        {selectedMovie && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className={MoviesPlatformContainer.playerContainer}
            onClick={() => setSelectedMovie(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
              className={MoviesPlatformContainer.playerWindow}
            >
              {/* Video Player */}
              <div className={MoviesPlatformContainer.videoPlayer}>
                <video
                  ref={videoRef}
                  controls
                  className="w-full h-full"
                  autoPlay
                >
                  <source src={`/api/movies/${selectedMovie.movie_id}/stream`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>

              {/* Movie Info and Controls */}
              <div className={MoviesPlatformContainer.playerControls}>
                <div>
                  <h2 className="text-2xl font-bold mb-2">{selectedMovie.title}</h2>
                  <div className="flex gap-4 mb-4 items-center">
                    <span className={MoviesPlatformContainer.ratingBadge}>
                      ⭐ {selectedMovie.stats?.average_rating?.toFixed(1) || 'N/A'}
                    </span>
                    <span className={MoviesPlatformContainer.moderationBadge(selectedMovie.moderation?.level)}>
                      {selectedMovie.moderation?.level?.toUpperCase() || 'SAFE'}
                    </span>
                    <span className="text-gray-400">
                      {selectedMovie.duration_minutes} min
                    </span>
                  </div>
                  <p className="text-gray-300 mb-4">{selectedMovie.description}</p>
                </div>

                {/* Engagement Buttons */}
                <div className={MoviesPlatformContainer.engagementSection}>
                  <button className={MoviesPlatformContainer.engagementButton} onClick={handleLikeMovie}>
                    👍 {selectedMovie.stats?.likes || 0} Likes
                  </button>
                  <button className={MoviesPlatformContainer.engagementButton}>
                    💬 {selectedMovie.stats?.comments || 0} Comments
                  </button>
                  <button className={MoviesPlatformContainer.engagementButton}>
                    🔖 {selectedMovie.stats?.bookmarks || 0} Bookmarks
                  </button>
                </div>

                {/* Rating Section */}
                <div className="mt-6">
                  <p className="font-bold mb-2">Rate this movie:</p>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map(rating => (
                      <button
                        key={rating}
                        onClick={() => handleRateMovie(rating)}
                        className="text-2xl hover:scale-125 transition-transform"
                      >
                        ⭐
                      </button>
                    ))}
                  </div>
                </div>

                {/* Comments Section */}
                <div className={MoviesPlatformContainer.commentSection}>
                  {selectedMovie.comments?.map(comment => (
                    <motion.div
                      key={comment.comment_id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={MoviesPlatformContainer.comment}
                    >
                      <p className="font-bold text-sm mb-1">{comment.user_id}</p>
                      <p className="text-gray-300">{comment.text}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(comment.timestamp).toLocaleDateString()}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recommendations */}
      <div className={MoviesPlatformContainer.recommendationsSection}>
        {Object.entries(recommendations).map(([type, movies]) => (
          movies.length > 0 && (
            <div key={type} className={MoviesPlatformContainer.recommendationCategory}>
              <h3 className={MoviesPlatformContainer.categoryTitle}>
                {type === 'personalized' && 'For You'}
                {type === 'trending' && 'Trending Now'}
                {type === 'most_watched' && 'Most Watched'}
                {type === 'top_rated' && 'Top Rated'}
              </h3>
              <div className={MoviesPlatformContainer.gridContainer}>
                {movies.slice(0, 5).map(movie => (
                  <motion.div
                    key={movie.movie_id}
                    whileHover={{ scale: 1.05 }}
                    onClick={() => handleMovieClick(movie)}
                    className={MoviesPlatformContainer.movieCard}
                  >
                    <div className={MoviesPlatformContainer.movieImage}>
                      <div className="w-full h-full bg-gradient-to-br from-red-600 to-red-900 flex items-center justify-center text-4xl">
                        🎬
                      </div>
                    </div>
                    <motion.div
                      initial={{ opacity: 0 }}
                      whileHover={{ opacity: 1 }}
                      className={MoviesPlatformContainer.movieOverlay}
                    >
                      <h3 className={MoviesPlatformContainer.movieTitle}>{movie.title}</h3>
                      <div className={MoviesPlatformContainer.movieMeta}>
                        <div>⭐ {movie.rating?.toFixed(1) || 'N/A'}</div>
                        <div>👁️ {movie.view_count || 0}</div>
                        <div>{movie.type}</div>
                      </div>
                    </motion.div>
                  </motion.div>
                ))}
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
};

export default MoviesTab;
