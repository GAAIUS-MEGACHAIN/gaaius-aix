/**
 * Snapchat Lens Studio Clone - React Frontend Component
 * Real-time AR filter processing with live camera feed
 * Production-grade, enterprise-ready React component
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import axios from 'axios';

const LensStudioDashboard = () => {
  // Video and Canvas References
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animationFrameRef = useRef(null);

  // State Management
  const [isStreaming, isStreamingSet] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [availableFilters, setAvailableFilters] = useState([]);
  const [filterIntensity, setFilterIntensity] = useState(0.5);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fps, setFps] = useState(0);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const [beautyConfig, setBeautyConfig] = useState({
    skinSmoothStrength: 0.5,
    brighteningLevel: 0.3,
    contourStrength: 0.4,
    eyeSizeMultiplier: 1.2,
    lipColor: '#FF69B4',
    teethWhitening: 0.5,
    cheekGlow: 0.3,
    faceSlimStrength: 0.3,
  });

  const fpsCounterRef = useRef(0);
  const lastTimeRef = useRef(Date.now());
  const mediaRecorderRef = useRef(null);

  /**
   * Fetch available filters from backend
   */
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const response = await axios.get('/api/lens/available-filters');
        setAvailableFilters(response.data);
      } catch (err) {
        console.error('Error fetching filters:', err);
        setError('Failed to load filters');
      }
    };

    fetchFilters();
  }, []);

  /**
   * Initialize video stream from webcam
   */
  const initializeVideoStream = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: isRecording ? true : false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }

      isStreamingSet(true);

      // Initialize media recorder if recording
      if (isRecording) {
        const canvas = canvasRef.current;
        const canvasStream = canvas.captureStream(30);
        const audioTracks = stream.getAudioTracks();
        if (audioTracks.length > 0) {
          canvasStream.addTrack(audioTracks[0]);
        }

        const mediaRecorder = new MediaRecorder(canvasStream, {
          mimeType: 'video/webm;codecs=vp9',
          videoBitsPerSecond: 2500000,
        });

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            setRecordedChunks((prev) => [...prev, event.data]);
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
      }

      startProcessingFrames();
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Unable to access camera. Please check permissions.');
      isStreamingSet(false);
    }
  }, [isRecording]);

  /**
   * Stop video stream and cleanup
   */
  const stopVideoStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    isStreamingSet(false);
  }, []);

  /**
   * Process video frames with filters in real-time
   */
  const startProcessingFrames = useCallback(async () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');

    if (!canvas || !video || !ctx) return;

    const processFrame = async () => {
      try {
        if (!video.paused && !video.ended) {
          // Draw current video frame
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          // Get image data
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

          // Prepare frame for processing
          const frame = imageData.data;

          if (selectedFilters.length > 0) {
            setIsProcessing(true);

            try {
              // Create FormData for frame
              const formData = new FormData();
              canvas.toBlob((blob) => {
                if (blob) {
                  formData.append('file', blob, 'frame.jpg');
                  formData.append(
                    'filter_config',
                    JSON.stringify({
                      filter_type: selectedFilters[0],
                      intensity: filterIntensity,
                      beauty_config: beautyConfig,
                    })
                  );

                  // Send to backend for processing
                  axios
                    .post('/api/lens/apply-filter', formData, {
                      headers: { 'Content-Type': 'multipart/form-data' },
                    })
                    .then((response) => {
                      if (response.data.image) {
                        // Load processed frame back to canvas
                        const img = new Image();
                        img.onload = () => {
                          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        };
                        img.src = response.data.image;
                      }
                      setIsProcessing(false);
                    })
                    .catch((err) => {
                      console.error('Filter processing error:', err);
                      setIsProcessing(false);
                    });
                }
              }, 'image/jpeg', 0.8);
            } catch (err) {
              console.error('Frame processing error:', err);
              setIsProcessing(false);
            }
          }

          // Update FPS counter
          fpsCounterRef.current++;
          const currentTime = Date.now();
          const elapsed = currentTime - lastTimeRef.current;

          if (elapsed >= 1000) {
            setFps(fpsCounterRef.current);
            fpsCounterRef.current = 0;
            lastTimeRef.current = currentTime;
          }
        }

        animationFrameRef.current = requestAnimationFrame(processFrame);
      } catch (err) {
        console.error('Frame processing error:', err);
        animationFrameRef.current = requestAnimationFrame(processFrame);
      }
    };

    animationFrameRef.current = requestAnimationFrame(processFrame);
  }, [selectedFilters, filterIntensity, beautyConfig]);

  /**
   * Toggle streaming
   */
  const toggleStreaming = async () => {
    if (isStreaming) {
      stopVideoStream();
    } else {
      await initializeVideoStream();
    }
  };

  /**
   * Toggle recording
   */
  const toggleRecording = async () => {
    if (isRecording) {
      setIsRecording(false);

      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();

        mediaRecorderRef.current.onstop = () => {
          const blob = new Blob(recordedChunks, { type: 'video/webm' });
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `lens-studio-${Date.now()}.webm`;
          link.click();
          URL.revokeObjectURL(url);
          setRecordedChunks([]);
        };
      }
    } else {
      setIsRecording(true);
      setRecordedChunks([]);
      if (!isStreaming) {
        await initializeVideoStream();
      }
    }
  };

  /**
   * Add filter to selection
   */
  const addFilter = (filterType) => {
    if (!selectedFilters.includes(filterType)) {
      setSelectedFilters([...selectedFilters, filterType]);
    }
  };

  /**
   * Remove filter from selection
   */
  const removeFilter = (filterType) => {
    setSelectedFilters(selectedFilters.filter((f) => f !== filterType));
  };

  /**
   * Update beauty config
   */
  const updateBeautyConfig = (key, value) => {
    setBeautyConfig((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  /**
   * Capture current frame as image
   */
  const captureFrame = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `lens-studio-capture-${Date.now()}.jpg`;
        link.click();
        URL.revokeObjectURL(url);
      }, 'image/jpeg', 0.95);
    }
  };

  /**
   * Share filtered image to social
   */
  const shareToSocial = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    try {
      const formData = new FormData();
      canvas.toBlob((blob) => {
        if (blob) {
          formData.append('image_data', blob);
          formData.append('filters', selectedFilters.join(','));
          formData.append('caption', 'Check out my Lens Studio filter! 🎬✨');
          formData.append('user_id', localStorage.getItem('user_id') || 'anonymous');

          axios
            .post('/api/lens-studio/social/create-post-with-filter', formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
            })
            .then(() => {
              alert('Posted to social platform! 📱');
            })
            .catch((err) => {
              console.error('Share error:', err);
              alert('Failed to share. Please try again.');
            });
        }
      }, 'image/jpeg', 0.9);
    } catch (err) {
      console.error('Share error:', err);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isStreaming) {
        stopVideoStream();
      }
    };
  }, [isStreaming, stopVideoStream]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">
            🎬 Lens Studio
          </h1>
          <p className="text-purple-300">
            Real-time AR filters & beauty enhancement - Snapchat style
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Canvas - Main */}
          <div className="lg:col-span-2">
            <div className="bg-black/50 rounded-xl overflow-hidden border border-purple-500/30 shadow-2xl">
              {/* Hidden video element */}
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="hidden"
                onLoadedMetadata={() => {
                  if (canvasRef.current && videoRef.current) {
                    canvasRef.current.width = videoRef.current.videoWidth;
                    canvasRef.current.height = videoRef.current.videoHeight;
                  }
                }}
              />

              {/* Canvas for rendering filtered video */}
              <canvas
                ref={canvasRef}
                className="w-full h-auto max-h-[600px]"
                style={{ aspectRatio: '16 / 9' }}
              />

              {/* FPS Counter */}
              <div className="absolute top-4 right-4 bg-black/70 px-3 py-1 rounded text-green-400 font-mono text-sm">
                FPS: {fps}
              </div>

              {/* Processing Indicator */}
              {isProcessing && (
                <div className="absolute top-4 left-4 bg-blue-500/70 px-3 py-1 rounded text-white font-mono text-sm">
                  Processing...
                </div>
              )}
            </div>

            {/* Main Controls */}
            <div className="mt-6 grid grid-cols-2 gap-4">
              {/* Start/Stop Streaming */}
              <button
                onClick={toggleStreaming}
                className={`py-3 px-6 rounded-lg font-bold text-white transition transform hover:scale-105 ${
                  isStreaming
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {isStreaming ? '⏹ Stop Stream' : '▶ Start Stream'}
              </button>

              {/* Recording */}
              <button
                onClick={toggleRecording}
                disabled={!isStreaming}
                className={`py-3 px-6 rounded-lg font-bold text-white transition transform hover:scale-105 ${
                  isRecording
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {isRecording ? '🔴 Stop Recording' : '⭕ Record Video'}
              </button>

              {/* Capture Frame */}
              <button
                onClick={captureFrame}
                disabled={!isStreaming}
                className="py-3 px-6 rounded-lg font-bold text-white bg-blue-600 hover:bg-blue-700 transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                📸 Capture Photo
              </button>

              {/* Share to Social */}
              <button
                onClick={shareToSocial}
                disabled={!isStreaming}
                className="py-3 px-6 rounded-lg font-bold text-white bg-pink-600 hover:bg-pink-700 transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                📤 Share
              </button>
            </div>
          </div>

          {/* Sidebar - Filter Controls */}
          <div className="space-y-6">
            {/* Selected Filters */}
            <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-4">
              <h3 className="text-lg font-bold text-white mb-3">
                ✨ Applied Filters
              </h3>
              {selectedFilters.length === 0 ? (
                <p className="text-gray-400 text-sm">No filters selected</p>
              ) : (
                <div className="space-y-2">
                  {selectedFilters.map((filter) => (
                    <div
                      key={filter}
                      className="flex justify-between items-center bg-purple-600/40 p-2 rounded"
                    >
                      <span className="text-white capitalize">{filter}</span>
                      <button
                        onClick={() => removeFilter(filter)}
                        className="text-red-400 hover:text-red-300 font-bold"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Filter Intensity */}
            <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-4">
              <h3 className="text-white font-bold mb-3">Filter Intensity</h3>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={filterIntensity}
                onChange={(e) => setFilterIntensity(parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-gray-400 text-sm mt-2">
                {Math.round(filterIntensity * 100)}%
              </p>
            </div>

            {/* Beauty Config */}
            {selectedFilters.includes('beauty') && (
              <div className="bg-pink-900/30 border border-pink-500/30 rounded-xl p-4">
                <h3 className="text-white font-bold mb-3">💄 Beauty Settings</h3>

                {/* Skin Smooth */}
                <div className="mb-3">
                  <label className="text-white text-sm">Skin Smoothing</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={beautyConfig.skinSmoothStrength}
                    onChange={(e) =>
                      updateBeautyConfig(
                        'skinSmoothStrength',
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full"
                  />
                </div>

                {/* Brightening */}
                <div className="mb-3">
                  <label className="text-white text-sm">Brightening</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={beautyConfig.brighteningLevel}
                    onChange={(e) =>
                      updateBeautyConfig(
                        'brighteningLevel',
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full"
                  />
                </div>

                {/* Eye Size */}
                <div className="mb-3">
                  <label className="text-white text-sm">Eye Enlargement</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={beautyConfig.eyeSizeMultiplier}
                    onChange={(e) =>
                      updateBeautyConfig(
                        'eyeSizeMultiplier',
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full"
                  />
                </div>

                {/* Lip Color */}
                <div className="mb-3">
                  <label className="text-white text-sm">Lip Color</label>
                  <input
                    type="color"
                    value={beautyConfig.lipColor}
                    onChange={(e) =>
                      updateBeautyConfig('lipColor', e.target.value)
                    }
                    className="w-full h-8 rounded cursor-pointer"
                  />
                </div>

                {/* Teeth Whitening */}
                <div className="mb-3">
                  <label className="text-white text-sm">Teeth Whitening</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={beautyConfig.teethWhitening}
                    onChange={(e) =>
                      updateBeautyConfig(
                        'teethWhitening',
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full"
                  />
                </div>

                {/* Cheek Glow */}
                <div className="mb-3">
                  <label className="text-white text-sm">Cheek Glow</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={beautyConfig.cheekGlow}
                    onChange={(e) =>
                      updateBeautyConfig(
                        'cheekGlow',
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full"
                  />
                </div>
              </div>
            )}

            {/* Available Filters Grid */}
            <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-4">
              <h3 className="text-white font-bold mb-3">🎨 Filters</h3>
              <div className="grid grid-cols-2 gap-2">
                {availableFilters.map((filter) => (
                  <button
                    key={filter.type}
                    onClick={() => addFilter(filter.type)}
                    disabled={selectedFilters.includes(filter.type)}
                    className={`p-2 rounded text-sm font-bold transition ${
                      selectedFilters.includes(filter.type)
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    } disabled:opacity-70`}
                    title={filter.description}
                  >
                    {filter.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer - Stats */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>
            {isStreaming
              ? `✅ Streaming | ${selectedFilters.length} filter(s) active`
              : '⏸ Stream stopped'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LensStudioDashboard;
