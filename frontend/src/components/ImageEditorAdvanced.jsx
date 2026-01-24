import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import {
  Layers, Trash2, Copy, Eye, EyeOff, Lock, Unlock, Plus, ChevronDown,
  Pipette, Square, Circle, Type, Hand, ZoomIn, ZoomOut, RotateCw,
  RotateCcw, Maximize, Minimize, Save, Download, Upload, Undo, Redo,
  Sliders, Brightness, Contrast, Saturate, Blur, Droplet, Paintbrush,
  Grid3X3, AlignCenter, Crop, Eraser, Pencil, Filter, Settings,
  Brain, Loader, AlertCircle, CheckCircle
} from 'lucide-react';
import ReplicateAI, { FREE_MODELS } from '@/services/ReplicateAI';

// ============ STYLED COMPONENTS ============

const EditorContainer = styled.div`
  display: flex;
  width: 100%;
  height: calc(100vh - 100px);
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  font-family: 'Manrope', sans-serif;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
`;

const ToolPanel = styled.div`
  width: 80px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  backdrop-filter: blur(10px);
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(244, 114, 182, 0.5);
    border-radius: 3px;
    &:hover {
      background: rgba(244, 114, 182, 0.8);
    }
  }
`;

const ToolButton = styled.button`
  width: 56px;
  height: 56px;
  background: ${props => props.active ? 'linear-gradient(135deg, #f472b6, #ec4899)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.active ? '#f472b6' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 8px;
  color: ${props => props.active ? '#fff' : '#94a3b8'};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &:hover {
    background: ${props => props.active ? 'linear-gradient(135deg, #f472b6, #ec4899)' : 'rgba(255, 255, 255, 0.1)'};
    border-color: #f472b6;
    color: #f472b6;
    transform: translateY(-2px);
  }

  &:active {
    transform: scale(0.95);
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

const ToolTip = styled.div`
  position: absolute;
  left: 70px;
  background: rgba(0, 0, 0, 0.9);
  color: #e2e8f0;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 1000;

  ${ToolButton}:hover & {
    opacity: 1;
  }
`;

const Canvas = styled.canvas`
  flex: 1;
  background: #0a0f1a;
  border: 2px solid rgba(244, 114, 182, 0.2);
  border-radius: 12px;
  cursor: ${props => props.cursor || 'default'};
  image-rendering: crisp-edges;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 320px;
`;

const Panel = styled.div`
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(10px);
  overflow-y: auto;
  max-height: 45%;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(244, 114, 182, 0.5);
    border-radius: 3px;
  }
`;

const PanelTitle = styled.h3`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #f472b6;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// AI Panel Styled Components
const AIPanel = styled.div`
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
  max-height: 400px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(167, 139, 250, 0.5);
    border-radius: 3px;
  }
`;

const AIButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(139, 92, 246, 0.2));
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #e0e7ff;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.35), rgba(139, 92, 246, 0.35));
    border-color: rgba(167, 139, 250, 0.6);
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(167, 139, 250, 0.2);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const APIKeyInput = styled.input`
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  color: #e2e8f0;
  font-size: 12px;
  margin-bottom: 8px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: rgba(167, 139, 250, 0.6);
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 12px rgba(167, 139, 250, 0.2);
  }

  &::placeholder {
    color: #64748b;
  }
`;

const LoadingBar = styled.div`
  width: 100%;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;

  &::after {
    content: '';
    display: block;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.8), transparent);
    animation: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
`;

const StatusMessage = styled.div`
  padding: 8px;
  border-radius: 6px;
  font-size: 11px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: ${props => props.type === 'success' ? 'rgba(34, 197, 94, 0.1)' : 
                          props.type === 'error' ? 'rgba(239, 68, 68, 0.1)' : 
                          'rgba(59, 130, 246, 0.1)'};
  color: ${props => props.type === 'success' ? '#86efac' : 
                     props.type === 'error' ? '#fca5a5' : 
                     '#93c5fd'};
  border: 1px solid ${props => props.type === 'success' ? 'rgba(34, 197, 94, 0.3)' : 
                               props.type === 'error' ? 'rgba(239, 68, 68, 0.3)' : 
                               'rgba(59, 130, 246, 0.3)'};

  svg {
    width: 12px;
    height: 12px;
    flex-shrink: 0;
  }
`;

