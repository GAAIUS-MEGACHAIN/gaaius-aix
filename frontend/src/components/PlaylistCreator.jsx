import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * PlaylistCreator Component
 * Create, manage, and share playlists across music, movies, videos, and more
 */
const PlaylistCreator = () => {
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================
  
  const [activeTab, setActiveTab] = useState('create');
  const [templates, setTemplates] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState(null);
  
  // Create form state
  const [createForm, setCreateForm] = useState({
    playlistName: '',
    description: '',
    visibility: 'private',
    contentType: 'music',
    mood: '',
    theme: '',
    tags: []
  });
  
  // Items to add
  const [itemsToAdd, setItemsToAdd] = useState([]);
  const [newItem, setNewItem] = useState({
    itemId: '',
    title: '',
    creator: '',
    duration: ''
  });
  
  // Share state
  const [shareSettings, setShareSettings] = useState({
    visibility: 'public',
    shareType: 'link',
    platform: ''
  });
  
  const [collaborators, setCollaborators] = useState([]);
  const [newCollaborator, setNewCollaborator] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [trendingPlaylists, setTrendingPlaylists] = useState([]);
  
  // ============================================================================
  // INITIALIZATION
  // ============================================================================
  
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const userId = localStorage.getItem('userId') || 'demo-user';
        
        // Fetch templates
        const templatesRes = await axios.get('/api/playlists/create/templates');
        setTemplates(templatesRes.data.templates);
        
        // Fetch user playlists
        const playlistsRes = await axios.get(`/api/playlists?user_id=${userId}`);
        setPlaylists(playlistsRes.data.playlists);
        
        // Fetch recommendations
        const recsRes = await axios.get(
          `/api/playlists/recommendations/for-user?user_id=${userId}&limit=5`
        );
        setRecommendations(recsRes.data.recommendations);
        
        // Fetch trending
        const trendingRes = await axios.get('/api/playlists/trending/all?limit=5');
        setTrendingPlaylists(trendingRes.data.trending);
      } catch (error) {
        console.error('Failed to fetch initial data:', error);
        showMessage('error', 'Failed to load playlists');
      } finally {
        setLoading(false);
      }
    };
    
    fetchInitialData();
  }, []);
  
  // ============================================================================
  // MESSAGE HELPERS
  // ============================================================================
  
  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };
  
  // ============================================================================
  // PLAYLIST CREATION
  // ============================================================================
  
  const handleCreatePlaylist = async () => {
    try {
      if (!createForm.playlistName.trim()) {
        showMessage('error', 'Playlist name is required');
        return;
      }
      
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const userName = localStorage.getItem('userName') || 'Demo User';
      
      let response;
      
      if (createForm.contentType === 'music') {
        response = await axios.post(
          '/api/playlists/create/music',
          {
            user_id: userId,
            user_name: userName,
            playlist_name: createForm.playlistName,
            mood: createForm.mood,
            tags: createForm.tags,
            track_ids: itemsToAdd.map(item => item.itemId)
          }
        );
      } else if (createForm.contentType === 'movie') {
        response = await axios.post(
          '/api/playlists/create/movies',
          {
            user_id: userId,
            user_name: userName,
            playlist_name: createForm.playlistName,
            genre: createForm.theme,
            movie_ids: itemsToAdd.map(item => item.itemId)
          }
        );
      } else if (createForm.contentType === 'video') {
        response = await axios.post(
          '/api/playlists/create/videos',
          {
            user_id: userId,
            user_name: userName,
            playlist_name: createForm.playlistName,
            video_ids: itemsToAdd.map(item => item.itemId)
          }
        );
      } else {
        response = await axios.post(
          '/api/playlists',
          {
            name: createForm.playlistName,
            user_id: userId,
            user_name: userName,
            description: createForm.description,
            visibility: createForm.visibility,
            mood: createForm.mood,
            tags: createForm.tags
          }
        );
      }
      
      showMessage('success', `Playlist "${createForm.playlistName}" created!`);
      
      // Reset form
      setCreateForm({
        playlistName: '',
        description: '',
        visibility: 'private',
        contentType: 'music',
        mood: '',
        theme: '',
        tags: []
      });
      setItemsToAdd([]);
      
      // Refresh playlists
      const playlistsRes = await axios.get(`/api/playlists?user_id=${userId}`);
      setPlaylists(playlistsRes.data.playlists);
    } catch (error) {
      console.error('Failed to create playlist:', error);
      showMessage('error', error.response?.data?.detail || 'Failed to create playlist');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateFromTemplate = async (templateId) => {
    try {
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const userName = localStorage.getItem('userName') || 'Demo User';
      
      const response = await axios.post(
        `/api/playlists/create/from-template?template_id=${templateId}&user_id=${userId}&user_name=${userName}`
      );
      
      showMessage('success', 'Playlist created from template!');
      
      // Refresh playlists
      const playlistsRes = await axios.get(`/api/playlists?user_id=${userId}`);
      setPlaylists(playlistsRes.data.playlists);
    } catch (error) {
      console.error('Failed to create from template:', error);
      showMessage('error', 'Failed to create playlist from template');
    } finally {
      setLoading(false);
    }
  };
  
  // ============================================================================
  // ITEM MANAGEMENT
  // ============================================================================
  
  const handleAddItem = () => {
    if (!newItem.itemId || !newItem.title) {
      showMessage('error', 'Item ID and title are required');
      return;
    }
    
    setItemsToAdd([...itemsToAdd, { ...newItem }]);
    setNewItem({ itemId: '', title: '', creator: '', duration: '' });
    showMessage('success', 'Item added to playlist');
  };
  
  const handleRemoveItem = (index) => {
    setItemsToAdd(itemsToAdd.filter((_, i) => i !== index));
  };
  
  // ============================================================================
  // SEARCH & DISCOVERY
  // ============================================================================
  
  const handleSearchPlaylists = async () => {
    try {
      if (!searchQuery.trim()) return;
      
      setLoading(true);
      const response = await axios.get(
        `/api/playlists/search/find?query=${encodeURIComponent(searchQuery)}&limit=10`
      );
      
      setRecommendations(response.data.results);
    } catch (error) {
      console.error('Search failed:', error);
      showMessage('error', 'Search failed');
    } finally {
      setLoading(false);
    }
  };
  
  // ============================================================================
  // SHARING & COLLABORATION
  // ============================================================================
  
  const handleSharePlaylist = async (playlistId) => {
    try {
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'demo-user';
      
      const response = await axios.post(
        `/api/playlists/share/${playlistId}?shared_by=${userId}&share_type=${shareSettings.shareType}&platform=${shareSettings.platform}`
      );
      
      showMessage('success', 'Playlist shared!');
    } catch (error) {
      console.error('Share failed:', error);
      showMessage('error', 'Failed to share playlist');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDuplicatePlaylist = async (playlistId) => {
    try {
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const userName = localStorage.getItem('userName') || 'Demo User';
      
      const response = await axios.post(
        `/api/playlists/share/${playlistId}/duplicate?user_id=${userId}&user_name=${userName}`
      );
      
      showMessage('success', 'Playlist duplicated!');
      
      // Refresh playlists
      const playlistsRes = await axios.get(`/api/playlists?user_id=${userId}`);
      setPlaylists(playlistsRes.data.playlists);
    } catch (error) {
      console.error('Duplicate failed:', error);
      showMessage('error', 'Failed to duplicate playlist');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddCollaborator = async () => {
    if (!selectedPlaylist || !newCollaborator) return;
    
    try {
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'demo-user';
      
      const response = await axios.post(
        `/api/playlists/share/${selectedPlaylist}/collaborator?collaborator_id=${newCollaborator}&user_id=${userId}`
      );
      
      setCollaborators([...collaborators, newCollaborator]);
      setNewCollaborator('');
      showMessage('success', 'Collaborator added!');
    } catch (error) {
      console.error('Failed to add collaborator:', error);
      showMessage('error', 'Failed to add collaborator');
    } finally {
      setLoading(false);
    }
  };
  
  // ============================================================================
  // ENGAGEMENT
  // ============================================================================
  
  const handleLikePlaylist = async (playlistId) => {
    try {
      const userId = localStorage.getItem('userId') || 'demo-user';
      
      await axios.post(
        `/api/playlists/${playlistId}/like?user_id=${userId}`
      );
      
      showMessage('success', 'Liked!');
    } catch (error) {
      console.error('Like failed:', error);
    }
  };
  
  const handleSavePlaylist = async (playlistId) => {
    try {
      const userId = localStorage.getItem('userId') || 'demo-user';
      
      await axios.post(
        `/api/playlists/${playlistId}/save?user_id=${userId}`
      );
      
      showMessage('success', 'Saved to library!');
    } catch (error) {
      console.error('Save failed:', error);
    }
  };
  
  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================
  
  const renderTags = () => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          placeholder="Add tag and press Enter"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          onKeyPress={(e) => {
            if (e.key === 'Enter' && e.target.value) {
              setCreateForm({
                ...createForm,
                tags: [...createForm.tags, e.target.value]
              });
              e.target.value = '';
            }
          }}
        />
      </div>
      <div className="flex flex-wrap gap-2">
        {createForm.tags.map((tag, idx) => (
          <span
            key={idx}
            className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-2 cursor-pointer"
            onClick={() => setCreateForm({
              ...createForm,
              tags: createForm.tags.filter((_, i) => i !== idx)
            })}
          >
            {tag} ✕
          </span>
        ))}
      </div>
    </div>
  );
  
  // ============================================================================
  // JSX RETURN
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">🎵 Playlist Creator</h1>
        <p className="text-gray-600">Create, curate, and share playlists across music, movies, videos, and more</p>
      </div>
      
      {/* Message Alert */}
      {message.text && (
        <div className={`max-w-6xl mx-auto mb-4 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message.text}
        </div>
      )}
      
      {/* Tabs */}
      <div className="max-w-6xl mx-auto mb-8 border-b border-gray-200">
        <div className="flex gap-4">
          {[
            { id: 'create', label: '✚ Create', icon: 'create' },
            { id: 'manage', label: '📝 My Playlists', icon: 'manage' },
            { id: 'discover', label: '🔍 Discover', icon: 'discover' },
            { id: 'templates', label: '📋 Templates', icon: 'templates' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium border-b-2 transition-all ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      <div className="max-w-6xl mx-auto">
        {/* CREATE TAB */}
        {activeTab === 'create' && (
          <div className="grid grid-cols-2 gap-8">
            {/* Form */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Create New Playlist</h2>
              
              <div className="space-y-4">
                {/* Playlist Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Playlist Name *</label>
                  <input
                    type="text"
                    placeholder="e.g., Summer Vibes 2026"
                    value={createForm.playlistName}
                    onChange={(e) => setCreateForm({ ...createForm, playlistName: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    placeholder="Add a description for your playlist"
                    value={createForm.description}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                    rows="3"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                {/* Content Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
                  <select
                    value={createForm.contentType}
                    onChange={(e) => setCreateForm({ ...createForm, contentType: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="music">🎵 Music</option>
                    <option value="movie">🎬 Movies</option>
                    <option value="video">📹 Videos</option>
                    <option value="mixed">🎭 Mixed Content</option>
                  </select>
                </div>
                
                {/* Visibility */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Visibility</label>
                  <select
                    value={createForm.visibility}
                    onChange={(e) => setCreateForm({ ...createForm, visibility: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="private">🔒 Private</option>
                    <option value="public">🌍 Public</option>
                    <option value="friends_only">👥 Friends Only</option>
                    <option value="link_only">🔗 Link Only</option>
                  </select>
                </div>
                
                {/* Mood */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mood</label>
                  <select
                    value={createForm.mood}
                    onChange={(e) => setCreateForm({ ...createForm, mood: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select mood...</option>
                    <option value="energetic">⚡ Energetic</option>
                    <option value="relaxed">😎 Relaxed</option>
                    <option value="focused">🎯 Focused</option>
                    <option value="adventurous">🚀 Adventurous</option>
                    <option value="sad">💙 Melancholic</option>
                    <option value="happy">😊 Happy</option>
                  </select>
                </div>
                
                {/* Tags */}
                {renderTags()}
                
                {/* Create Button */}
                <button
                  onClick={handleCreatePlaylist}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {loading ? 'Creating...' : '✓ Create Playlist'}
                </button>
              </div>
            </div>
            
            {/* Items Preview */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Add Items</h2>
              
              <div className="space-y-4 mb-6">
                {/* Add Item Form */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <div className="space-y-3">
                    <input
                      type="text"
                      placeholder="Item ID"
                      value={newItem.itemId}
                      onChange={(e) => setNewItem({ ...newItem, itemId: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                    <input
                      type="text"
                      placeholder="Title"
                      value={newItem.title}
                      onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                    <input
                      type="text"
                      placeholder="Creator/Artist"
                      value={newItem.creator}
                      onChange={(e) => setNewItem({ ...newItem, creator: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                    <input
                      type="text"
                      placeholder="Duration (e.g., 3:45)"
                      value={newItem.duration}
                      onChange={(e) => setNewItem({ ...newItem, duration: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                    <button
                      onClick={handleAddItem}
                      className="w-full bg-blue-600 text-white px-3 py-2 rounded text-sm font-medium hover:bg-blue-700"
                    >
                      + Add Item
                    </button>
                  </div>
                </div>
                
                {/* Items List */}
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {itemsToAdd.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No items added yet</p>
                  ) : (
                    itemsToAdd.map((item, idx) => (
                      <div key={idx} className="bg-gray-50 p-3 rounded flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{item.title}</p>
                          <p className="text-sm text-gray-600">{item.creator}</p>
                        </div>
                        <button
                          onClick={() => handleRemoveItem(idx)}
                          className="text-red-600 hover:text-red-800 font-bold ml-2"
                        >
                          ✕
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
              
              <p className="text-sm text-gray-600">
                <strong>{itemsToAdd.length}</strong> item(s) added
              </p>
            </div>
          </div>
        )}
        
        {/* MANAGE TAB */}
        {activeTab === 'manage' && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">My Playlists</h2>
            
            {playlists.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No playlists yet. Create one to get started!</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {playlists.map((playlist) => (
                  <div key={playlist.playlist_id} className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border border-gray-200 hover:shadow-lg transition-all cursor-pointer"
                    onClick={() => setSelectedPlaylist(playlist.playlist_id)}
                  >
                    <h3 className="font-bold text-gray-900 mb-2">{playlist.name}</h3>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{playlist.description}</p>
                    <div className="flex justify-between text-xs text-gray-500 mb-4">
                      <span>{playlist.item_count} items</span>
                      <span>{playlist.followers} followers</span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLikePlaylist(playlist.playlist_id);
                        }}
                        className="flex-1 bg-red-100 text-red-600 px-2 py-1 rounded text-sm hover:bg-red-200"
                      >
                        ❤️ Like
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDuplicatePlaylist(playlist.playlist_id);
                        }}
                        className="flex-1 bg-blue-100 text-blue-600 px-2 py-1 rounded text-sm hover:bg-blue-200"
                      >
                        📋 Duplicate
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSharePlaylist(playlist.playlist_id);
                        }}
                        className="flex-1 bg-green-100 text-green-600 px-2 py-1 rounded text-sm hover:bg-green-200"
                      >
                        🔗 Share
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* DISCOVER TAB */}
        {activeTab === 'discover' && (
          <div className="space-y-8">
            {/* Search */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Search Playlists</h2>
              
              <div className="flex gap-3 mb-6">
                <input
                  type="text"
                  placeholder="Search playlists by name, mood, genre..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearchPlaylists()}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSearchPlaylists}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
                >
                  🔍 Search
                </button>
              </div>
              
              {recommendations.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.map((playlist) => (
                    <div key={playlist.playlist_id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <h3 className="font-bold text-gray-900 mb-2">{playlist.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">by {playlist.creator_name}</p>
                      <p className="text-xs text-gray-500 mb-3">{playlist.item_count} items • {playlist.followers} followers</p>
                      <button
                        onClick={() => handleSavePlaylist(playlist.playlist_id)}
                        className="w-full bg-blue-100 text-blue-600 px-3 py-2 rounded text-sm font-medium hover:bg-blue-200"
                      >
                        💾 Save
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Trending */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Trending Playlists</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {trendingPlaylists.map((playlist) => (
                  <div key={playlist.playlist_id} className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg p-4 border border-yellow-200">
                    <h3 className="font-bold text-gray-900 mb-2">🔥 {playlist.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">by {playlist.creator_name}</p>
                    <div className="flex justify-between text-xs text-gray-500 mb-3">
                      <span>{playlist.item_count} items</span>
                      <span>{playlist.plays} plays</span>
                    </div>
                    <button
                      onClick={() => handleSavePlaylist(playlist.playlist_id)}
                      className="w-full bg-orange-100 text-orange-600 px-3 py-2 rounded text-sm font-medium hover:bg-orange-200"
                    >
                      ⭐ Save
                    </button>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Recommended For You</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.slice(0, 3).map((playlist) => (
                  <div key={playlist.playlist_id} className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                    <h3 className="font-bold text-gray-900 mb-2">💜 {playlist.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">by {playlist.creator_name}</p>
                    <button
                      onClick={() => handleSavePlaylist(playlist.playlist_id)}
                      className="w-full bg-purple-100 text-purple-600 px-3 py-2 rounded text-sm font-medium hover:bg-purple-200"
                    >
                      💾 Save
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* TEMPLATES TAB */}
        {activeTab === 'templates' && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">Playlist Templates</h2>
            <p className="text-gray-600 mb-6">Start creating instantly with our pre-designed templates</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((template) => (
                <div key={template.template_id} className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg p-6 border border-indigo-200 hover:shadow-lg transition-all cursor-pointer">
                  <div className="text-4xl mb-3">{template.icon}</div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{template.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                  <p className="text-xs text-gray-500 mb-4">
                    {template.content_type} • {template.category}
                  </p>
                  <button
                    onClick={() => handleCreateFromTemplate(template.template_id)}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all"
                  >
                    Create from Template
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaylistCreator;
