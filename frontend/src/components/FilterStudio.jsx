import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import {
  Camera, Video, Download, Share2, Heart, MessageCircle, Settings,
  Play, Pause, Square, RotateCcw, Zap, Layers, Search, Grid, List,
  Loader, CheckCircle, AlertCircle, Volume2, VolumeMute
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// ============ STYLED COMPONENTS ============

const Container = styled.div`
  display: flex;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
`;

const Sidebar = styled.div`
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  overflow-y: auto;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 3px;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const SectionTitle = styled.h3`
  font-size: 12px;
  font-weight: 700;
  color: #999;
  text-transform: uppercase;
  margin: 20px 0 12px 0;
  letter-spacing: 0.5px;
`;

const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
`;

const FilterButton = styled.button`
  padding: 10px;
  background: ${props => props.active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'rgba(102, 126, 234, 0.1)'};
  color: ${props => props.active ? 'white' : '#333'};
  border: 1px solid ${props => props.active ? '#667eea' : 'transparent'};
  border-radius: 8px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-align: center;
  
  &:hover {
    background: ${props => props.active ? '' : 'rgba(102, 126, 234, 0.2)'};
    border-color: #667eea;
  }
`;

const CameraContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
  position: relative;
`;

const CameraPreview = styled.video`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const Canvas = styled.canvas`
  display: none;
`;

const ControlBar = styled.div`
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.8);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  justify-content: center;
  align-items: center;
`;

const ControlButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const RightPanel = styled.div`
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 3px;
  }
`;

const IntensityControl = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
`;

const Label = styled.label`
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-bottom: 6px;
`;

const Slider = styled.input`
  width: 100%;
  cursor: pointer;
`;

const StatsCard = styled.div`
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  margin-bottom: 12px;
`;

const StatValue = styled.div`
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
`;

const StatLabel = styled.div`
  font-size: 11px;
  color: #999;
  margin-top: 4px;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const StatusMessage = styled.div`
  padding: 12px 16px;
  background: ${props => props.error ? '#fee' : '#efe'};
  color: ${props => props.error ? '#c33' : '#3c3'};
  border-radius: 8px;
  font-size: 12px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
`;

const Tab = styled.button`
  padding: 6px 12px;
  background: ${props => props.active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent'};
  color: ${props => props.active ? 'white' : '#999'};
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
`;

// ============ FILTER STUDIO COMPONENT ============

export default function FilterStudio() {
  // State management
  const [filters, setFilters] = useState([]);
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [intensities, setIntensities] = useState({});
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cameraActive, setCameraActive] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [filterCategory, setFilterCategory] = useState('all');
  const [showFreeOnly, setShowFreeOnly] = useState(false);
  const [faceAnalysis, setFaceAnalysis] = useState(null);
  const [rightPanelTab, setRightPanelTab] = useState('controls');
  const [stats, setStats] = useState({ free: 0, premium: 0, total: 0 });

  // Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animationFrameRef = useRef(null);
  const recordingRef = useRef(null);

  // Initialize filters
  useEffect(() => {
    fetchFilters();
  }, []);

  const fetchFilters = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/filters/library`);
      setFilters(response.data);
      
      const statsRes = await axios.get(`${API_BASE_URL}/api/filters/library/stats`);
      setStats({
        free: statsRes.data.free_filters,
        premium: statsRes.data.premium_filters,
        total: statsRes.data.total_filters
      });
      
      setError('');
    } catch (err) {
      setError('Failed to load filters: ' + (err.response?.data?.detail || err.message));
      console.error('Filter loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const initializeCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
        setError('');
        
        // Start real-time frame processing
        processFrames();
      }
    } catch (err) {
      setError('Camera access denied: ' + err.message);
      console.error('Camera error:', err);
    }
  }, []);

  const processFrames = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !cameraActive) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const video = videoRef.current;
    
    // Set canvas size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const processFrame = async () => {
      try {
        // Draw current video frame
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get frame data
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        const base64Data = imageData.split(',')[1];
        
        // Apply filters
        if (selectedFilters.length > 0) {
          const filterIntensities = {};
          selectedFilters.forEach(filterId => {
            filterIntensities[filterId] = intensities[filterId] || 0.7;
          });
          
          const response = await axios.post(`${API_BASE_URL}/api/filters/apply`, {
            frame_data: base64Data,
            filter_ids: selectedFilters,
            intensities: filterIntensities
          });
          
          if (response.data.frame_data) {
            const img = new Image();
            img.onload = () => {
              ctx.drawImage(img, 0, 0);
            };
            img.src = `data:image/jpeg;base64,${response.data.frame_data}`;
          }
        }
        
        // Analyze face every 5 frames
        if (Math.random() < 0.2) {
          const faceRes = await axios.post(`${API_BASE_URL}/api/filters/analyze-face`, {
            frame_data: base64Data
          });
          setFaceAnalysis(faceRes.data);
        }
        
      } catch (err) {
        console.error('Frame processing error:', err);
      }
      
      animationFrameRef.current = requestAnimationFrame(processFrame);
    };
    
    animationFrameRef.current = requestAnimationFrame(processFrame);
  }, [selectedFilters, intensities, cameraActive]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    setCameraActive(false);
  }, []);

  const capturePhoto = useCallback(async () => {
    if (!canvasRef.current) return;
    
    try {
      const canvas = canvasRef.current;
      const imageData = canvas.toDataURL('image/jpeg', 0.9);
      
      // Save media
      await axios.post(`${API_BASE_URL}/api/filters/save-media`, {
        user_id: 'demo_user',
        media_type: 'image',
        filter_ids: selectedFilters,
        media_data: imageData.substring(0, 100)
      });
      
      // Download image
      const link = document.createElement('a');
      link.href = imageData;
      link.download = `filtered_photo_${Date.now()}.jpg`;
      link.click();
      
      setError('');
    } catch (err) {
      setError('Failed to capture photo: ' + err.message);
    }
  }, [selectedFilters]);

  const toggleFilter = (filterId) => {
    setSelectedFilters(prev =>
      prev.includes(filterId)
        ? prev.filter(f => f !== filterId)
        : [...prev, filterId]
    );
    
    if (!intensities[filterId]) {
      setIntensities(prev => ({ ...prev, [filterId]: 0.7 }));
    }
  };

  const updateIntensity = (filterId, value) => {
    setIntensities(prev => ({ ...prev, [filterId]: parseFloat(value) }));
  };

  // Filter list based on selection
  const filteredList = filters.filter(f => {
    if (filterCategory !== 'all' && f.category !== filterCategory) return false;
    if (showFreeOnly && !f.is_free) return false;
    return true;
  });

  return (
    <Container>
      {/* LEFT SIDEBAR - FILTERS */}
      <Sidebar>
        <Logo>
          <Zap size={20} />
          FilterStudio
        </Logo>
        
        <SectionTitle>Filter Library ({stats.total})</SectionTitle>
        <StatusMessage>
          <span>🎁 {stats.free} FREE • 💎 {stats.premium} Premium</span>
        </StatusMessage>
        
        <TabContainer>
          <Tab active={filterCategory === 'all'} onClick={() => setFilterCategory('all')}>All</Tab>
          <Tab active={filterCategory === 'beauty'} onClick={() => setFilterCategory('beauty')}>Beauty</Tab>
          <Tab active={filterCategory === 'ar'} onClick={() => setFilterCategory('ar')}>AR</Tab>
        </TabContainer>
        
        <SectionTitle>Effects ({filteredList.length})</SectionTitle>
        <FilterGrid>
          {loading ? (
            <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '20px' }}>
              <LoadingSpinner>
                <Loader size={20} />
              </LoadingSpinner>
            </div>
          ) : (
            filteredList.map(filter => (
              <FilterButton
                key={filter.filter_id}
                active={selectedFilters.includes(filter.filter_id)}
                onClick={() => toggleFilter(filter.filter_id)}
                title={filter.description}
              >
                {filter.is_free ? '🎁' : '💎'} {filter.name}
              </FilterButton>
            ))
          )}
        </FilterGrid>
      </Sidebar>

      {/* CENTER - CAMERA */}
      <CameraContainer>
        <CameraPreview ref={videoRef} autoPlay playsInline />
        <Canvas ref={canvasRef} />
        
        <ControlBar>
          {!cameraActive ? (
            <ControlButton onClick={initializeCamera} title="Start Camera">
              <Camera size={24} />
            </ControlButton>
          ) : (
            <>
              <ControlButton onClick={stopCamera} title="Stop Camera">
                <RotateCcw size={24} />
              </ControlButton>
              <ControlButton onClick={capturePhoto} title="Capture Photo">
                <Camera size={24} />
              </ControlButton>
            </>
          )}
        </ControlBar>
        
        {error && (
          <StatusMessage error style={{ position: 'absolute', bottom: '80px', left: '16px', right: '16px' }}>
            <AlertCircle size={16} />
            {error}
          </StatusMessage>
        )}
      </CameraContainer>

      {/* RIGHT SIDEBAR - CONTROLS */}
      <RightPanel>
        <TabContainer>
          <Tab active={rightPanelTab === 'controls'} onClick={() => setRightPanelTab('controls')}>
            Settings
          </Tab>
          <Tab active={rightPanelTab === 'analysis'} onClick={() => setRightPanelTab('analysis')}>
            Analysis
          </Tab>
        </TabContainer>
        
        {rightPanelTab === 'controls' && (
          <div style={{ padding: '16px' }}>
            <SectionTitle>Filter Intensity</SectionTitle>
            {selectedFilters.length === 0 ? (
              <StatusMessage>Select filters to adjust</StatusMessage>
            ) : (
              selectedFilters.map(filterId => (
                <IntensityControl key={filterId}>
                  <Label>
                    {filters.find(f => f.filter_id === filterId)?.name || filterId}
                  </Label>
                  <Slider
                    type="range"
                    min={filters.find(f => f.filter_id === filterId)?.intensity_range[0] || 0}
                    max={filters.find(f => f.filter_id === filterId)?.intensity_range[1] || 1}
                    step="0.1"
                    value={intensities[filterId] || 0.7}
                    onChange={(e) => updateIntensity(filterId, e.target.value)}
                  />
                  <div style={{ fontSize: '11px', color: '#999', marginTop: '4px' }}>
                    {(intensities[filterId] || 0.7).toFixed(2)}
                  </div>
                </IntensityControl>
              ))
            )}
          </div>
        )}
        
        {rightPanelTab === 'analysis' && (
          <div style={{ padding: '16px' }}>
            <SectionTitle>Face Analysis</SectionTitle>
            {faceAnalysis ? (
              <>
                <StatsCard>
                  <StatValue>{faceAnalysis.faces_detected}</StatValue>
                  <StatLabel>Faces Detected</StatLabel>
                </StatsCard>
                
                {faceAnalysis.smile && (
                  <StatsCard>
                    <StatValue>
                      {faceAnalysis.smile.has_smile ? '😊' : '😐'}
                    </StatValue>
                    <StatLabel>Smile: {faceAnalysis.smile.smiles_detected} detected</StatLabel>
                  </StatsCard>
                )}
                
                {faceAnalysis.eyes && (
                  <StatsCard>
                    <StatValue>
                      {faceAnalysis.eyes.all_eyes_open ? '👀' : '😑'}
                    </StatValue>
                    <StatLabel>Eyes: {faceAnalysis.eyes.eyes_open_count} open</StatLabel>
                  </StatsCard>
                )}
              </>
            ) : (
              <StatusMessage>Point camera at face to analyze</StatusMessage>
            )}
          </div>
        )}
      </RightPanel>
    </Container>
  );
}
