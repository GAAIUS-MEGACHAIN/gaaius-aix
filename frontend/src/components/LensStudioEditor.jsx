/**
 * Lens Studio Editor Component
 * Production-grade real-time camera filter application
 * Real-time WebSocket streaming with live preview
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Camera, Download, Share2, RotateCcw, Play, Pause, Settings } from 'lucide-react';

const LensStudioEditor = ({ userId = 'user123' }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const recordedChunksRef = useRef([]);

  const [isRecording, setIsRecording] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [availableFilters, setAvailableFilters] = useState([]);
  const [filterIntensities, setFilterIntensities] = useState({});
  const [frameCount, setFrameCount] = useState(0);
  const [fps, setFps] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const initializeWebSocket = async () => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/api/lens-studio/ws/live-filter/${userId}`);

        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          setError(null);
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          setError('Connection error. Real-time filters may not work.');
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          if (data.type === 'processed_frame') {
            // Render processed frame to canvas
            renderProcessedFrame(data.frame, data.metadata);
          } else if (data.type === 'pong') {
            // Keep-alive response
            console.log('Pong received');
          }
        };

        wsRef.current = ws;
      } catch (e) {
        console.error('Failed to initialize WebSocket:', e);
        setError('Failed to establish real-time connection');
      }
    };

    initializeWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Fetch available filters
  useEffect(() => {
    fetchAvailableFilters();
  }, []);

  const fetchAvailableFilters = async () => {
    try {
      const response = await fetch('/api/lens-studio/filters/free');
      const data = await response.json();

      if (data.success) {
        setAvailableFilters(data.filters);

        // Initialize intensities
        const intensities = {};
        data.filters.forEach((filter) => {
          intensities[filter.filter_id] = filter.intensity;
        });
        setFilterIntensities(intensities);
      }
    } catch (e) {
      console.error('Failed to fetch filters:', e);
      setError('Failed to load filters');
    }
  };

  // Start camera capture
  const startCamera = async () => {
    try {
      setLoading(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: false
      });

      mediaStreamRef.current = stream;
      videoRef.current.srcObject = stream;
      setIsCameraActive(true);
      setError(null);

      // Start frame processing loop
      processFramesLoop();
    } catch (e) {
      console.error('Failed to start camera:', e);
      setError('Could not access camera. Please check permissions.');
    } finally {
      setLoading(false);
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    setIsCameraActive(false);
    setIsRecording(false);
  };

  // Process frames in loop
  const processFramesLoop = useCallback(() => {
    if (!isCameraActive || !videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const video = videoRef.current;

    // Set canvas dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const frameData = canvas.toDataURL('image/jpeg').split(',')[1];

    // Send to WebSocket for processing
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'frame',
          frame: frameData,
          filters: selectedFilters
        })
      );
    }

    // Update FPS counter
    setFrameCount((prev) => {
      const count = prev + 1;
      if (count % 30 === 0) {
        setFps(Math.round(1000 / 33)); // Approximate FPS
      }
      return count;
    });

    // Continue loop
    requestAnimationFrame(processFramesLoop);
  }, [isCameraActive, selectedFilters]);

  // Render processed frame from WebSocket
  const renderProcessedFrame = (frameData, metadata) => {
    if (!canvasRef.current) return;

    try {
      const img = new Image();
      img.onload = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
      img.src = `data:image/jpeg;base64,${frameData}`;
    } catch (e) {
      console.error('Failed to render processed frame:', e);
    }
  };

  // Toggle filter selection
  const toggleFilter = (filterId) => {
    setSelectedFilters((prev) =>
      prev.includes(filterId)
        ? prev.filter((f) => f !== filterId)
        : [...prev, filterId]
    );

    // Track usage
    trackFilterUsage(filterId);
  };

  // Track filter usage for analytics
  const trackFilterUsage = async (filterId) => {
    try {
      await fetch('/api/lens-studio/analytics/filter-usage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filter_id: filterId, user_id: userId })
      });
    } catch (e) {
      console.error('Failed to track filter usage:', e);
    }
  };

  // Update filter intensity
  const updateFilterIntensity = (filterId, intensity) => {
    setFilterIntensities((prev) => ({
      ...prev,
      [filterId]: intensity
    }));
  };

  // Capture screenshot
  const captureScreenshot = () => {
    if (!canvasRef.current) return;

    const link = document.createElement('a');
    link.href = canvasRef.current.toDataURL('image/png');
    link.download = `lens-studio-${Date.now()}.png`;
    link.click();
  };

  // Start recording
  const startRecording = () => {
    if (!canvasRef.current) return;

    recordedChunksRef.current = [];
    const stream = canvasRef.current.captureStream(30);

    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'video/webm;codecs=vp9'
    });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `lens-studio-${Date.now()}.webm`;
      link.click();
      setIsRecording(false);
    };

    mediaRecorder.start();
    setIsRecording(true);

    // Store recorder for later stop
    window.currentMediaRecorder = mediaRecorder;
  };

  const stopRecording = () => {
    if (window.currentMediaRecorder) {
      window.currentMediaRecorder.stop();
    }
  };

  // Share to social
  const shareToSocial = async () => {
    if (!canvasRef.current) return;

    try {
      setLoading(true);
      const canvas = canvasRef.current;

      canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('image_data', blob, 'filtered_image.jpg');
        formData.append('filters', selectedFilters.join(','));
        formData.append('caption', 'Just took this with Lens Studio! #AR #Filters');
        formData.append('user_id', userId);

        const response = await fetch('/api/lens-studio/social/create-post-with-filter', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();

        if (data.success) {
          alert('📱 Shared to social feed!');
        }
      }, 'image/jpeg');
    } catch (e) {
      console.error('Failed to share:', e);
      setError('Failed to share post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-800 to-red-700">
      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">🎬 Lens Studio</h1>
          <p className="text-pink-200">Enterprise-Grade Real-Time AR Filters</p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500 text-white p-4 rounded-lg mb-6">
            ⚠️ {error}
          </div>
        )}

        {/* Camera Canvas Container */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Camera/Canvas Area */}
          <div className="lg:col-span-2">
            <div className="relative bg-black rounded-lg overflow-hidden aspect-video shadow-2xl border-4 border-pink-500">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="hidden w-full h-full object-cover"
                style={{ transform: 'scaleX(-1)' }}
              />
              <canvas
                ref={canvasRef}
                className="w-full h-full object-cover"
                style={{ transform: 'scaleX(-1)' }}
              />

              {!isCameraActive && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                  <div className="text-center">
                    <Camera className="w-20 h-20 text-pink-400 mx-auto mb-4" />
                    <p className="text-white text-lg">Camera not active</p>
                  </div>
                </div>
              )}

              {/* FPS Counter */}
              {isCameraActive && (
                <div className="absolute top-4 right-4 bg-black/70 text-green-400 px-3 py-1 rounded text-sm font-mono">
                  {fps} FPS
                </div>
              )}

              {/* Recording Indicator */}
              {isRecording && (
                <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded">
                  <div className="w-3 h-3 bg-red-300 rounded-full animate-pulse" />
                  Recording
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="flex gap-3 mt-4 flex-wrap">
              <button
                onClick={isCameraActive ? stopCamera : startCamera}
                disabled={loading}
                className="flex items-center gap-2 bg-pink-500 hover:bg-pink-600 text-white px-6 py-3 rounded-lg font-bold transition disabled:opacity-50"
              >
                <Camera className="w-5 h-5" />
                {isCameraActive ? 'Stop Camera' : 'Start Camera'}
              </button>

              {isCameraActive && (
                <>
                  <button
                    onClick={captureScreenshot}
                    className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-bold transition"
                  >
                    <Download className="w-5 h-5" />
                    Screenshot
                  </button>

                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-bold transition"
                  >
                    {isRecording ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                  </button>

                  <button
                    onClick={shareToSocial}
                    disabled={loading}
                    className="flex items-center gap-2 bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-lg font-bold transition disabled:opacity-50"
                  >
                    <Share2 className="w-5 h-5" />
                    Share
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Sidebar - Filter Selection */}
          <div className="bg-white/10 backdrop-blur rounded-lg p-6 border border-pink-400">
            <h2 className="text-2xl font-bold text-white mb-4">Filters ({selectedFilters.length})</h2>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {availableFilters.map((filter) => (
                <div
                  key={filter.filter_id}
                  className="bg-white/10 p-3 rounded-lg border border-pink-300/50 hover:border-pink-400 transition cursor-pointer"
                  onClick={() => toggleFilter(filter.filter_id)}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <input
                      type="checkbox"
                      checked={selectedFilters.includes(filter.filter_id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        toggleFilter(filter.filter_id);
                      }}
                      className="w-4 h-4 cursor-pointer"
                    />
                    <div className="flex-1">
                      <p className="text-white font-semibold">{filter.name}</p>
                      <p className="text-xs text-pink-200">{filter.type}</p>
                    </div>
                  </div>

                  {selectedFilters.includes(filter.filter_id) && (
                    <div className="mt-2">
                      <label className="text-xs text-gray-300 block mb-1">
                        Intensity: {Math.round(filterIntensities[filter.filter_id] * 100)}%
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={filterIntensities[filter.filter_id]}
                        onChange={(e) => updateFilterIntensity(filter.filter_id, parseFloat(e.target.value))}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full h-2 bg-pink-600 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {selectedFilters.length === 0 && (
              <p className="text-gray-300 text-center py-8">Select filters to apply</p>
            )}
          </div>
        </div>

        {/* Filter Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['Beauty', 'Face Shape', 'Makeup', 'Artistic'].map((category, idx) => (
            <div key={idx} className="bg-white/5 backdrop-blur border border-pink-300/30 rounded-lg p-4 text-center hover:border-pink-400 transition">
              <p className="text-pink-200 font-semibold">{category}</p>
              <p className="text-gray-300 text-sm mt-1">
                {availableFilters.filter((f) => f.type.includes(category.toLowerCase())).length} filters
              </p>
            </div>
          ))}
        </div>

        {/* Stats */}
        {isCameraActive && (
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div className="bg-white/10 backdrop-blur rounded-lg p-4 border border-pink-400">
              <p className="text-2xl font-bold text-pink-300">{selectedFilters.length}</p>
              <p className="text-gray-300 text-sm">Active Filters</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4 border border-pink-400">
              <p className="text-2xl font-bold text-pink-300">{fps}</p>
              <p className="text-gray-300 text-sm">Frames/Second</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4 border border-pink-400">
              <p className="text-2xl font-bold text-pink-300">Live</p>
              <p className="text-gray-300 text-sm">Processing</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LensStudioEditor;
