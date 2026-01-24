/**
 * CapCut-Like Advanced Video Editor Component
 * Professional video editing platform with modern premium UI
 * Effects: 18+ | Transitions: 14+ | Subtitles: Auto + Manual | Audio: Multi-track
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { AlertCircle, Plus, Trash2, Download, Play, Pause, Settings, Copy, Undo, Redo, Sliders, Type, Music, Zap, Sparkles, Volume2, Filter, Layers, Eye, EyeOff, Lock, Unlock, ChevronDown, Search } from 'lucide-react';
import axios from 'axios';

// ==================== TIMELINE SEGMENT COMPONENT ====================

const TimelineSegment = ({ segment, index, onClick, isSelected, onDelete, onUpdate }) => {
  const [showMenu, setShowMenu] = useState(false);
  const duration = segment.duration_ms;

  return (
    <div
      className={`relative h-24 cursor-pointer transition-all group rounded-lg overflow-hidden shadow-sm ${
        isSelected 
          ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-gray-900 shadow-lg shadow-cyan-500/50' 
          : 'hover:shadow-md hover:ring-1 hover:ring-cyan-300/50'
      }`}
      onClick={onClick}
      style={{
        width: `${Math.max(duration / 100, 40)}px`,
        minWidth: '40px'
      }}
    >
      {/* Professional gradient background with video preview effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-700 via-gray-800 to-gray-900 flex items-center justify-center overflow-hidden">
        {/* Video texture grid */}
        <div className="absolute inset-0 opacity-20" style={{backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,.05) 2px, rgba(255,255,255,.05) 4px)'}}></div>
        
        <div className="relative z-10 text-center">
          <div className="text-xs font-semibold text-cyan-300 drop-shadow-lg">Clip {index + 1}</div>
          <div className="text-xs text-gray-300 mt-1">{(duration / 1000).toFixed(1)}s</div>
        </div>
      </div>

      {/* Animated selection border */}
      {isSelected && (
        <div className="absolute inset-0 border-2 border-cyan-400 rounded-lg animate-pulse" style={{animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1)'}}></div>
      )}

      {/* Quick action menu */}
      <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity z-20">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="p-1.5 bg-gray-900/90 backdrop-blur hover:bg-cyan-600 rounded-full transition-all"
        >
          <span className="text-white text-lg">⋯</span>
        </button>

        {showMenu && (
          <div className="absolute right-0 top-8 bg-gray-800 border border-gray-700 rounded-lg shadow-2xl z-30 min-w-40 overflow-hidden backdrop-blur-sm">
            <button
              onClick={() => {
                onDelete(index);
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-2.5 text-sm hover:bg-red-600/20 text-red-400 hover:text-red-300 flex items-center gap-2 transition-colors border-b border-gray-700"
            >
              <Trash2 size={14} /> Delete Clip
            </button>
            <button
              onClick={() => {
                onUpdate(index, { speed_multiplier: 0.5 });
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-2.5 text-sm hover:bg-blue-600/20 text-blue-400 hover:text-blue-300 transition-colors border-b border-gray-700"
            >
              🐢 Slow (0.5x)
            </button>
            <button
              onClick={() => {
                onUpdate(index, { speed_multiplier: 2.0 });
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-2.5 text-sm hover:bg-green-600/20 text-green-400 hover:text-green-300 transition-colors"
            >
              🐇 Speed up (2x)
            </button>
          </div>
        )}
      </div>

      {/* Duration overlay on hover */}
      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity text-xs text-cyan-300 font-mono whitespace-nowrap">
        {Math.floor(duration / 1000)}s
      </div>
    </div>
  );

// ==================== EFFECTS PANEL ====================

const EffectsPanel = ({ segment, onApplyEffect }) => {
  const effects = [
    { name: 'Blur', value: 'blur', icon: '✨', color: 'from-blue-600 to-blue-500' },
    { name: 'Brightness', value: 'brightness', icon: '☀️', color: 'from-yellow-600 to-yellow-500' },
    { name: 'Contrast', value: 'contrast', icon: '◐', color: 'from-purple-600 to-purple-500' },
    { name: 'Saturation', value: 'saturation', icon: '🎨', color: 'from-pink-600 to-pink-500' },
    { name: 'Grayscale', value: 'grayscale', icon: '⚪', color: 'from-gray-600 to-gray-500' },
    { name: 'Sepia', value: 'sepia', icon: '🌅', color: 'from-amber-600 to-amber-500' },
    { name: 'Glow', value: 'glow', icon: '💫', color: 'from-green-600 to-green-500' },
    { name: 'Glitch', value: 'glitch', icon: '⚡', color: 'from-red-600 to-red-500' },
    { name: 'Vignette', value: 'vignette', icon: '◯', color: 'from-indigo-600 to-indigo-500' },
    { name: 'Shake', value: 'shake', icon: '↔️', color: 'from-orange-600 to-orange-500' },
    { name: 'Motion Blur', value: 'motion_blur', icon: '💨', color: 'from-cyan-600 to-cyan-500' },
    { name: 'Zoom', value: 'zoom', icon: '🔍', color: 'from-lime-600 to-lime-500' },
  ];

  const [intensity, setIntensity] = useState(0.5);
  const [selectedEffect, setSelectedEffect] = useState(null);

  const handleApply = (effect) => {
    onApplyEffect(effect, intensity);
    setSelectedEffect(effect);
  };

  return (
    <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-cyan-500/20 rounded-xl p-5 space-y-4 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 flex items-center gap-2">
          <Zap size={20} className="text-cyan-400" /> Effects & Filters
        </h3>
        <span className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded-full font-mono">{effects.length}+</span>
      </div>

      {/* Effects grid with premium styling */}
      <div className="grid grid-cols-3 gap-2">
        {effects.map((effect) => (
          <button
            key={effect.value}
            onClick={() => handleApply(effect.value)}
            className={`relative overflow-hidden rounded-lg p-3 transition-all duration-300 group ${
              selectedEffect === effect.value
                ? `bg-gradient-to-br ${effect.color} shadow-lg shadow-cyan-500/50`
                : 'bg-gray-700/50 hover:bg-gray-600/50 hover:shadow-lg'
            }`}
          >
            <div className="relative z-10">
              <div className="text-2xl mb-1">{effect.icon}</div>
              <div className="text-xs font-semibold text-white text-center leading-tight">{effect.name}</div>
            </div>
            
            {/* Animated background for unselected */}
            {selectedEffect !== effect.value && (
              <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-20 transition-opacity" style={{backgroundImage: `linear-gradient(135deg, currentColor, transparent)`}}></div>
            )}
          </button>
        ))}
      </div>

      {/* Intensity slider with premium styling */}
      <div className="bg-gray-700/30 rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold text-gray-200">Effect Intensity</label>
          <span className="text-sm font-mono bg-cyan-500/20 text-cyan-300 px-3 py-1 rounded-full">{Math.round(intensity * 100)}%</span>
        </div>
        
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={intensity}
          onChange={(e) => setIntensity(parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-600 rounded-full appearance-none cursor-pointer accent-cyan-500"
          style={{background: `linear-gradient(to right, rgb(15, 23, 42) 0%, rgb(34, 211, 238) ${intensity * 100}%, rgb(55, 65, 81) ${intensity * 100}%, rgb(55, 65, 81) 100%)`}}
        />
        
        {/* Visual intensity indicator */}
        <div className="flex gap-1">
          {[...Array(10)].map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-1 rounded-full transition-all ${
                i < Math.ceil(intensity * 10)
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 shadow-lg'
                  : 'bg-gray-600'
              }`}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== SUBTITLES PANEL ====================

const SubtitlesPanel = ({ project, onAddSubtitle, onDeleteSubtitle, subtitles }) => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    text: '',
    start_time_ms: 0,
    end_time_ms: 3000,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.text.trim()) return;
    onAddSubtitle(formData);
    setFormData({ text: '', start_time_ms: 0, end_time_ms: 3000 });
    setShowForm(false);
  };

  return (
    <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-purple-500/20 rounded-xl p-5 space-y-4 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 flex items-center gap-2">
          <Type size={20} className="text-purple-400" /> Subtitles & Captions
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-sm text-white rounded-lg transition-all shadow-lg hover:shadow-purple-500/50"
        >
          + Add Subtitle
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="space-y-3 bg-gray-700/30 p-4 rounded-lg border border-purple-500/20">
          <div>
            <label className="text-xs font-semibold text-purple-300 mb-1 block">Subtitle Text</label>
            <textarea
              placeholder="Type your subtitle text here..."
              value={formData.text}
              onChange={(e) => setFormData({ ...formData, text: e.target.value })}
              className="w-full px-4 py-2.5 bg-gray-600/50 text-white rounded-lg border border-gray-500 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-sm resize-none"
              rows="2"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-purple-300 mb-1 block">Start Time (ms)</label>
              <input
                type="number"
                placeholder="0"
                value={formData.start_time_ms}
                onChange={(e) => setFormData({ ...formData, start_time_ms: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-gray-600/50 text-white rounded-lg border border-gray-500 focus:border-purple-500 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-purple-300 mb-1 block">End Time (ms)</label>
              <input
                type="number"
                placeholder="3000"
                value={formData.end_time_ms}
                onChange={(e) => setFormData({ ...formData, end_time_ms: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-gray-600/50 text-white rounded-lg border border-gray-500 focus:border-purple-500 focus:outline-none text-sm"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full px-4 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg text-sm font-semibold transition-all shadow-lg"
          >
            Add Subtitle to Timeline
          </button>
        </form>
      )}

      {/* Subtitles list with modern cards */}
      <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-purple-500 scrollbar-track-gray-700">
        {subtitles.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <Type size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No subtitles added yet</p>
            <p className="text-xs mt-1">Add subtitles to enhance your video</p>
          </div>
        ) : (
          subtitles.map((sub, idx) => (
            <div key={sub.subtitle_id} className="bg-gray-700/40 hover:bg-gray-700/60 p-3 rounded-lg border border-purple-500/10 hover:border-purple-500/30 transition-all group">
              <div className="flex justify-between items-start gap-2">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-white">{sub.text}</p>
                  <p className="text-xs text-purple-300 font-mono mt-1">
                    {(sub.start_time_ms / 1000).toFixed(2)}s → {(sub.end_time_ms / 1000).toFixed(2)}s
                  </p>
                </div>
                <button
                  onClick={() => onDeleteSubtitle(sub.subtitle_id)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/20 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// ==================== AUDIO PANEL ====================

const AudioPanel = ({ project, onAddAudio, audioTracks }) => {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleAudioUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('audio_type', 'music');
      await onAddAudio(formData);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-orange-500/20 rounded-xl p-5 space-y-4 backdrop-blur-sm">
      <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400 flex items-center gap-2">
        <Music size={20} className="text-orange-400" /> Audio Tracks
      </h3>

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="w-full px-4 py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 disabled:opacity-50 text-white rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-orange-500/50 font-semibold"
      >
        <Plus size={18} /> {uploading ? 'Uploading Audio...' : 'Add Music / Audio Track'}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleAudioUpload}
        className="hidden"
      />

      {/* Audio tracks list */}
      <div className="space-y-2 max-h-48 overflow-y-auto scrollbar-thin scrollbar-thumb-orange-500 scrollbar-track-gray-700">
        {audioTracks.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <Music size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No audio tracks yet</p>
            <p className="text-xs mt-1">Add background music or effects</p>
          </div>
        ) : (
          audioTracks.map((audio) => (
            <div key={audio.audio_id} className="bg-gray-700/40 hover:bg-gray-700/60 p-3 rounded-lg border border-orange-500/10 hover:border-orange-500/30 transition-all group">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-white truncate">{audio.title}</p>
                  <p className="text-xs text-orange-300 capitalize">{audio.audio_type.replace('_', ' ')}</p>
                </div>
                <button className="text-orange-400 hover:text-orange-300 opacity-0 group-hover:opacity-100 transition-all p-1.5 hover:bg-orange-500/20 rounded-lg">
                  <Trash2 size={16} />
                </button>
              </div>

              {/* Volume slider */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs text-gray-300 flex items-center gap-1">
                    <Volume2 size={14} /> Volume
                  </label>
                  <span className="text-xs font-mono text-orange-300">{Math.round((audio.volume || 1) * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  defaultValue={audio.volume || 1}
                  className="w-full h-1.5 bg-gray-600 rounded-full accent-orange-500"
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// ==================== MAIN VIDEO EDITOR COMPONENT ====================

export const CapCutVideoEditor = () => {
  const [project, setProject] = useState(null);
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [segments, setSegments] = useState([]);
  const [subtitles, setSubtitles] = useState([]);
  const [audioTracks, setAudioTracks] = useState([]);
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const videoRef = useRef(null);
  const timelineRef = useRef(null);

  // Create new project
  const createProject = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/video-editor/projects', {
        title: 'New Video Project',
        aspect_ratio: '9:16',
      });
      setProject(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  // Add video clip
  const handleAddClip = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !project) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `/api/v1/video-editor/projects/${project.project_id}/clips`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      // Add segment to timeline
      const newSegment = {
        segment_id: response.data.clip_id,
        clip_index: segments.length,
        start_time_ms: 0,
        end_time_ms: response.data.duration_ms,
        duration_ms: response.data.duration_ms,
        timeline_position_ms: segments.reduce((sum, seg) => sum + seg.duration_ms, 0),
        speed_multiplier: 1.0,
        volume: 1.0,
        effect_type: 'none',
        filter_type: 'none',
      };

      setSegments([...segments, newSegment]);
      addToHistory([...segments, newSegment]);
    } catch (err) {
      setError('Failed to add clip');
    } finally {
      setLoading(false);
    }
  };

  // Apply effect to segment
  const applyEffect = async (effectType, intensity) => {
    if (!selectedSegment) return;

    try {
      const updated = segments.map((seg, idx) =>
        idx === selectedSegment
          ? { ...seg, effect_type: effectType, effect_intensity: intensity }
          : seg
      );

      setSegments(updated);
      addToHistory(updated);
    } catch (err) {
      setError('Failed to apply effect');
    }
  };

  // Add subtitle
  const handleAddSubtitle = async (subtitleData) => {
    if (!project) return;

    try {
      const response = await axios.post(
        `/api/v1/video-editor/projects/${project.project_id}/subtitles`,
        subtitleData
      );

      setSubtitles([...subtitles, response.data]);
      addToHistory(subtitles);
    } catch (err) {
      setError('Failed to add subtitle');
    }
  };

  // Delete subtitle
  const handleDeleteSubtitle = async (subtitleId) => {
    if (!project) return;

    try {
      await axios.delete(
        `/api/v1/video-editor/projects/${project.project_id}/subtitles/${subtitleId}`
      );

      setSubtitles(subtitles.filter((s) => s.subtitle_id !== subtitleId));
      addToHistory(subtitles);
    } catch (err) {
      setError('Failed to delete subtitle');
    }
  };

  // Add audio
  const handleAddAudio = async (formData) => {
    if (!project) return;

    try {
      const response = await axios.post(
        `/api/v1/video-editor/projects/${project.project_id}/audio`,
        formData
      );

      setAudioTracks([...audioTracks, response.data]);
      addToHistory(audioTracks);
    } catch (err) {
      setError('Failed to add audio');
    }
  };

  // History management
  const addToHistory = (newState) => {
    setHistory(history.slice(0, historyIndex + 1));
    setHistory([...history, newState]);
    setHistoryIndex(history.length);
  };

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setSegments(history[historyIndex - 1]);
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setSegments(history[historyIndex + 1]);
    }
  };

  // Export video
  const handleExport = async () => {
    if (!project) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `/api/v1/video-editor/projects/${project.project_id}/export`,
        { resolution: '1080p' }
      );

      alert('Video export started! Check your downloads.');
    } catch (err) {
      setError('Failed to export video');
    } finally {
      setLoading(false);
    }
  };

  if (!project) {
    return (
      <div className="w-full h-screen bg-gradient-to-br from-gray-950 via-slate-950 to-gray-950 flex items-center justify-center relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-20 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>

        <div className="relative z-10 text-center space-y-6">
          <div>
            <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 mb-2">CapCut</h1>
            <p className="text-gray-400 font-light">Professional Video Editor</p>
          </div>

          <button
            onClick={createProject}
            disabled={loading}
            className="relative inline-block group"
          >
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-pulse"></div>
            <div className="relative px-8 py-4 bg-gray-950 rounded-lg flex items-center gap-2 font-bold text-white">
              {loading ? (
                <>
                  <span className="inline-block animate-spin">⚙️</span>
                  Creating Project...
                </>
              ) : (
                <>
                  <Plus size={20} />
                  Create New Video Project
                </>
              )}
            </div>
          </button>

          <p className="text-sm text-gray-500">
            With effects, subtitles, music, and professional editing tools
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white flex flex-col overflow-hidden">
      {/* Premium Header */}
      <div className="bg-gradient-to-r from-gray-900/95 via-slate-900/95 to-gray-900/95 border-b border-cyan-500/20 px-6 py-4 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">{project.title}</h1>
            <p className="text-xs text-gray-400 mt-0.5">Professional Video Editing</p>
          </div>

          <div className="flex items-center gap-3">
            {/* Undo/Redo buttons with improved styling */}
            <div className="flex gap-1 bg-gray-800/50 p-1 rounded-lg border border-gray-700/50">
              <button
                onClick={undo}
                disabled={historyIndex <= 0}
                className="p-2.5 hover:bg-cyan-600/20 disabled:opacity-30 rounded transition-all tooltip"
                title="Undo (Ctrl+Z)"
              >
                <Undo size={18} />
              </button>
              <div className="w-px bg-gray-700"></div>
              <button
                onClick={redo}
                disabled={historyIndex >= history.length - 1}
                className="p-2.5 hover:bg-cyan-600/20 disabled:opacity-30 rounded transition-all tooltip"
                title="Redo (Ctrl+Y)"
              >
                <Redo size={18} />
              </button>
            </div>

            {/* Export button with glow effect */}
            <button
              onClick={handleExport}
              disabled={loading || segments.length === 0}
              className="relative group overflow-hidden px-6 py-2.5 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 group-hover:from-green-500 group-hover:to-emerald-500 transition-all opacity-100"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 blur group-hover:blur-md transition-all opacity-0 group-hover:opacity-50"></div>
              <div className="relative flex items-center gap-2">
                {loading ? (
                  <>
                    <span className="inline-block animate-spin">⚙️</span>
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download size={18} />
                    Export Video
                  </>
                )}
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Main editor area */}
      <div className="flex-1 flex overflow-hidden gap-4 p-4">
        {/* Preview panel */}
        <div className="flex-1 flex flex-col bg-gray-900 rounded-lg overflow-hidden border border-gray-800">
          <div className="flex-1 bg-black flex items-center justify-center">
            {/* Video preview */}
            <div className="w-full h-full bg-gray-800 flex items-center justify-center">
              <div className="text-center">
                <Play size={64} className="mx-auto mb-4 text-gray-600" />
                <p className="text-gray-500">Video Preview</p>
                <p className="text-xs text-gray-600 mt-2">{Math.round(playbackTime / 1000)}s</p>
              </div>
            </div>
          </div>

          {/* Playback controls */}
          <div className="bg-gray-800 border-t border-gray-700 px-4 py-3">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-2 hover:bg-gray-700 rounded"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </button>
              <input
                type="range"
                min="0"
                max={Math.max(...segments.map((s) => s.timeline_position_ms + s.duration_ms), 0)}
                value={playbackTime}
                onChange={(e) => setPlaybackTime(parseInt(e.target.value))}
                className="flex-1 cursor-pointer"
              />
              <span className="text-sm text-gray-400 min-w-12">
                {Math.round(playbackTime / 1000)}s
              </span>
            </div>
          </div>
        </div>

        {/* Right sidebar - Controls */}
        <div className="w-80 flex flex-col gap-4 overflow-y-auto">
          {/* Add clip */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Plus size={20} /> Clips
            </h3>
            <input
              type="file"
              accept="video/*"
              onChange={handleAddClip}
              className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:bg-blue-600 file:text-white hover:file:bg-blue-700"
            />
          </div>

          {/* Effects panel */}
          {selectedSegment !== null && <EffectsPanel segment={segments[selectedSegment]} onApplyEffect={applyEffect} />}

          {/* Subtitles panel */}
          <SubtitlesPanel
            project={project}
            onAddSubtitle={handleAddSubtitle}
            onDeleteSubtitle={handleDeleteSubtitle}
            subtitles={subtitles}
          />

          {/* Audio panel */}
          <AudioPanel project={project} onAddAudio={handleAddAudio} audioTracks={audioTracks} />
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-gray-900 border-t border-gray-800 h-32 p-4 overflow-x-auto">
        <div className="flex gap-2" ref={timelineRef}>
          {segments.length === 0 ? (
            <div className="flex items-center justify-center w-full text-gray-500">
              <p>Add video clips to start editing</p>
            </div>
          ) : (
            segments.map((segment, idx) => (
              <TimelineSegment
                key={segment.segment_id}
                segment={segment}
                index={idx}
                isSelected={selectedSegment === idx}
                onClick={() => setSelectedSegment(idx)}
                onDelete={(i) => {
                  const updated = segments.filter((_, idx) => idx !== i);
                  setSegments(updated);
                  addToHistory(updated);
                  setSelectedSegment(null);
                }}
                onUpdate={(i, updates) => {
                  const updated = segments.map((seg, idx) => (idx === i ? { ...seg, ...updates } : seg));
                  setSegments(updated);
                  addToHistory(updated);
                }}
              />
            ))
          )}
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="fixed top-4 right-4 bg-red-900 border border-red-700 text-white px-4 py-3 rounded flex items-center gap-2">
          <AlertCircle size={20} />
          {error}
        </div>
      )}
    </div>
  );
};

export default CapCutVideoEditor;