const LayerItem = styled.div`
  background: ${props => props.active ? 'rgba(244, 114, 182, 0.15)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.active ? 'rgba(244, 114, 182, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;

  &:hover {
    background: rgba(244, 114, 182, 0.1);
    border-color: rgba(244, 114, 182, 0.3);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const LayerName = styled.span`
  flex: 1;
  font-size: 13px;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const LayerControls = styled.div`
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;

  ${LayerItem}:hover & {
    opacity: 1;
  }
`;

const IconButton = styled.button`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: rgba(244, 114, 182, 0.1);
    border-color: #f472b6;
    color: #f472b6;
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const Slider = styled.input`
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.1);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f472b6, #ec4899);
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(244, 114, 182, 0.4);
  }

  &::-moz-range-thumb {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f472b6, #ec4899);
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 8px rgba(244, 114, 182, 0.4);
  }
`;

const SliderGroup = styled.div`
  margin-bottom: 16px;
`;

const SliderLabel = styled.label`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #cbd5e1;
  margin-bottom: 6px;

  span:last-child {
    background: rgba(244, 114, 182, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    color: #f472b6;
    font-weight: 600;
  }
`;

const ColorPicker = styled.input`
  width: 100%;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  background: transparent;
`;

const TopBar = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(15, 23, 42, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 16px;
  z-index: 100;
`;

const TopBarButton = styled.button`
  background: ${props => props.primary ? 'linear-gradient(135deg, #f472b6, #ec4899)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.primary ? '#f472b6' : 'rgba(255, 255, 255, 0.1)'};
  color: ${props => props.primary ? '#fff' : '#e2e8f0'};
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.primary ? 'linear-gradient(135deg, #ec4899, #db2777)' : 'rgba(255, 255, 255, 0.1)'};
    border-color: #f472b6;
    transform: translateY(-1px);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const ZoomLevel = styled.span`
  font-size: 12px;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 8px;
  border-radius: 4px;
  min-width: 50px;
  text-align: center;
`;

const Separator = styled.div`
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
`;

const BrushSizePreview = styled.div`
  width: ${props => props.size}px;
  height: ${props => props.size}px;
  background: ${props => props.color};
  border-radius: 50%;
  margin: 8px auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  opacity: 0.7;
`;

// ============ IMAGE EDITOR COMPONENT ============

const ImageEditorAdvanced = () => {
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const [image, setImage] = useState(null);
  const [activeTool, setActiveTool] = useState('select');
  const [layers, setLayers] = useState([]);
  const [activeLayerId, setActiveLayerId] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [offsetX, setOffsetX] = useState(0);
  const [offsetY, setOffsetY] = useState(0);
  const [isDrawing, setIsDrawing] = useState(false);
  const [lastX, setLastX] = useState(0);
  const [lastY, setLastY] = useState(0);
  const [history, setHistory] = useState([]);
  const [historyStep, setHistoryStep] = useState(-1);
  
  // Tool properties
  const [brushColor, setBrushColor] = useState('#f472b6');
  const [brushSize, setBrushSize] = useState(10);
  const [opacity, setOpacity] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [saturation, setSaturation] = useState(100);
  const [blur, setBlur] = useState(0);

  // AI State
  const [aiService] = useState(new ReplicateAI());
  const [apiKey, setApiKey] = useState(process.env.REACT_APP_REPLICATE_API_KEY || '');
  const [aiProcessing, setAiProcessing] = useState(false);
  const [aiStatus, setAiStatus] = useState({ type: null, message: '' });
  const [showAIPanel, setShowAIPanel] = useState(false);

  // Canvas and context
  let ctx = null;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      ctx = canvas.getContext('2d', { willReadFrequently: true });
      redrawCanvas();
    }
  }, [image, layers, zoom, offsetX, offsetY, brightness, contrast, saturation, blur, rotation]);

  // Upload image
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          setImage(img);
          const newLayer = {
            id: Date.now(),
            name: 'Background',
            image: img,
            visible: true,
            locked: false,
            opacity: 100,
            blendMode: 'normal'
          };
          setLayers([newLayer]);
          setActiveLayerId(newLayer.id);
          saveToHistory();
        };
        img.src = event.target.result;
      };
      reader.readAsDataURL(file);
    }
  };

  // Save to history
  const saveToHistory = useCallback(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const imageData = canvas.toDataURL();
      setHistory(prev => [...prev.slice(0, historyStep + 1), imageData]);
      setHistoryStep(prev => prev + 1);
    }
  }, [historyStep]);

  // Undo/Redo
  const handleUndo = () => {
    if (historyStep > 0) {
      setHistoryStep(historyStep - 1);
      restoreFromHistory(historyStep - 1);
    }
  };

  const handleRedo = () => {
    if (historyStep < history.length - 1) {
      setHistoryStep(historyStep + 1);
      restoreFromHistory(historyStep + 1);
    }
  };

  const restoreFromHistory = (step) => {
    if (history[step]) {
      const img = new Image();
      img.onload = () => {
        const canvas = canvasRef.current;
        ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
      };
      img.src = history[step];
    }
  };

  // Redraw canvas
  const redrawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Apply filters
    ctx.filter = `
      brightness(${brightness}%)
      contrast(${contrast}%)
      saturate(${saturation}%)
      blur(${blur}px)
    `;

    // Draw layers
    layers.forEach(layer => {
      if (layer.visible && layer.image) {
        ctx.save();
        ctx.globalAlpha = layer.opacity / 100;
        ctx.globalCompositeOperation = layer.blendMode;

        // Apply zoom and pan
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.scale(zoom, zoom);
        ctx.rotate((rotation * Math.PI) / 180);
        ctx.translate(-layer.image.width / 2 + offsetX, -layer.image.height / 2 + offsetY);

        ctx.drawImage(layer.image, 0, 0);
        ctx.restore();
      }
    });

    ctx.filter = 'none';
  };

  // Canvas drawing
  const handleCanvasMouseDown = (e) => {
    if (!image || activeTool === 'select' || activeTool === 'hand') return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - offsetX * zoom) / zoom;
    const y = (e.clientY - rect.top - offsetY * zoom) / zoom;

    setIsDrawing(true);
    setLastX(x);
    setLastY(y);

    if (activeTool === 'brush') {
      drawBrushStroke(x, y);
    } else if (activeTool === 'eraser') {
      eraseStroke(x, y);
    }
  };

  const handleCanvasMouseMove = (e) => {
    if (!isDrawing || !image) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - offsetX * zoom) / zoom;
    const y = (e.clientY - rect.top - offsetY * zoom) / zoom;

    if (activeTool === 'brush') {
      drawBrushLine(lastX, lastY, x, y);
    } else if (activeTool === 'eraser') {
      eraseLine(lastX, lastY, x, y);
    }

    setLastX(x);
    setLastY(y);
  };

  const handleCanvasMouseUp = () => {
    setIsDrawing(false);
    if (isDrawing && (activeTool === 'brush' || activeTool === 'eraser')) {
      saveToHistory();
    }
  };

  const drawBrushStroke = (x, y) => {
    ctx = canvasRef.current.getContext('2d');
    ctx.beginPath();
    ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
    ctx.fillStyle = brushColor;
    ctx.globalAlpha = opacity / 100;
    ctx.fill();
    ctx.globalAlpha = 1;
  };

  const drawBrushLine = (fromX, fromY, toX, toY) => {
    ctx = canvasRef.current.getContext('2d');
    ctx.strokeStyle = brushColor;
    ctx.lineWidth = brushSize;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = opacity / 100;
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();
    ctx.globalAlpha = 1;
  };

  const eraseStroke = (x, y) => {
    ctx = canvasRef.current.getContext('2d');
    ctx.clearRect(x - brushSize / 2, y - brushSize / 2, brushSize, brushSize);
  };

  const eraseLine = (fromX, fromY, toX, toY) => {
    ctx = canvasRef.current.getContext('2d');
    ctx.clearRect(fromX - brushSize / 2, fromY - brushSize / 2, brushSize, brushSize);
    ctx.clearRect(toX - brushSize / 2, toY - brushSize / 2, brushSize, brushSize);
  };

  // Zoom controls
  const handleZoom = (delta) => {
    const newZoom = Math.max(0.1, Math.min(5, zoom + delta));
    setZoom(newZoom);
  };

  // Layer management
  const addLayer = () => {
    const canvas = document.createElement('canvas');
    canvas.width = image?.width || 800;
    canvas.height = image?.height || 600;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'transparent';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const newLayer = {
      id: Date.now(),
      name: `Layer ${layers.length + 1}`,
      image: canvas,
      visible: true,
      locked: false,
      opacity: 100,
      blendMode: 'normal'
    };

    setLayers([...layers, newLayer]);
    setActiveLayerId(newLayer.id);
  };

  const deleteLayer = (id) => {
    const newLayers = layers.filter(l => l.id !== id);
    setLayers(newLayers);
    if (activeLayerId === id) {
      setActiveLayerId(newLayers[0]?.id || null);
    }
  };

  const toggleLayerVisibility = (id) => {
    setLayers(layers.map(l =>
      l.id === id ? { ...l, visible: !l.visible } : l
    ));
  };

  const toggleLayerLock = (id) => {
    setLayers(layers.map(l =>
      l.id === id ? { ...l, locked: !l.locked } : l
    ));
  };

  // Export
  const handleExport = (format) => {
    const canvas = canvasRef.current;
    const link = document.createElement('a');
    link.href = canvas.toDataURL(`image/${format}`);
    link.download = `edited-image.${format}`;
    link.click();
  };

  // AI Handlers
  const handleAPIKeySubmit = (key) => {
    if (key.trim()) {
      aiService.setApiKey(key);
      setApiKey(key);
      setAiStatus({ type: 'success', message: 'API Key set! Ready to use AI features.' });
      setTimeout(() => setAiStatus({ type: null, message: '' }), 3000);
    }
  };

  const applyAIEffect = async (effectName, handler) => {
    if (!image) {
      setAiStatus({ type: 'error', message: 'Upload an image first' });
      return;
    }
    if (!aiService.isReady()) {
      setAiStatus({ type: 'error', message: 'Add Replicate API key to use AI features' });
      return;
    }

    setAiProcessing(true);
    setAiStatus({ type: null, message: `Processing ${effectName}...` });

    try {
      const canvas = canvasRef.current;
      const imageUrl = canvas.toDataURL('image/png');

      const result = await handler(imageUrl);
      if (result) {
        const resultUrl = Array.isArray(result) ? result[0] : result;
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          const newLayer = {
            id: Date.now(),
            name: `${effectName} Layer`,
            image: img,
            visible: true,
            locked: false,
            opacity: 100,
            blendMode: 'normal'
          };
          setLayers([...layers, newLayer]);
          setActiveLayerId(newLayer.id);
          saveToHistory();
          setAiStatus({ type: 'success', message: `${effectName} applied! Added as new layer.` });
          setTimeout(() => setAiStatus({ type: null, message: '' }), 3000);
        };
        img.onerror = () => setAiStatus({ type: 'error', message: 'Failed to load result' });
        img.src = resultUrl;
      }
    } catch (error) {
      setAiStatus({ type: 'error', message: error.message || `${effectName} failed` });
    } finally {
      setAiProcessing(false);
    }
  };

  const aiEffects = [
    {
      name: 'AI Upscale 4x',
      handler: () => applyAIEffect('Upscale 4x', (url) => aiService.upscaleImage(url))
    },
    {
      name: 'Remove Background',
      handler: () => applyAIEffect('Remove Background', (url) => aiService.removeBackground(url))
    },
    {
      name: 'AI Enhance',
      handler: () => applyAIEffect('Enhance', (url) => aiService.enhanceImage(url))
    },
    {
      name: 'Colorize B&W',
      handler: () => applyAIEffect('Colorize', (url) => aiService.colorizeImage(url))
    },
    {
      name: 'Denoise',
      handler: () => applyAIEffect('Denoise', (url) => aiService.denoiseImage(url, 0.7))
    },
    {
      name: 'Restore Photo',
      handler: () => applyAIEffect('Restore', (url) => aiService.restorePhoto(url))
    },
    {
      name: 'Segment Objects',
      handler: () => applyAIEffect('Segment', (url) => aiService.segmentImage(url))
    },
    {
      name: 'Depth Map',
      handler: () => applyAIEffect('Depth', (url) => aiService.depthMap(url))
    }
  ];

  const tools = [
    { id: 'select', icon: Grid3X3, label: 'Select' },
    { id: 'hand', icon: Hand, label: 'Pan' },
    { id: 'brush', icon: Paintbrush, label: 'Brush' },
    { id: 'eraser', icon: Eraser, label: 'Eraser' },
    { id: 'pencil', icon: Pencil, label: 'Pencil' },
    { id: 'crop', icon: Crop, label: 'Crop' },
    { id: 'color', icon: Pipette, label: 'Color Picker' },
    { id: 'shapes', icon: Square, label: 'Shapes' },
    { id: 'text', icon: Type, label: 'Text' },
    { id: 'filters', icon: Filter, label: 'Filters' },
  ];

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)' }}>
      <TopBar>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>Image Editor Pro</h2>
        
        <Separator />
        
        <TopBarButton onClick={() => fileInputRef.current?.click()}>
          <Upload size={16} /> Open Image
        </TopBarButton>
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ display: 'none' }}
        />

        <TopBarButton onClick={handleUndo} disabled={historyStep <= 0}>
          <Undo size={16} /> Undo
        </TopBarButton>

        <TopBarButton onClick={handleRedo} disabled={historyStep >= history.length - 1}>
          <Redo size={16} /> Redo
        </TopBarButton>

        <Separator />

        <TopBarButton onClick={() => handleZoom(0.2)}>
          <ZoomIn size={16} />
        </TopBarButton>

        <ZoomLevel>{Math.round(zoom * 100)}%</ZoomLevel>

        <TopBarButton onClick={() => handleZoom(-0.2)}>
          <ZoomOut size={16} />
        </TopBarButton>

        <Separator />

        <TopBarButton onClick={() => handleExport('png')} primary>
          <Download size={16} /> PNG
        </TopBarButton>

        <TopBarButton onClick={() => handleExport('jpg')} primary>
          <Download size={16} /> JPG
        </TopBarButton>

        <Separator />

        <TopBarButton onClick={() => setShowAIPanel(!showAIPanel)} style={{ background: 'rgba(167, 139, 250, 0.2)', borderColor: 'rgba(167, 139, 250, 0.5)' }}>
          <Brain size={16} /> AI Tools
        </TopBarButton>
      </TopBar>

      <div style={{ marginTop: '60px', display: 'flex', height: 'calc(100vh - 60px)', gap: '16px', padding: '16px' }}>
        <ToolPanel>
          {tools.map(tool => (
            <div key={tool.id} style={{ position: 'relative' }}>
              <ToolButton
                active={activeTool === tool.id}
                onClick={() => setActiveTool(tool.id)}
              >
                <tool.icon />
                <ToolTip>{tool.label}</ToolTip>
              </ToolButton>
            </div>
          ))}
        </ToolPanel>

        <Canvas
          ref={canvasRef}
          onMouseDown={handleCanvasMouseDown}
          onMouseMove={handleCanvasMouseMove}
          onMouseUp={handleCanvasMouseUp}
          onMouseLeave={handleCanvasMouseUp}
          cursor={activeTool === 'hand' ? 'grab' : activeTool === 'brush' ? 'crosshair' : 'default'}
        />

        <RightPanel>
          <Panel>
            <PanelTitle><Layers size={16} /> Layers</PanelTitle>
            <div>
              {layers.map(layer => (
                <LayerItem
                  key={layer.id}
                  active={activeLayerId === layer.id}
                  onClick={() => setActiveLayerId(layer.id)}
                >
                  <IconButton onClick={() => toggleLayerVisibility(layer.id)} title="Toggle visibility">
                    {layer.visible ? <Eye size={14} /> : <EyeOff size={14} />}
                  </IconButton>
                  <LayerName>{layer.name}</LayerName>
                  <LayerControls>
                    <IconButton onClick={() => toggleLayerLock(layer.id)} title="Lock/Unlock">
                      {layer.locked ? <Lock size={14} /> : <Unlock size={14} />}
                    </IconButton>
                    <IconButton onClick={() => deleteLayer(layer.id)} title="Delete">
                      <Trash2 size={14} />
                    </IconButton>
                  </LayerControls>
                </LayerItem>
              ))}
            </div>
            <TopBarButton onClick={addLayer} style={{ marginTop: '12px', width: '100%' }}>
              <Plus size={14} /> New Layer
            </TopBarButton>
          </Panel>

          <Panel>
            <PanelTitle><Sliders size={16} /> Adjustments</PanelTitle>
            
            <SliderGroup>
              <SliderLabel>
                <span>Brightness</span>
                <span>{brightness}%</span>
              </SliderLabel>
              <Slider
                type="range"
                min="0"
                max="200"
                value={brightness}
                onChange={(e) => setBrightness(Number(e.target.value))}
              />
            </SliderGroup>

            <SliderGroup>
              <SliderLabel>
                <span>Contrast</span>
                <span>{contrast}%</span>
              </SliderLabel>
              <Slider
                type="range"
                min="0"
                max="200"
                value={contrast}
                onChange={(e) => setContrast(Number(e.target.value))}
              />
            </SliderGroup>

            <SliderGroup>
              <SliderLabel>
                <span>Saturation</span>
                <span>{saturation}%</span>
              </SliderLabel>
              <Slider
                type="range"
                min="0"
                max="200"
                value={saturation}
                onChange={(e) => setSaturation(Number(e.target.value))}
              />
            </SliderGroup>

            <SliderGroup>
              <SliderLabel>
                <span>Blur</span>
                <span>{blur}px</span>
              </SliderLabel>
              <Slider
                type="range"
                min="0"
                max="20"
                value={blur}
                onChange={(e) => setBlur(Number(e.target.value))}
              />
            </SliderGroup>

            <SliderGroup>
              <SliderLabel>
                <span>Rotation</span>
                <span>{rotation}°</span>
              </SliderLabel>
              <Slider
                type="range"
                min="0"
                max="360"
                value={rotation}
                onChange={(e) => setRotation(Number(e.target.value))}
              />
            </SliderGroup>
          </Panel>

          <Panel>
            <PanelTitle><Paintbrush size={16} /> Brush Settings</PanelTitle>
            
            <SliderGroup style={{ marginBottom: '12px' }}>
              <SliderLabel>
                <span>Color</span>
              </SliderLabel>
              <ColorPicker
                type="color"
                value={brushColor}
                onChange={(e) => setBrushColor(e.target.value)}
              />
            </SliderGroup>

            <BrushSizePreview size={Math.min(brushSize, 60)} color={brushColor} />

            <SliderGroup>
              <SliderLabel>
                <span>Brush Size</span>
                <span>{brushSize}px</span>
              </SliderLabel>
              <Slider
                type="range"
                min="1"
                max="100"
                value={brushSize}
                onChange={(e) => setBrushSize(Number(e.target.value))}
              />
            </SliderGroup>

            <SliderGroup>
              <SliderLabel>
                <span>Opacity</span>
                <span>{opacity}%</span>
              </SliderLabel>
              <Slider
                type="range"
                min="0"
                max="100"
                value={opacity}
                onChange={(e) => setOpacity(Number(e.target.value))}
              />
            </SliderGroup>
          </Panel>

          {showAIPanel && (
            <AIPanel>
              <PanelTitle style={{ color: '#e0e7ff', marginBottom: '12px' }}><Brain size={16} /> AI Tools</PanelTitle>
              
              {!aiService.isReady() && (
                <>
                  <APIKeyInput
                    type="password"
                    placeholder="Enter Replicate API key..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAPIKeySubmit(apiKey)}
                  />
                  <AIButton onClick={() => handleAPIKeySubmit(apiKey)}>
                    Set API Key
                  </AIButton>
                  <small style={{ color: '#94a3b8', fontSize: '11px', textAlign: 'center', display: 'block', marginBottom: '8px' }}>
                    Get free key at replicate.com
                  </small>
                </>
              )}

              {aiService.isReady() && aiProcessing && (
                <>
                  <LoadingBar />
                  <small style={{ color: '#93c5fd', fontSize: '11px', textAlign: 'center', display: 'block' }}>
                    Processing AI effect... (2-10 seconds)
                  </small>
                </>
              )}

              {aiStatus.message && (
                <StatusMessage type={aiStatus.type}>
                  {aiStatus.type === 'success' && <CheckCircle size={12} />}
                  {aiStatus.type === 'error' && <AlertCircle size={12} />}
                  {aiStatus.type === 'info' && <Loader size={12} />}
                  {aiStatus.message}
                </StatusMessage>
              )}

              {aiService.isReady() && (
                <>
                  {aiEffects.map((effect, idx) => (
                    <AIButton
                      key={idx}
                      onClick={effect.handler}
                      disabled={aiProcessing || !image}
                    >
                      <Brain size={13} />
                      {effect.name}
                    </AIButton>
                  ))}
                </>
              )}
            </AIPanel>
          )}
        </RightPanel>
      </div>
    </div>
  );
};

export default ImageEditorAdvanced;
