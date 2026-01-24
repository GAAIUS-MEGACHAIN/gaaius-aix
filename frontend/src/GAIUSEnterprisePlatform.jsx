/**
 * GAAIUS Complete Enterprise Platform Component
 * Stories, Video, Search, Algorithm, Effects, Marketplace, Ads, Creator Fund, Live Streaming
 * Production-grade UI with 10 independent platforms
 */

import React, { useState, useEffect, useRef } from 'react';
import { Heart, MessageCircle, Share2, Search, Plus, Home, ShoppingCart, Zap, Sparkles, Upload, Loader, TrendingUp, Video, Users, DollarSign, Radio } from 'lucide-react';

// Main GAAIUS Enterprise Platform Component (10-tab system)
export const GAIUSEnterprisePlatform = ({ user }) => {
  const [activeTab, setActiveTab] = useState('feed');
  const [loading, setLoading] = useState(false);
  const [socialPosts, setSocialPosts] = useState([]);
  const [stories, setStories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [marketplace, setMarketplace] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [creatorFund, setCreatorFund] = useState(null);
  const [liveStreams, setLiveStreams] = useState([]);
  const [effects, setEffects] = useState([]);

  // Form states
  const [postContent, setPostContent] = useState('');
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [aiEnhance, setAiEnhance] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const fileInputRef = useRef(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  // ==================== LOAD DATA BASED ON TAB ====================

  useEffect(() => {
    if (activeTab === 'feed') loadFeed();
    else if (activeTab === 'stories') loadStoriesFeed();
    else if (activeTab === 'search') loadTrending();
    else if (activeTab === 'marketplace') loadMarketplace();
    else if (activeTab === 'ads') loadCampaigns();
    else if (activeTab === 'profile') loadProfile();
    else if (activeTab === 'effects') loadEffects();
    else if (activeTab === 'creator-fund') loadCreatorFund();
    else if (activeTab === 'live') loadLiveStreams();
  }, [activeTab, user]);

  // ==================== CORE API CALLS ====================

  const loadFeed = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/social/feed`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setSocialPosts(data.posts || []);
    } catch (error) {
      console.error('Error loading feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStoriesFeed = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/stories/feed`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setStories(data.stories || []);
    } catch (error) {
      console.error('Error loading stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProfile = async () => {
    try {
      const response = await fetch(`${API_BASE}/social/profile/${user.id}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setUserProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const loadMarketplace = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/marketplace/listings`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setMarketplace(data.products || []);
    } catch (error) {
      console.error('Error loading marketplace:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await fetch(`${API_BASE}/ads/campaigns`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setCampaigns(data.campaigns || []);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    }
  };

  const loadEffects = async () => {
    try {
      const response = await fetch(`${API_BASE}/effects`);
      const data = await response.json();
      setEffects(data.effects || []);
    } catch (error) {
      console.error('Error loading effects:', error);
    }
  };

  const loadCreatorFund = async () => {
    try {
      const response = await fetch(`${API_BASE}/creator-fund`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setCreatorFund(data);
    } catch (error) {
      console.error('Error loading creator fund:', error);
    }
  };

  const loadLiveStreams = async () => {
    try {
      const response = await fetch(`${API_BASE}/live/active`);
      const data = await response.json();
      setLiveStreams(data.streams || []);
    } catch (error) {
      console.error('Error loading live streams:', error);
    }
  };

  const loadTrending = async () => {
    setLoading(true);
    try {
      if (searchQuery.trim()) {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(searchQuery)}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  // ==================== POST ACTIONS ====================

  const createPost = async () => {
    if (!postContent.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/social/posts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: postContent,
          media_items: selectedMedia ? [selectedMedia] : [],
          ai_enhance: aiEnhance
        })
      });
      const newPost = await response.json();
      setSocialPosts([newPost, ...socialPosts]);
      setPostContent('');
      setSelectedMedia(null);
      setAiEnhance(false);
      setShowCreateModal(false);
    } catch (error) {
      console.error('Error creating post:', error);
    } finally {
      setLoading(false);
    }
  };

  const likePost = async (postId) => {
    try {
      await fetch(`${API_BASE}/social/posts/${postId}/like`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setSocialPosts(socialPosts.map(p => 
        p.post_id === postId 
          ? { ...p, likes_count: (p.likes_count || 0) + 1 } 
          : p
      ));
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  // ==================== MARKETPLACE ACTIONS ====================

  const createMarketplaceListing = async (title, description, category, price) => {
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('category', category);
      formData.append('price', price);
      formData.append('images', selectedMedia?.url || '');

      const response = await fetch(`${API_BASE}/marketplace/listings`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });
      const listing = await response.json();
      setMarketplace([listing, ...marketplace]);
    } catch (error) {
      console.error('Error creating listing:', error);
    }
  };

  // ==================== ADS ACTIONS ====================

  const createAdCampaign = async (name, headline, description, budget) => {
    try {
      const formData = new FormData();
      formData.append('campaign_name', name);
      formData.append('headline', headline);
      formData.append('description', description);
      formData.append('daily_budget', budget);
      formData.append('image_url', selectedMedia?.url || '');
      formData.append('cta_url', 'https://gaaius.io');
      formData.append('target_interests', 'technology');

      const response = await fetch(`${API_BASE}/ads/campaigns`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });
      const campaign = await response.json();
      setCampaigns([campaign, ...campaigns]);
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
  };

  // ==================== LIVE STREAMING ACTIONS ====================

  const startLiveStream = async (title) => {
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('category', 'general');

      const response = await fetch(`${API_BASE}/live`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });
      const stream = await response.json();
      setLiveStreams([stream, ...liveStreams]);
      return stream;
    } catch (error) {
      console.error('Error starting live stream:', error);
    }
  };

  // ==================== UI COMPONENTS ====================

  const SidebarNav = () => (
    <div className="w-64 bg-black border-r border-purple-900/30 p-6 flex flex-col gap-4">
      <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500 mb-8">
        GAAIUS
      </div>

      <nav className="space-y-3 flex-1">
        {[
          { id: 'feed', icon: Home, label: 'Feed' },
          { id: 'stories', icon: Video, label: 'Stories' },
          { id: 'create', icon: Plus, label: 'Create' },
          { id: 'messages', icon: MessageCircle, label: 'Messages' },
          { id: 'search', icon: Search, label: 'Search' },
          { id: 'effects', icon: Sparkles, label: 'Effects' },
          { id: 'marketplace', icon: ShoppingCart, label: 'Marketplace' },
          { id: 'ads', icon: Zap, label: 'Ads Platform' },
          { id: 'live', icon: Radio, label: 'Live' },
          { id: 'creator-fund', icon: DollarSign, label: 'Creator Fund' },
          { id: 'profile', icon: Users, label: 'Profile' }
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
              activeTab === item.id
                ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white'
                : 'text-gray-300 hover:bg-purple-900/20'
            }`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="border-t border-purple-900/30 pt-4">
        <div className="text-sm text-gray-400">{user?.username || 'User'}</div>
        <div className="text-xs text-gray-500 mt-2">Verified ✓</div>
      </div>
    </div>
  );

  const Header = () => (
    <div className="h-20 bg-black border-b border-purple-900/30 px-8 flex items-center justify-between sticky top-0 z-40">
      <h1 className="text-2xl font-bold">
        {activeTab === 'feed' && 'Your Feed'}
        {activeTab === 'stories' && 'Stories'}
        {activeTab === 'create' && 'Create Post'}
        {activeTab === 'messages' && 'Messages'}
        {activeTab === 'search' && 'Search & Explore'}
        {activeTab === 'effects' && 'Effects Gallery'}
        {activeTab === 'marketplace' && 'Marketplace'}
        {activeTab === 'ads' && 'Ads Platform'}
        {activeTab === 'live' && 'Live Streaming'}
        {activeTab === 'creator-fund' && 'Creator Fund'}
        {activeTab === 'profile' && 'Your Profile'}
      </h1>
      <button
        onClick={() => setShowCreateModal(true)}
        className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full text-white hover:opacity-90 transition"
      >
        <Plus size={20} />
        Create
      </button>
    </div>
  );

  // ==================== CONTENT AREAS ====================

  const FeedTab = () => (
    <div className="space-y-4">
      {loading && <div className="text-center py-12"><Loader className="animate-spin mx-auto" /></div>}
      {!loading && socialPosts.length === 0 && <div className="text-center text-gray-400 py-12">No posts yet</div>}
      {socialPosts.map(post => (
        <div key={post.post_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full" />
            <div>
              <div className="font-semibold">{post.user_id}</div>
              <div className="text-xs text-gray-500">{new Date(post.created_at).toLocaleDateString()}</div>
            </div>
          </div>
          <p className="text-gray-200 mb-4">{post.content}</p>
          {post.media_items?.length > 0 && (
            <img src={post.media_items[0].url} alt="media" className="w-full h-64 object-cover rounded-lg mb-4" />
          )}
          <div className="flex items-center gap-6 text-gray-400">
            <button onClick={() => likePost(post.post_id)} className="flex items-center gap-2 hover:text-pink-500">
              <Heart size={18} /> {post.likes_count || 0}
            </button>
            <div className="flex items-center gap-2">{post.comments_count || 0} Comments</div>
            <div className="flex items-center gap-2">{post.shares_count || 0} Shares</div>
          </div>
        </div>
      ))}
    </div>
  );

  const StoriesTab = () => (
    <div className="space-y-4">
      {loading && <Loader className="animate-spin" />}
      {!loading && stories.length === 0 && <div className="text-gray-400">No stories</div>}
      {stories.map(story => (
        <div key={story.story_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl overflow-hidden">
          <img src={story.media_url} alt="story" className="w-full h-96 object-cover" />
          <div className="p-4">
            <div className="text-sm text-gray-400">Expires in {24} hours</div>
            <div className="text-sm mt-2">{story.caption}</div>
          </div>
        </div>
      ))}
    </div>
  );

  const CreateTab = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-8">
        <h2 className="text-xl font-bold mb-6">Create New Post</h2>
        <textarea
          value={postContent}
          onChange={(e) => setPostContent(e.target.value)}
          placeholder="What's on your mind?"
          className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-4 text-white placeholder-gray-500 resize-none h-32"
        />

        <div className="mt-4 flex gap-4 items-center">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-2 bg-purple-900/30 rounded-lg hover:bg-purple-900/50 transition"
          >
            <Upload size={18} />
            Upload Media
          </button>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={aiEnhance}
              onChange={(e) => setAiEnhance(e.target.checked)}
            />
            <Sparkles size={18} className="text-cyan-400" />
            Enhance with AI
          </label>
        </div>

        {selectedMedia && (
          <div className="mt-4 relative">
            <img src={selectedMedia.preview} alt="preview" className="w-full h-48 object-cover rounded-lg" />
            <button
              onClick={() => setSelectedMedia(null)}
              className="absolute top-2 right-2 bg-red-500 px-3 py-1 rounded text-white"
            >
              Remove
            </button>
          </div>
        )}

        <div className="mt-6 flex gap-3">
          <button
            onClick={createPost}
            disabled={loading || !postContent.trim()}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 transition"
          >
            {loading ? 'Posting...' : 'Post'}
          </button>
          <button className="flex-1 px-6 py-3 border border-purple-900/30 rounded-lg hover:bg-purple-900/20 transition">
            Draft
          </button>
        </div>
      </div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
              setSelectedMedia({
                preview: reader.result,
                file,
                url: reader.result
              });
            };
            reader.readAsDataURL(file);
          }
        }}
        hidden
      />
    </div>
  );

  const MarketplaceTab = () => (
    <div className="space-y-4">
      <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 mb-6">
        <h3 className="font-bold mb-4">Create New Listing</h3>
        <input type="text" placeholder="Title" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3" />
        <textarea placeholder="Description" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3 h-24" />
        <input type="number" placeholder="Price" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3" />
        <button className="w-full px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg font-semibold hover:opacity-90 transition">
          Create Listing
        </button>
      </div>

      <h3 className="font-bold text-lg mb-4">Marketplace Listings</h3>
      {loading && <Loader className="animate-spin" />}
      {!loading && marketplace.map(product => (
        <div key={product.product_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 flex gap-4">
          <div className="w-32 h-32 bg-gradient-to-br from-pink-500 to-purple-500 rounded-lg" />
          <div className="flex-1">
            <h4 className="font-bold text-lg">{product.title}</h4>
            <p className="text-gray-400 text-sm mt-2">{product.description?.substring(0, 100)}</p>
            <div className="mt-4 flex items-center justify-between">
              <div className="text-xl font-bold text-cyan-400">${product.price_usd}</div>
              <button className="px-6 py-2 bg-purple-900/30 rounded-lg hover:bg-purple-900/50 transition">
                Inquire
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const AdsTab = () => (
    <div className="space-y-4">
      <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 mb-6">
        <h3 className="font-bold mb-4">Create Ad Campaign</h3>
        <input type="text" placeholder="Campaign Name" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3" />
        <input type="text" placeholder="Headline" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3" />
        <textarea placeholder="Description" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3 h-20" />
        <input type="number" placeholder="Daily Budget ($)" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3" />
        <button className="w-full px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg font-semibold hover:opacity-90 transition">
          Create Campaign
        </button>
      </div>

      <h3 className="font-bold text-lg mb-4">Your Campaigns</h3>
      {campaigns.map(ad => (
        <div key={ad.ad_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold">{ad.campaign_name}</h4>
            <span className={`px-3 py-1 rounded text-sm ${ad.status === 'running' ? 'bg-green-900/30 text-green-400' : 'bg-gray-900/30 text-gray-400'}`}>
              {ad.status}
            </span>
          </div>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div><div className="text-gray-400">Impressions</div><div className="font-bold text-lg">{ad.impressions}</div></div>
            <div><div className="text-gray-400">Clicks</div><div className="font-bold text-lg">{ad.clicks}</div></div>
            <div><div className="text-gray-400">CTR</div><div className="font-bold text-lg">{(ad.ctr * 100).toFixed(2)}%</div></div>
            <div><div className="text-gray-400">Spend</div><div className="font-bold text-lg">${ad.spend_usd.toFixed(2)}</div></div>
          </div>
        </div>
      ))}
    </div>
  );

  const EffectsTab = () => (
    <div className="grid grid-cols-4 gap-4">
      {effects.map(effect => (
        <div key={effect.effect_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl overflow-hidden hover:border-cyan-500/30 transition cursor-pointer">
          <div className="aspect-square bg-gradient-to-br from-pink-500 to-purple-500" />
          <div className="p-4">
            <h4 className="font-bold text-sm">{effect.name}</h4>
            <div className="text-xs text-gray-500 mt-1">{effect.effect_type}</div>
            <div className="text-xs text-cyan-400 mt-2">{effect.downloads_count} downloads</div>
          </div>
        </div>
      ))}
    </div>
  );

  const LiveTab = () => (
    <div className="space-y-4">
      <button className="w-full px-6 py-4 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg font-bold flex items-center gap-2 hover:opacity-90 transition">
        <Radio size={20} />
        Start Live Stream
      </button>

      <h3 className="font-bold text-lg">Active Streams</h3>
      {liveStreams.map(stream => (
        <div key={stream.stream_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-32 h-20 bg-gradient-to-br from-pink-500 to-purple-500 rounded-lg" />
            <div className="flex-1">
              <h4 className="font-bold">{stream.title}</h4>
              <div className="text-sm text-gray-400 mt-1 flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                {stream.viewers_count} watching
              </div>
            </div>
            <button className="px-6 py-2 bg-purple-900/30 rounded-lg hover:bg-purple-900/50 transition">
              Watch
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const CreatorFundTab = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      {creatorFund && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Total Earnings</div>
              <div className="text-3xl font-bold mt-2 text-cyan-400">${creatorFund.total_earnings?.toFixed(2)}</div>
            </div>
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Pending</div>
              <div className="text-3xl font-bold mt-2 text-pink-500">${creatorFund.pending_balance?.toFixed(2)}</div>
            </div>
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Withdrawn</div>
              <div className="text-3xl font-bold mt-2 text-purple-500">${creatorFund.withdrawn_balance?.toFixed(2)}</div>
            </div>
          </div>

          {creatorFund.pending_balance >= 100 && (
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6">
              <h3 className="font-bold mb-4">Request Payout</h3>
              <input type="number" placeholder="Amount" className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3" />
              <select className="w-full bg-gray-800 border border-purple-900/30 rounded-lg p-3 text-white mb-3">
                <option>Select Payout Method</option>
                <option>Stripe</option>
                <option>PayPal</option>
                <option>Bank Transfer</option>
              </select>
              <button className="w-full px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg font-semibold hover:opacity-90 transition">
                Request Payout
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );

  const ProfileTab = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      {userProfile && (
        <>
          <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl overflow-hidden">
            <div className="h-40 bg-gradient-to-r from-pink-500 to-purple-500" />
            <div className="p-8 -mt-20 relative">
              <div className="w-32 h-32 bg-gradient-to-br from-pink-500 to-purple-500 rounded-full border-4 border-black mb-4" />
              <h2 className="text-3xl font-bold">{userProfile.display_name}</h2>
              <div className="text-gray-400 mt-1">@{userProfile.username}</div>
              {userProfile.bio && <p className="text-gray-300 mt-4">{userProfile.bio}</p>}
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Posts</div>
              <div className="text-2xl font-bold mt-2">{userProfile.posts_count}</div>
            </div>
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Followers</div>
              <div className="text-2xl font-bold mt-2">{userProfile.followers_count}</div>
            </div>
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Following</div>
              <div className="text-2xl font-bold mt-2">{userProfile.following_count}</div>
            </div>
            <div className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-6 text-center">
              <div className="text-gray-400 text-sm">Likes</div>
              <div className="text-2xl font-bold mt-2">{userProfile.total_likes_received}</div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  // ==================== MAIN RENDER ====================

  return (
    <div className="flex h-screen bg-black text-white">
      <SidebarNav />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto p-8">
          {activeTab === 'feed' && <FeedTab />}
          {activeTab === 'stories' && <StoriesTab />}
          {activeTab === 'create' && <CreateTab />}
          {activeTab === 'search' && (
            <div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && loadTrending()}
                placeholder="Search users, posts, videos..."
                className="w-full max-w-2xl bg-gray-900/50 border border-purple-900/30 rounded-lg p-4 text-white mb-6"
              />
              <div className="space-y-4">
                {searchResults.map(result => (
                  <div key={result.result_id} className="bg-gray-900/50 border border-purple-900/30 rounded-xl p-4">
                    <h3 className="font-bold">{result.title}</h3>
                    <div className="text-sm text-gray-400 mt-1">{result.result_type}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {activeTab === 'marketplace' && <MarketplaceTab />}
          {activeTab === 'ads' && <AdsTab />}
          {activeTab === 'effects' && <EffectsTab />}
          {activeTab === 'live' && <LiveTab />}
          {activeTab === 'creator-fund' && <CreatorFundTab />}
          {activeTab === 'profile' && <ProfileTab />}
          {activeTab === 'messages' && <div className="text-gray-400">Messages coming soon...</div>}
        </div>
      </div>
    </div>
  );
};

export default GAIUSEnterprisePlatform;
