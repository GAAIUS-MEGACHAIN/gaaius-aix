/**
 * AI Filter Studio - Real-time AR Filters Component
 * Production-grade React component with WebSocket streaming, real-time filters, and AI enhancements
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { AlertCircle, Settings, Zap, RotateCcw, Download, Share2 } from 'lucide-react';
import axios from 'axios';

const AIFilterStudio = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const animationIdRef = useRef(null);

  // State management
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [activeFilters, setActiveFilters] = useState(['beauty']);
  const [showSettings, setShowSettings] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedFrames, setRecordedFrames] = useState([]);

  // Beauty filter configs
  const [beautyConfig, setBeautyConfig] = useState({
    smoothing_strength: 0.5,
    brightness_adjustment: 0,
    contrast_adjustment: 0,
    saturation_boost: 0,
    eye_enlargement: 0,
    eye_brightness: 0,
    lips_tint: '#FF6B9D',
    lips_intensity: 0.5,
  });

  // Background filter config
  const [backgroundConfig, setBackgroundConfig] = useState({
    filter_type: 'blur',
    blur_strength: 25,
    replacement_color: '#FFFFFF',
    opacity: 1,
  });

  const [availableFilters, setAvailableFilters] = useState([]);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [detectedFaces, setDetectedFaces] = useState(0);

  // Snapchat filters state
  const [snapchatFilters, setSnapchatFilters] = useState({});
  const [availableSnapchatFilters, setAvailableSnapchatFilters] = useState([]);
  const [socialPlatform, setSocialPlatform] = useState('snapchat');
  const [platformFilters, setPlatformFilters] = useState([]);

  // Social media filters state
  const [socialFilters, setSocialFilters] = useState({});
  const [availableSocialFilters, setAvailableSocialFilters] = useState([]);
  const [selectedSocialPlatform, setSelectedSocialPlatform] = useState('instagram');
  const [selectedSocialFilters, setSelectedSocialFilters] = useState([]);
  const [socialPlatformFilters, setSocialPlatformFilters] = useState([]);

  // Advanced filters state
  const [advancedFilters, setAdvancedFilters] = useState({});
  const [availableAdvancedFilters, setAvailableAdvancedFilters] = useState([]);
  const [selectedAdvancedCategory, setSelectedAdvancedCategory] = useState('beauty');
  const [advancedCategories, setAdvancedCategories] = useState([]);
  const [categoryFilters, setCategoryFilters] = useState([]);

  // Menu state
  const [activeMenu, setActiveMenu] = useState('main'); // main, snapchat, social, advanced

  // Initialize session
  const initializeSession = useCallback(async () => {
    try {
      const response = await axios.post('/api/ai-filter-studio/session/create', {
        user_id: 'current_user',
      });
      setSessionId(response.data.session_id);
      return response.data.session_id;
    } catch (err) {
      setError('Failed to create session: ' + err.message);
      return null;
    }
  }, []);

  // Fetch available filters
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const response = await axios.get('/api/ai-filter-studio/filters/available');
        setAvailableFilters(response.data.filters);
      } catch (err) {
        console.error('Failed to fetch filters:', err);
      }
    };
    
    const fetchSnapchatFilters = async () => {
      try {
        const response = await axios.get('/api/ai-filter-studio/snapchat-filters/available');
        setAvailableSnapchatFilters(response.data.filters || []);
      } catch (err) {
        console.error('Failed to fetch Snapchat filters:', err);
      }
    };
    
    const fetchSocialFilters = async () => {
      try {
        const response = await axios.get('/api/ai-filter-studio/social-filters/available');
        setAvailableSocialFilters(response.data.filters || []);
      } catch (err) {
        console.error('Failed to fetch social filters:', err);
      }
    };

    const fetchAdvancedFilters = async () => {
      try {
        const response = await axios.get('/api/ai-filter-studio/advanced-filters/available');
        setAvailableAdvancedFilters(response.data.filters || []);
        setAdvancedCategories(response.data.categories || []);
        if (response.data.categories && response.data.categories.length > 0) {
          setSelectedAdvancedCategory(response.data.categories[0]);
        }
      } catch (err) {
        console.error('Failed to fetch advanced filters:', err);
      }
    };
    
    fetchFilters();
    fetchSnapchatFilters();
    fetchSocialFilters();
    fetchAdvancedFilters();
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!sessionId) return;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/stream/${sessionId}`;

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          switch (message.type) {
            case 'frame':
              handleFrameResponse(message);
              break;
            case 'metrics':
              setMetrics(message.data);
              break;
            case 'error':
              setError(message.error);
              break;
            default:
              break;
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Attempt reconnection after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId]);

  // Handle frame response from server
  const handleFrameResponse = useCallback((message) => {
    try {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        ctx.drawImage(img, 0, 0);
      };

      img.src = `data:image/jpeg;base64,${message.frame_base64}`;
      setDetectedFaces(message.detected_faces);

      if (message.ai_suggestions) {
        setAiSuggestions(message.ai_suggestions);
      }

      // Store frame if recording
      if (isRecording) {
        setRecordedFrames((prev) => [
          ...prev.slice(-299),
          message.frame_base64,
        ]);
      }
    } catch (err) {
      console.error('Error handling frame response:', err);
    }
  }, [isRecording]);

  // Start streaming
  const startStreaming = async () => {
    try {
      const sid = await initializeSession();
      if (!sid) return;

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: false,
      });

      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      videoRef.current.play();

      setIsStreaming(true);
      captureFrames();
    } catch (err) {
      setError('Failed to access camera: ' + err.message);
    }
  };

  // Capture and send frames
  const captureFrames = useCallback(() => {
    if (!isStreaming || !videoRef.current || !canvasRef.current || !wsRef.current) {
      return;
    }

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      const reader = new FileReader();
      reader.onload = () => {
        const frameBase64 = reader.result.split(',')[1];

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: 'frame',
              frame_base64: frameBase64,
              request_id: `${Date.now()}`,
            })
          );
        }
      };
      reader.readAsDataURL(blob);
    }, 'image/jpeg', 0.9);

    animationIdRef.current = requestAnimationFrame(captureFrames);
  }, [isStreaming]);

  useEffect(() => {
    if (isStreaming && videoRef.current && videoRef.current.readyState === 4) {
      captureFrames();
    }

    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, [isStreaming, captureFrames]);

  // Stop streaming
  const stopStreaming = () => {
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current);
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }

    setIsStreaming(false);
    setRecordedFrames([]);
  };

  // Send filter updates
  const updateFilters = useCallback(
    (filters) => {
      setActiveFilters(filters);
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'filters',
            filters: filters,
          })
        );
      }
    },
    []
  );

  // Send Snapchat filter updates
  const updateSnapchatFilters = useCallback(
    (filters) => {
      setSnapchatFilters(filters);
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'snapchat_filters',
            filters: filters,
            social_platform: socialPlatform
          })
        );
      }
    },
    [socialPlatform]
  );

  // Update social platform and fetch its filters
  const changeSocialPlatform = useCallback(
    (platform) => {
      setSocialPlatform(platform);
      
      // Fetch platform-specific filters
      axios.get(`/api/ai-filter-studio/snapchat-filters/by-platform/${platform}`)
        .then(response => {
          setPlatformFilters(response.data.filters || []);
        })
        .catch(err => console.error('Failed to fetch platform filters:', err));
    },
    []
  );

  // Update social media platform filters
  const changeSocialMediaPlatform = useCallback(
    (platform) => {
      setSelectedSocialPlatform(platform);
      
      // Fetch platform-specific social filters
      axios.get(`/api/ai-filter-studio/social-filters/by-platform/${platform}`)
        .then(response => {
          setSocialPlatformFilters(response.data.filters || []);
        })
        .catch(err => console.error('Failed to fetch social media platform filters:', err));
    },
    []
  );

  // Send social filters to WebSocket
  const updateSocialFilters = useCallback(
    (filterIds) => {
      setSelectedSocialFilters(filterIds);
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const intensities = {};
        filterIds.forEach(id => {
          intensities[id] = socialFilters[id] || 0.5;
        });
        
        wsRef.current.send(
          JSON.stringify({
            type: 'social_filters',
            filters: filterIds,
            intensities: intensities,
            platform: selectedSocialPlatform
          })
        );
      }
    },
    [socialFilters, selectedSocialPlatform]
  );

  // Update social filter intensity
  const updateSocialFilterIntensity = useCallback(
    (filterId, intensity) => {
      setSocialFilters(prev => ({
        ...prev,
        [filterId]: intensity
      }));
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'social_filter_intensity',
            filter_id: filterId,
            intensity: intensity,
            platform: selectedSocialPlatform
          })
        );
      }
    },
    [selectedSocialPlatform]
  );

  // Change advanced filter category
  const changeAdvancedCategory = useCallback(
    (category) => {
      setSelectedAdvancedCategory(category);
      
      // Fetch category-specific filters
      axios.get(`/api/ai-filter-studio/advanced-filters/by-category/${category}`)
        .then(response => {
          setCategoryFilters(response.data.filters || []);
        })
        .catch(err => console.error('Failed to fetch category filters:', err));
    },
    []
  );

  // Update advanced filter intensity
  const updateAdvancedFilterIntensity = useCallback(
    (filterId, intensity) => {
      setAdvancedFilters(prev => ({
        ...prev,
        [filterId]: intensity
      }));
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'advanced_filter_intensity',
            filter_id: filterId,
            intensity: intensity,
            category: selectedAdvancedCategory
          })
        );
      }
    },
    [selectedAdvancedCategory]
  );

  // Send advanced filters to WebSocket
  const updateAdvancedFilters = useCallback(
    (filterIds) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const intensities = {};
        filterIds.forEach(id => {
          intensities[id] = advancedFilters[id] || 0.5;
        });
        
        wsRef.current.send(
          JSON.stringify({
            type: 'advanced_filters',
            filters: filterIds,
            intensities: intensities,
            category: selectedAdvancedCategory
          })
        );
      }
    },
    [advancedFilters, selectedAdvancedCategory]
  );

  // Send config updates
  const updateBeautyConfig = useCallback((newConfig) => {
    setBeautyConfig(newConfig);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'config',
          beauty_config: newConfig,
        })
      );
    }
  }, []);

  const updateBackgroundConfig = useCallback((newConfig) => {
    setBackgroundConfig(newConfig);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'config',
          background_config: newConfig,
        })
      );
    }
  }, []);

  // Generate AI suggestions
  const generateAISuggestions = async () => {
    if (!canvasRef.current) return;

    try {
      const canvas = canvasRef.current;
      const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

      const response = await axios.post(
        '/api/ai-filter-studio/suggestions/generate',
        {
          frame_base64: imageData,
          filter_type: 'beauty',
        }
      );

      setAiSuggestions(response.data.suggestions);
    } catch (err) {
      console.error('Failed to generate suggestions:', err);
    }
  };

  // Download video
  const downloadVideo = () => {
    if (recordedFrames.length === 0) {
      alert('No frames recorded');
      return;
    }

    // Create video from frames (simplified - uses canvas animation)
    const canvas = canvasRef.current;
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/jpeg');
    link.download = `filtered-video-${Date.now()}.jpg`;
    link.click();
  };

  return (
    <div className="w-full h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white overflow-hidden">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="bg-black bg-opacity-50 backdrop-blur-md border-b border-cyan-500 border-opacity-30 p-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                AI Filter Studio
              </h1>
              <p className="text-sm text-slate-300 mt-1">
                Powered by Groq ML & Real-time AR
              </p>
            </div>
            <div className="flex gap-4">
              <div className="text-right">
                <div className="text-xs text-slate-400">Status</div>
                <div
                  className={`text-sm font-semibold ${
                    isConnected ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {isConnected ? '● Connected' : '● Disconnected'}
                </div>
              </div>
              {metrics && (
                <div className="text-right border-l border-slate-600 pl-4">
                  <div className="text-xs text-slate-400">Performance</div>
                  <div className="text-sm font-mono text-cyan-400">
                    {metrics.sessions[sessionId]?.fps || 0} FPS
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden p-4">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-4 h-full">
            {/* Video Canvas */}
            <div className="lg:col-span-3">
              <div className="bg-black rounded-lg overflow-hidden border border-cyan-500 border-opacity-30 h-full flex flex-col">
                {error && (
                  <div className="bg-red-500 bg-opacity-20 border-l-4 border-red-500 p-3 text-sm flex items-center gap-2">
                    <AlertCircle size={16} />
                    {error}
                  </div>
                )}

                {/* Canvas */}
                <div className="flex-1 bg-gradient-to-b from-slate-900 to-black relative">
                  <canvas
                    ref={canvasRef}
                    className="w-full h-full object-cover"
                    style={{ display: 'block' }}
                  />
                  <video
                    ref={videoRef}
                    className="hidden"
                    playsInline
                    muted
                  />

                  {!isStreaming && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                      <div className="text-center">
                        <div className="text-4xl mb-4">📸</div>
                        <p className="text-lg mb-4">
                          Click "Start Stream" to begin
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Detected Faces Badge */}
                  {isStreaming && (
                    <div className="absolute top-4 left-4 bg-cyan-500 bg-opacity-80 px-3 py-1 rounded text-sm font-semibold">
                      👤 {detectedFaces} face{detectedFaces !== 1 ? 's' : ''}
                    </div>
                  )}

                  {/* Recording Badge */}
                  {isRecording && (
                    <div className="absolute top-4 right-4 bg-red-500 bg-opacity-80 px-3 py-1 rounded text-sm font-semibold animate-pulse">
                      ● Recording
                    </div>
                  )}
                </div>

                {/* Controls */}
                <div className="bg-slate-900 border-t border-slate-700 p-4 flex gap-2">
                  <button
                    onClick={isStreaming ? stopStreaming : startStreaming}
                    className={`flex-1 py-2 px-4 rounded font-semibold transition ${
                      isStreaming
                        ? 'bg-red-600 hover:bg-red-700'
                        : 'bg-cyan-600 hover:bg-cyan-700'
                    }`}
                  >
                    {isStreaming ? '■ Stop Stream' : '▶ Start Stream'}
                  </button>

                  <button
                    onClick={() => setIsRecording(!isRecording)}
                    disabled={!isStreaming}
                    className={`px-4 py-2 rounded font-semibold transition ${
                      isRecording
                        ? 'bg-red-600 hover:bg-red-700'
                        : 'bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed'
                    }`}
                  >
                    ● Record
                  </button>

                  <button
                    onClick={downloadVideo}
                    disabled={recordedFrames.length === 0}
                    className="px-4 py-2 rounded font-semibold bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    title="Download recorded video"
                  >
                    <Download size={18} />
                  </button>

                  <button
                    onClick={generateAISuggestions}
                    disabled={!isStreaming}
                    className="px-4 py-2 rounded font-semibold bg-purple-700 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
                  >
                    <Zap size={18} />
                    AI Tips
                  </button>
                </div>
              </div>
            </div>

            {/* Sidebar - Filters & Settings */}
            <div className="flex flex-col gap-4">
              {/* Menu Tabs */}
              <div className="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
                <div className="flex gap-0">
                  <button
                    onClick={() => setActiveMenu('main')}
                    className={`flex-1 py-2 px-3 text-sm font-semibold transition border-r border-slate-700 ${
                      activeMenu === 'main'
                        ? 'bg-cyan-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    Main
                  </button>
                  <button
                    onClick={() => setActiveMenu('snapchat')}
                    className={`flex-1 py-2 px-3 text-sm font-semibold transition border-r border-slate-700 ${
                      activeMenu === 'snapchat'
                        ? 'bg-yellow-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    🔥 Snapchat
                  </button>
                  <button
                    onClick={() => setActiveMenu('social')}
                    className={`flex-1 py-2 px-3 text-sm font-semibold transition border-r border-slate-700 ${
                      activeMenu === 'social'
                        ? 'bg-pink-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    📱 Social
                  </button>
                  <button
                    onClick={() => setActiveMenu('advanced')}
                    className={`flex-1 py-2 px-3 text-sm font-semibold transition ${
                      activeMenu === 'advanced'
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    ✨ Advanced
                  </button>
                </div>
              </div>

              {/* Main Filters Tab */}
              {activeMenu === 'main' && (
              <div className="bg-slate-900 rounded-lg border border-slate-700 p-4">
                <h3 className="text-sm font-bold text-cyan-400 mb-3 uppercase tracking-wider">
                  Filters
                </h3>
                <div className="space-y-2">
                  {availableFilters.map((filter) => (
                    <label
                      key={filter.type}
                      className="flex items-center gap-2 cursor-pointer hover:bg-slate-800 p-2 rounded transition"
                    >
                      <input
                        type="checkbox"
                        checked={activeFilters.includes(filter.type)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            updateFilters([...activeFilters, filter.type]);
                          } else {
                            updateFilters(
                              activeFilters.filter((f) => f !== filter.type)
                            );
                          }
                        }}
                        className="w-4 h-4 accent-cyan-500"
                      />
                      <div>
                        <div className="text-sm font-medium">{filter.name}</div>
                        <div className="text-xs text-slate-400">
                          {filter.description}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
              )}

              {/* Snapchat Filters Tab */}
              {activeMenu === 'snapchat' && (
              <div className="bg-gradient-to-br from-yellow-900 to-red-900 rounded-lg border border-yellow-600 p-4">
                <h3 className="text-sm font-bold text-yellow-300 mb-3 uppercase tracking-wider">
                  🔥 Snapchat Filters
                </h3>
                
                {/* Social Platform Selector */}
                <div className="mb-3">
                  <label className="block text-xs text-yellow-200 mb-2 font-semibold">Social Platform</label>
                  <select
                    value={socialPlatform}
                    onChange={(e) => changeSocialPlatform(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-yellow-500 rounded text-yellow-100 text-sm"
                  >
                    <option value="snapchat">Snapchat</option>
                    <option value="instagram">Instagram</option>
                    <option value="tiktok">TikTok</option>
                    <option value="youtube">YouTube</option>
                    <option value="facebook">Facebook</option>
                  </select>
                </div>

                {/* Snapchat Filters Grid */}
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {platformFilters.length > 0 ? (
                    platformFilters.map((filter) => (
                      <div key={filter.id} className="flex items-center gap-3 bg-slate-800 bg-opacity-50 p-2 rounded border border-yellow-500 border-opacity-30">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-yellow-100">{filter.name}</div>
                          <div className="text-xs text-yellow-200 opacity-70">{filter.description}</div>
                        </div>
                        <div className="flex gap-1 items-center">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={snapchatFilters[filter.id] || 0}
                            onChange={(e) => {
                              const newFilters = {
                                ...snapchatFilters,
                                [filter.id]: parseFloat(e.target.value)
                              };
                              // Remove if 0
                              if (newFilters[filter.id] === 0) {
                                delete newFilters[filter.id];
                              }
                              updateSnapchatFilters(newFilters);
                            }}
                            className="w-24 h-1 accent-yellow-400"
                          />
                          <span className="text-xs text-yellow-200 w-8 text-right">
                            {Math.round((snapchatFilters[filter.id] || 0) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : availableSnapchatFilters.length > 0 ? (
                    availableSnapchatFilters.map((filter) => (
                      <div key={filter.id} className="flex items-center gap-3 bg-slate-800 bg-opacity-50 p-2 rounded border border-yellow-500 border-opacity-30">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-yellow-100">{filter.name}</div>
                          <div className="text-xs text-yellow-200 opacity-70">{filter.description}</div>
                        </div>
                        <div className="flex gap-1 items-center">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={snapchatFilters[filter.id] || 0}
                            onChange={(e) => {
                              const newFilters = {
                                ...snapchatFilters,
                                [filter.id]: parseFloat(e.target.value)
                              };
                              if (newFilters[filter.id] === 0) {
                                delete newFilters[filter.id];
                              }
                              updateSnapchatFilters(newFilters);
                            }}
                            className="w-24 h-1 accent-yellow-400"
                          />
                          <span className="text-xs text-yellow-200 w-8 text-right">
                            {Math.round((snapchatFilters[filter.id] || 0) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-yellow-200 opacity-50 p-2">No filters available for this platform</div>
                  )}
                </div>
              </div>
              )}

              {/* Social Media Filters Tab */}
              {activeMenu === 'social' && (
              <div className="bg-gradient-to-br from-pink-900 to-purple-900 rounded-lg border border-pink-500 p-4">
                <h3 className="text-sm font-bold text-pink-300 mb-3 uppercase tracking-wider">
                  📱 Social Media Filters
                </h3>
                
                {/* Platform Selector */}
                <div className="mb-3">
                  <label className="block text-xs text-pink-200 mb-2 font-semibold">Platform</label>
                  <select
                    value={selectedSocialPlatform}
                    onChange={(e) => changeSocialMediaPlatform(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-pink-400 rounded text-pink-100 text-sm"
                  >
                    <option value="instagram">📷 Instagram</option>
                    <option value="tiktok">🎵 TikTok</option>
                    <option value="youtube">▶️ YouTube</option>
                    <option value="facebook">👥 Facebook</option>
                  </select>
                </div>

                {/* Social Filters Grid */}
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {socialPlatformFilters.length > 0 ? (
                    socialPlatformFilters.map((filter) => (
                      <div key={filter.id} className="flex items-center gap-3 bg-slate-800 bg-opacity-50 p-2 rounded border border-pink-400 border-opacity-30 hover:border-opacity-60 transition">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-pink-100">{filter.name}</div>
                          <div className="text-xs text-pink-200 opacity-70">{filter.description}</div>
                          <div className="text-xs text-pink-300 opacity-50">{filter.category}</div>
                        </div>
                        <div className="flex gap-1 items-center">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={socialFilters[filter.id] || 0}
                            onChange={(e) => {
                              updateSocialFilterIntensity(filter.id, parseFloat(e.target.value));
                            }}
                            className="w-24 h-1 accent-pink-400"
                          />
                          <span className="text-xs text-pink-200 w-8 text-right">
                            {Math.round((socialFilters[filter.id] || 0) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : availableSocialFilters.length > 0 ? (
                    availableSocialFilters.map((filter) => (
                      <div key={filter.id} className="flex items-center gap-3 bg-slate-800 bg-opacity-50 p-2 rounded border border-pink-400 border-opacity-30 hover:border-opacity-60 transition">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-pink-100">{filter.name}</div>
                          <div className="text-xs text-pink-200 opacity-70">{filter.description}</div>
                          <div className="text-xs text-pink-300 opacity-50">{filter.category}</div>
                        </div>
                        <div className="flex gap-1 items-center">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={socialFilters[filter.id] || 0}
                            onChange={(e) => {
                              updateSocialFilterIntensity(filter.id, parseFloat(e.target.value));
                            }}
                            className="w-24 h-1 accent-pink-400"
                          />
                          <span className="text-xs text-pink-200 w-8 text-right">
                            {Math.round((socialFilters[filter.id] || 0) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-pink-200 opacity-50 p-2">Loading filters for {selectedSocialPlatform}...</div>
                  )}
                </div>

                {/* Apply All Filters Button */}
                {Object.keys(socialFilters).length > 0 && (
                  <button
                    onClick={() => updateSocialFilters(Object.keys(socialFilters))}
                    className="w-full mt-3 py-2 px-3 bg-pink-600 hover:bg-pink-700 text-white text-sm font-semibold rounded transition"
                  >
                    Apply Filters
                  </button>
                )}
              </div>
              )}

              {/* Advanced Filters Tab */}
              {activeMenu === 'advanced' && (
              <div className="bg-gradient-to-br from-purple-900 to-indigo-900 rounded-lg border border-purple-500 p-4">
                <h3 className="text-sm font-bold text-purple-300 mb-3 uppercase tracking-wider">
                  ✨ Advanced Filters Library
                </h3>
                
                {/* Category Selector */}
                <div className="mb-3">
                  <label className="block text-xs text-purple-200 mb-2 font-semibold">Category</label>
                  <select
                    value={selectedAdvancedCategory}
                    onChange={(e) => changeAdvancedCategory(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-purple-400 rounded text-purple-100 text-sm"
                  >
                    {advancedCategories.map(cat => (
                      <option key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Advanced Filters Grid */}
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {categoryFilters.length > 0 ? (
                    categoryFilters.map((filter) => (
                      <div key={filter.id} className="flex items-center gap-3 bg-slate-800 bg-opacity-50 p-2 rounded border border-purple-400 border-opacity-30 hover:border-opacity-60 transition">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-purple-100">{filter.name}</div>
                          <div className="text-xs text-purple-200 opacity-70">{filter.description}</div>
                        </div>
                        <div className="flex gap-1 items-center">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={advancedFilters[filter.id] || 0}
                            onChange={(e) => {
                              updateAdvancedFilterIntensity(filter.id, parseFloat(e.target.value));
                            }}
                            className="w-24 h-1 accent-purple-400"
                          />
                          <span className="text-xs text-purple-200 w-8 text-right">
                            {Math.round((advancedFilters[filter.id] || 0) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : availableAdvancedFilters.length > 0 ? (
                    availableAdvancedFilters
                      .filter(f => f.category === selectedAdvancedCategory)
                      .map((filter) => (
                        <div key={filter.id} className="flex items-center gap-3 bg-slate-800 bg-opacity-50 p-2 rounded border border-purple-400 border-opacity-30 hover:border-opacity-60 transition">
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-semibold text-purple-100">{filter.name}</div>
                            <div className="text-xs text-purple-200 opacity-70">{filter.description}</div>
                          </div>
                          <div className="flex gap-1 items-center">
                            <input
                              type="range"
                              min="0"
                              max="1"
                              step="0.1"
                              value={advancedFilters[filter.id] || 0}
                              onChange={(e) => {
                                updateAdvancedFilterIntensity(filter.id, parseFloat(e.target.value));
                              }}
                              className="w-24 h-1 accent-purple-400"
                            />
                            <span className="text-xs text-purple-200 w-8 text-right">
                              {Math.round((advancedFilters[filter.id] || 0) * 100)}%
                            </span>
                          </div>
                        </div>
                      ))
                  ) : (
                    <div className="text-xs text-purple-200 opacity-50 p-2">Loading filters for {selectedAdvancedCategory}...</div>
                  )}
                </div>

                {/* Apply All Advanced Filters Button */}
                {Object.keys(advancedFilters).length > 0 && (
                  <button
                    onClick={() => updateAdvancedFilters(Object.keys(advancedFilters))}
                    className="w-full mt-3 py-2 px-3 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold rounded transition"
                  >
                    Apply Advanced Filters
                  </button>
                )}

                {/* Category Info */}
                <div className="mt-3 p-2 bg-purple-900 bg-opacity-30 rounded border border-purple-400 border-opacity-20">
                  <p className="text-xs text-purple-300 opacity-70">
                    Select from {advancedCategories.length} professional filter categories with 20+ premium effects
                  </p>
                </div>
              </div>
              )}

              {/* AI Suggestions */}
              {aiSuggestions.length > 0 && (
                <div className="bg-purple-900 bg-opacity-30 rounded-lg border border-purple-500 border-opacity-50 p-4">
                  <h3 className="text-sm font-bold text-purple-400 mb-2 uppercase tracking-wider flex items-center gap-2">
                    <Zap size={16} />
                    AI Suggestions
                  </h3>
                  <div className="space-y-1">
                    {aiSuggestions.map((suggestion, idx) => (
                      <div
                        key={idx}
                        className="text-xs bg-purple-900 bg-opacity-40 p-2 rounded border-l-2 border-purple-400"
                      >
                        {suggestion}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Settings Panel */}
              <div className="bg-slate-900 rounded-lg border border-slate-700 p-4 flex-1 overflow-y-auto">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="w-full flex items-center justify-between mb-3 hover:text-cyan-400 transition"
                >
                  <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-wider">
                    Settings
                  </h3>
                  <Settings size={18} />
                </button>

                {showSettings && (
                  <div className="space-y-3 text-xs">
                    {/* Beauty Settings */}
                    {activeFilters.includes('beauty') && (
                      <div className="space-y-2 border-t border-slate-700 pt-2">
                        <div className="font-semibold text-cyan-300">
                          Beauty Filter
                        </div>

                        <div>
                          <label className="block text-slate-400 mb-1">
                            Smoothing: {Math.round(
                              beautyConfig.smoothing_strength * 100
                            )}%
                          </label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={beautyConfig.smoothing_strength}
                            onChange={(e) =>
                              updateBeautyConfig({
                                ...beautyConfig,
                                smoothing_strength: parseFloat(e.target.value),
                              })
                            }
                            className="w-full accent-cyan-500"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-400 mb-1">
                            Brightness:{' '}
                            {Math.round(
                              beautyConfig.brightness_adjustment * 100
                            )}%
                          </label>
                          <input
                            type="range"
                            min="-1"
                            max="1"
                            step="0.1"
                            value={beautyConfig.brightness_adjustment}
                            onChange={(e) =>
                              updateBeautyConfig({
                                ...beautyConfig,
                                brightness_adjustment: parseFloat(e.target.value),
                              })
                            }
                            className="w-full accent-cyan-500"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-400 mb-1">
                            Saturation:{' '}
                            {Math.round(
                              beautyConfig.saturation_boost * 100
                            )}%
                          </label>
                          <input
                            type="range"
                            min="-1"
                            max="1"
                            step="0.1"
                            value={beautyConfig.saturation_boost}
                            onChange={(e) =>
                              updateBeautyConfig({
                                ...beautyConfig,
                                saturation_boost: parseFloat(e.target.value),
                              })
                            }
                            className="w-full accent-cyan-500"
                          />
                        </div>

                        <div>
                          <label className="block text-slate-400 mb-1">
                            Lips Intensity:{' '}
                            {Math.round(beautyConfig.lips_intensity * 100)}%
                          </label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={beautyConfig.lips_intensity}
                            onChange={(e) =>
                              updateBeautyConfig({
                                ...beautyConfig,
                                lips_intensity: parseFloat(e.target.value),
                              })
                            }
                            className="w-full accent-cyan-500"
                          />
                        </div>
                      </div>
                    )}

                    {/* Background Settings */}
                    {activeFilters.includes('background') && (
                      <div className="space-y-2 border-t border-slate-700 pt-2">
                        <div className="font-semibold text-cyan-300">
                          Background
                        </div>

                        <div>
                          <label className="block text-slate-400 mb-1">
                            Effect
                          </label>
                          <select
                            value={backgroundConfig.filter_type}
                            onChange={(e) =>
                              updateBackgroundConfig({
                                ...backgroundConfig,
                                filter_type: e.target.value,
                              })
                            }
                            className="w-full bg-slate-800 text-white p-1 rounded border border-slate-600"
                          >
                            <option>blur</option>
                            <option>color</option>
                          </select>
                        </div>

                        {backgroundConfig.filter_type === 'blur' && (
                          <div>
                            <label className="block text-slate-400 mb-1">
                              Blur Strength:{' '}
                              {backgroundConfig.blur_strength}
                            </label>
                            <input
                              type="range"
                              min="1"
                              max="100"
                              step="1"
                              value={backgroundConfig.blur_strength}
                              onChange={(e) =>
                                updateBackgroundConfig({
                                  ...backgroundConfig,
                                  blur_strength: parseInt(e.target.value),
                                })
                              }
                              className="w-full accent-cyan-500"
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Stats */}
              {metrics && metrics.sessions[sessionId] && (
                <div className="bg-slate-900 rounded-lg border border-slate-700 p-4 text-xs">
                  <h3 className="text-sm font-bold text-cyan-400 mb-2 uppercase tracking-wider">
                    Stats
                  </h3>
                  <div className="space-y-1 text-slate-300">
                    <div className="flex justify-between">
                      <span>FPS:</span>
                      <span className="font-mono text-cyan-400">
                        {metrics.sessions[sessionId].fps}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Proc. Time:</span>
                      <span className="font-mono text-cyan-400">
                        {metrics.sessions[sessionId].avg_processing_ms.toFixed(
                          1
                        )}
                        ms
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Frames:</span>
                      <span className="font-mono text-cyan-400">
                        {metrics.sessions[sessionId].total_frames}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIFilterStudio;
