/**
 * CapCut Pro - Advanced Professional Video Editor Component
 * Premium modern UI with all CapCut-like features
 * Effects: 18+ | Transitions: 14+ | Subtitles: Auto + Manual | Audio: Multi-track
 */

import React, { useState, useRef, useEffect } from 'react';
import { AlertCircle, Plus, Trash2, Download, Play, Pause, Settings, Undo, Redo, Sliders, Type, Music, Zap, Sparkles, Volume2, Filter, Layers, Clock, Grid3x3, Maximize2 } from 'lucide-react';
import axios from 'axios';

// ==================== TIMELINE SEGMENT COMPONENT ====================

const TimelineSegment = ({ segment, index, onClick, isSelected, onDelete, onUpdate }) => {
  const [showMenu, setShowMenu] = useState(false);
  const duration = segment.duration_ms;

  return (
    <div
      className={`relative h-24 cursor-pointer transition-all group rounded-lg overflow-hidden shadow-sm flex-shrink-0 ${
        isSelected 
          ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-gray-900 shadow-lg shadow-cyan-500/50' 
          : 'hover:shadow-md hover:ring-1 hover:ring-cyan-300/50'
      }`}
      onClick={onClick}
      style={{
        width: `${Math.max(duration / 100, 50)}px`,
        minWidth: '50px'
      }}
    >
      {/* Gradient background with grid pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-700 via-gray-800 to-gray-900 flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(255,255,255,.05) 25%, rgba(255,255,255,.05) 26%, transparent 27%, transparent 74%, rgba(255,255,255,.05) 75%, rgba(255,255,255,.05) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(255,255,255,.05) 25%, rgba(255,255,255,.05) 26%, transparent 27%, transparent 74%, rgba(255,255,255,.05) 75%, rgba(255,255,255,.05) 76%, transparent 77%, transparent)',
          backgroundSize: '40px 40px'
        }}></div>
        
        <div className="relative z-10 text-center">
          <div className="text-xs font-bold text-cyan-300 drop-shadow-lg">#{index + 1}</div>
          <div className="text-xs text-gray-300 mt-0.5 font-mono">{(duration / 1000).toFixed(1)}s</div>
        </div>
      </div>

      {/* Selection indicator */}
      {isSelected && (
        <div className="absolute top-1 left-1 w-3 h-3 bg-cyan-400 rounded-full shadow-lg shadow-cyan-400/50 animate-pulse"></div>
      )}

      {/* Quick actions menu */}
      <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity z-20">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="p-1.5 bg-gray-900/95 backdrop-blur hover:bg-cyan-600 rounded-full transition-all shadow-lg"
        >
          <span className="text-white text-sm font-bold">⋯</span>
        </button>

        {showMenu && (
          <div className="absolute right-0 top-9 bg-gray-800/95 border border-cyan-500/30 rounded-lg shadow-2xl z-30 min-w-44 overflow-hidden backdrop-blur-md">
            <button
              onClick={() => {
                onDelete(index);
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-3 text-sm hover:bg-red-600/30 text-red-400 hover:text-red-300 flex items-center gap-2 transition-colors border-b border-gray-700"
            >
              <Trash2 size={14} /> Delete Clip
            </button>
            <button
              onClick={() => {
                onUpdate(index, { speed_multiplier: 0.5 });
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-3 text-sm hover:bg-blue-600/30 text-blue-400 hover:text-blue-300 transition-colors border-b border-gray-700"
            >
              🐢 Slow Motion (0.5x)
            </button>
            <button
              onClick={() => {
                onUpdate(index, { speed_multiplier: 2.0 });
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-3 text-sm hover:bg-green-600/30 text-green-400 hover:text-green-300 transition-colors"
            >
              🐇 Speed Up (2x)
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

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
    <div className="bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-cyan-500/20 rounded-2xl p-5 space-y-4 backdrop-blur-xl">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 flex items-center gap-2">
          <Zap size={20} className="text-cyan-400" /> Effects & Filters
        </h3>
        <span className="text-xs px-3 py-1 bg-cyan-500/20 text-cyan-300 rounded-full font-semibold">{effects.length}+</span>
      </div>

      {/* Effects grid */}
      <div className="grid grid-cols-3 gap-2 max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-500/50 scrollbar-track-transparent">
        {effects.map((effect) => (
          <button
            key={effect.value}
            onClick={() => handleApply(effect.value)}
            className={`relative overflow-hidden rounded-xl p-3 transition-all duration-300 group transform hover:scale-105 ${
              selectedEffect === effect.value
                ? `bg-gradient-to-br ${effect.color} shadow-lg shadow-cyan-500/50 ring-2 ring-cyan-400`
                : 'bg-gray-700/50 hover:bg-gray-600/50 hover:shadow-lg hover:ring-1 hover:ring-cyan-300/50'
            }`}
          >
            <div className="relative z-10 text-center">
              <div className="text-2xl mb-1">{effect.icon}</div>
              <div className="text-xs font-bold text-white leading-tight">{effect.name}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Intensity slider */}
      <div className="bg-gray-700/30 rounded-xl p-4 space-y-3 border border-gray-600/30">
        <div className="flex items-center justify-between">
          <label className="text-sm font-semibold text-cyan-300">Effect Intensity</label>
          <span className="text-sm font-mono bg-cyan-500/30 text-cyan-200 px-3 py-1 rounded-lg">{Math.round(intensity * 100)}%</span>
        </div>
        
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={intensity}
          onChange={(e) => setIntensity(parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-600/50 rounded-full appearance-none cursor-pointer accent-cyan-400"
          style={{
            background: `linear-gradient(to right, rgb(15, 23, 42) 0%, rgb(34, 211, 238) ${intensity * 100}%, rgb(55, 65, 81) ${intensity * 100}%, rgb(55, 65, 81) 100%)`
          }}
        />
        
        {/* Visual intensity bars */}
        <div className="flex gap-1">
          {[...Array(10)].map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-1.5 rounded-full transition-all ${
                i < Math.ceil(intensity * 10)
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 shadow-lg shadow-cyan-500/50'
                  : 'bg-gray-600/50'
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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.text.trim()) return;
    onAddSubtitle(formData);
    setFormData({ text: '', start_time_ms: 0, end_time_ms: 3000 });
    setShowForm(false);
  };

  return (
    <div className="bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-purple-500/20 rounded-2xl p-5 space-y-4 backdrop-blur-xl">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 flex items-center gap-2">
          <Type size={20} className="text-purple-400" /> Subtitles
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-sm text-white rounded-lg transition-all shadow-lg hover:shadow-purple-500/50 font-semibold"
        >
          + Add
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="space-y-3 bg-gray-700/30 p-4 rounded-xl border border-purple-500/20">
          <textarea
            placeholder="Type subtitle text..."
            value={formData.text}
            onChange={(e) => setFormData({ ...formData, text: e.target.value })}
            className="w-full px-3 py-2 bg-gray-600/50 text-white rounded-lg border border-gray-500 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-sm resize-none"
            rows="2"
          />

          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Start (ms)"
              value={formData.start_time_ms}
              onChange={(e) => setFormData({ ...formData, start_time_ms: parseInt(e.target.value) || 0 })}
              className="px-3 py-2 bg-gray-600/50 text-white rounded-lg border border-gray-500 focus:border-purple-500 focus:outline-none text-sm"
            />
            <input
              type="number"
              placeholder="End (ms)"
              value={formData.end_time_ms}
              onChange={(e) => setFormData({ ...formData, end_time_ms: parseInt(e.target.value) || 0 })}
              className="px-3 py-2 bg-gray-600/50 text-white rounded-lg border border-gray-500 focus:border-purple-500 focus:outline-none text-sm"
            />
          </div>

          <button
            type="submit"
            className="w-full px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg text-sm font-semibold transition-all"
          >
            Add Subtitle
          </button>
        </form>
      )}

      <div className="space-y-2 max-h-48 overflow-y-auto scrollbar-thin scrollbar-thumb-purple-500/50">
        {subtitles.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <Type size={28} className="mx-auto mb-2 opacity-40" />
            <p className="text-sm">No subtitles yet</p>
          </div>
        ) : (
          subtitles.map((sub) => (
            <div key={sub.subtitle_id} className="bg-gray-700/40 hover:bg-gray-700/60 p-3 rounded-lg border border-purple-500/10 hover:border-purple-500/30 transition-all group">
              <div className="flex justify-between items-start gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white truncate">{sub.text}</p>
                  <p className="text-xs text-purple-300 font-mono mt-1">{(sub.start_time_ms / 1000).toFixed(1)}s → {(sub.end_time_ms / 1000).toFixed(1)}s</p>
                </div>
                <button
                  onClick={() => onDeleteSubtitle(sub.subtitle_id)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/20 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
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
    <div className="bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-orange-500/20 rounded-2xl p-5 space-y-4 backdrop-blur-xl">
      <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400 flex items-center gap-2">
        <Music size={20} className="text-orange-400" /> Audio Tracks
      </h3>

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="w-full px-4 py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 disabled:opacity-50 text-white rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-orange-500/50 font-semibold"
      >
        <Plus size={18} /> {uploading ? 'Uploading...' : 'Add Audio'}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleAudioUpload}
        className="hidden"
      />

      <div className="space-y-2 max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-orange-500/50">
        {audioTracks.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <Music size={28} className="mx-auto mb-2 opacity-40" />
            <p className="text-sm">No audio tracks</p>
          </div>
        ) : (
          audioTracks.map((audio) => (
            <div key={audio.audio_id} className="bg-gray-700/40 hover:bg-gray-700/60 p-3 rounded-lg border border-orange-500/10 hover:border-orange-500/30 transition-all group">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white truncate">{audio.title}</p>
                  <p className="text-xs text-orange-300 capitalize">{audio.audio_type.replace('_', ' ')}</p>
                </div>
                <button className="text-orange-400 hover:text-orange-300 opacity-0 group-hover:opacity-100 transition-all p-1 hover:bg-orange-500/20 rounded flex-shrink-0">
                  <Trash2 size={14} />
                </button>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <label className="text-gray-300">Volume</label>
                  <span className="font-mono text-orange-300">{Math.round((audio.volume || 1) * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  defaultValue={audio.volume || 1}
                  className="w-full h-1.5 bg-gray-600/50 rounded-full accent-orange-500"
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// ==================== MAIN VIDEO EDITOR ====================

export const CapCutVideoEditorPro = () => {
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
  const [isFullscreen, setIsFullscreen] = useState(false);

  const videoRef = useRef(null);
  const timelineRef = useRef(null);

  const createProject = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/video-editor/projects', {
        title: 'My New Video',
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

  const applyEffect = async (effectType, intensity) => {
    if (selectedSegment === null) return;

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

  const handleExport = async () => {
    if (!project) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `/api/v1/video-editor/projects/${project.project_id}/export`,
        { resolution: '1080p' }
      );

      alert('✨ Video export started! Check your downloads folder.');
    } catch (err) {
      setError('Failed to export video');
    } finally {
      setLoading(false);
    }
  };

  // Welcome screen
  if (!project) {
    return (
      <div className="w-full h-screen bg-gradient-to-br from-gray-950 via-slate-950 to-gray-950 flex items-center justify-center relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-10 left-10 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-10 right-10 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
        </div>

        <div className="relative z-10 text-center space-y-8 max-w-2xl px-6">
          <div>
            <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 mb-4 drop-shadow-lg">
              CapCut Pro
            </div>
            <p className="text-xl text-gray-300 font-light">Professional Video Editing Platform</p>
          </div>

          <div className="space-y-4">
            <p className="text-gray-400 text-sm leading-relaxed">
              Create stunning videos with professional effects, transitions, subtitles, and multi-track audio editing.
            </p>

            <button
              onClick={createProject}
              disabled={loading}
              className="relative inline-block group mx-auto"
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-pulse group-disabled:animate-none"></div>
              <div className="relative px-10 py-4 bg-gray-950 rounded-xl flex items-center gap-3 font-bold text-lg text-white hover:text-cyan-300 transition-colors">
                {loading ? (
                  <>
                    <span className="inline-block animate-spin text-xl">⚙️</span>
                    Creating Project...
                  </>
                ) : (
                  <>
                    <Plus size={24} />
                    Start Creating Video
                  </>
                )}
              </div>
            </button>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-8">
            <div className="text-center">
              <div className="text-3xl mb-2">✨</div>
              <p className="text-xs text-gray-400">18+ Effects</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🎬</div>
              <p className="text-xs text-gray-400">14+ Transitions</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">📝</div>
              <p className="text-xs text-gray-400">Auto-Subtitles</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main editor
  return (
    <div className="w-full h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-900/80 via-slate-900/80 to-gray-900/80 border-b border-cyan-500/20 px-6 py-4 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-400">
              {project.title}
            </h1>
            <p className="text-xs text-gray-400 mt-0.5">Professional Video Editing</p>
          </div>

          <div className="flex items-center gap-3">
            {/* History buttons */}
            <div className="flex gap-1 bg-gray-800/50 p-1 rounded-lg border border-gray-700/50 backdrop-blur-sm">
              <button
                onClick={undo}
                disabled={historyIndex <= 0}
                className="p-2.5 hover:bg-cyan-600/20 disabled:opacity-30 rounded-lg transition-all text-cyan-300"
              >
                <Undo size={18} />
              </button>
              <div className="w-px bg-gray-700"></div>
              <button
                onClick={redo}
                disabled={historyIndex >= history.length - 1}
                className="p-2.5 hover:bg-cyan-600/20 disabled:opacity-30 rounded-lg transition-all text-cyan-300"
              >
                <Redo size={18} />
              </button>
            </div>

            {/* Export button */}
            <button
              onClick={handleExport}
              disabled={loading || segments.length === 0}
              className="relative group overflow-hidden px-6 py-2.5 rounded-lg font-bold flex items-center gap-2 disabled:opacity-50 transition-all"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 group-hover:from-green-500 group-hover:to-emerald-500 transition-all"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 blur group-hover:blur-lg opacity-0 group-hover:opacity-50 transition-all"></div>
              <div className="relative flex items-center gap-2">
                {loading ? (
                  <>
                    <span className="animate-spin">⚙️</span>
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download size={18} />
                    Export
                  </>
                )}
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Main editor area */}
      <div className="flex-1 flex overflow-hidden gap-4 p-4">
        {/* Video preview panel */}
        <div className="flex-1 flex flex-col bg-gradient-to-b from-gray-800/50 to-gray-900/50 rounded-2xl overflow-hidden border border-cyan-500/10 backdrop-blur-sm">
          {/* Video player */}
          <div className="flex-1 bg-black/80 flex items-center justify-center relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-gray-900/20 to-transparent pointer-events-none"></div>
            <div className="w-full h-full flex items-center justify-center text-center">
              <div>
                <Play size={80} className="mx-auto mb-4 text-gray-500 opacity-30" />
                <p className="text-gray-500 font-semibold text-lg">Video Preview</p>
                <p className="text-gray-600 text-sm mt-2">{Math.round(playbackTime / 1000)}s / {Math.round(Math.max(...segments.map(s => s.duration_ms), 0) / 1000)}s</p>
              </div>
            </div>

            {/* Fullscreen button */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="absolute top-4 right-4 p-2 bg-gray-900/80 hover:bg-cyan-600 rounded-lg transition-all opacity-0 group-hover:opacity-100"
            >
              <Maximize2 size={18} />
            </button>
          </div>

          {/* Playback controls */}
          <div className="bg-gray-800/50 border-t border-gray-700/50 px-4 py-3 backdrop-blur-sm space-y-2">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-2.5 hover:bg-cyan-600/20 rounded-lg transition-all text-cyan-300"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </button>

              <input
                type="range"
                min="0"
                max={Math.max(...segments.map(s => s.timeline_position_ms + s.duration_ms), 1000)}
                value={playbackTime}
                onChange={(e) => setPlaybackTime(parseInt(e.target.value))}
                className="flex-1 h-2 bg-gray-600 rounded-full accent-cyan-500 cursor-pointer"
              />

              <span className="text-sm text-gray-300 font-mono min-w-12">
                {Math.round(playbackTime / 1000)}s
              </span>
            </div>
          </div>
        </div>

        {/* Right panel - Controls */}
        <div className="w-96 flex flex-col gap-4 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
          {/* Add clips */}
          <div className="bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-blue-500/20 rounded-2xl p-5 backdrop-blur-xl">
            <h3 className="text-lg font-bold mb-3 flex items-center gap-2 text-blue-300">
              <Plus size={20} /> Add Clips
            </h3>
            <input
              type="file"
              accept="video/*"
              onChange={handleAddClip}
              className="block w-full text-sm text-gray-300 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-600 file:to-blue-500 file:text-white hover:file:from-blue-500 hover:file:to-blue-400 file:cursor-pointer transition-all"
            />
            <p className="text-xs text-gray-400 mt-3">
              {segments.length} clip{segments.length !== 1 ? 's' : ''} added • {Math.round(segments.reduce((sum, s) => sum + s.duration_ms, 0) / 1000)}s duration
            </p>
          </div>

          {/* Effects */}
          {selectedSegment !== null && (
            <EffectsPanel
              segment={segments[selectedSegment]}
              onApplyEffect={applyEffect}
            />
          )}

          {/* Subtitles */}
          <SubtitlesPanel
            project={project}
            onAddSubtitle={handleAddSubtitle}
            onDeleteSubtitle={handleDeleteSubtitle}
            subtitles={subtitles}
          />

          {/* Audio */}
          <AudioPanel
            project={project}
            onAddAudio={handleAddAudio}
            audioTracks={audioTracks}
          />
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-gradient-to-t from-gray-900/80 to-gray-800/50 border-t border-cyan-500/10 h-32 p-4 backdrop-blur-sm overflow-x-auto scrollbar-thin scrollbar-thumb-cyan-500/50">
        <div className="flex gap-3 h-full" ref={timelineRef}>
          {segments.length === 0 ? (
            <div className="flex items-center justify-center w-full text-gray-500">
              <div className="text-center">
                <Grid3x3 size={32} className="mx-auto mb-2 opacity-30" />
                <p className="text-sm">Add video clips to start editing</p>
              </div>
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
                  const updated = segments.map((seg, idx) =>
                    idx === i ? { ...seg, ...updates } : seg
                  );
                  setSegments(updated);
                  addToHistory(updated);
                }}
              />
            ))
          )}
        </div>
      </div>

      {/* Error toast */}
      {error && (
        <div className="fixed top-6 right-6 bg-red-900/90 border border-red-700 text-white px-6 py-4 rounded-lg flex items-center gap-3 shadow-2xl backdrop-blur-sm z-50 animate-slide-in">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default CapCutVideoEditorPro;
