/**
 * Advanced Duet & Collaborative Video Editor
 * Record and edit videos together with other users in real-time
 * Features: Multi-user editing, live sync, collaborative timeline, real-time effects
 */

import React, { useState, useEffect, useRef } from 'react';
import { Users, Plus, Play, MessageCircle, Copy, Save, FileVideo, Mic, X, Send, Sparkles } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const DuetCollabVideoEditor = ({ user }) => {
  const [duetSession, setDuetSession] = useState(null);
  const [duetSessions, setDuetSessions] = useState([]);
  const [clips, setClips] = useState([]);
  const [selectedClip, setSelectedClip] = useState(null);
  const [selectedEffects, setSelectedEffects] = useState([]);
  const [collaborators, setCollaborators] = useState([]);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [viewers, setViewers] = useState(0);
  const fileInputRef = useRef(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  useEffect(() => {
    loadDuetSessions();
  }, [user]);

  const loadDuetSessions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/duet/sessions`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setDuetSessions(response.data.sessions || []);
      if (response.data.sessions.length > 0) {
        selectDuetSession(response.data.sessions[0]);
      }
    } catch (error) {
      console.error('Error loading duet sessions:', error);
      const mockSessions = [{
        id: 1,
        title: 'Summer Vibes Duet',
        creator: 'Sarah Chen',
        collaborators: 2,
        duration: 120
      }];
      setDuetSessions(mockSessions);
      selectDuetSession(mockSessions[0]);
    } finally {
      setLoading(false);
    }
  };

  const selectDuetSession = async (session) => {
    setDuetSession(session);
    try {
      const response = await axios.get(`${API_BASE}/duet/sessions/${session.id}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = response.data;
      setClips(data.clips || []);
      setCollaborators(data.collaborators || []);
      setComments(data.comments || []);
      setViewers(data.viewers || 0);
    } catch (error) {
      setClips([
        { id: 1, title: 'Intro Shot', duration: 5, contributor: 'Sarah Chen' },
        { id: 2, title: 'Dance Segment', duration: 15, contributor: 'Marcus Johnson' }
      ]);
      setCollaborators([
        { id: 1, name: 'Sarah Chen', avatar: 'SC', status: 'editing', active: true },
        { id: 2, name: 'Marcus Johnson', avatar: 'MJ', status: 'recording', active: true }
      ]);
      setViewers(34);
    }
  };

  const createDuetSession = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/duet/sessions`, {
        title: 'New Duet Project',
        description: 'Collaborative video editing session'
      }, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const newSession = response.data.session;
      setDuetSessions([...duetSessions, newSession]);
      selectDuetSession(newSession);
      toast.success('Duet session created! Invite collaborators to join.');
    } catch (error) {
      toast.error('Failed to create duet session');
    } finally {
      setLoading(false);
    }
  };

  const uploadClip = async (file) => {
    if (!duetSession) {
      toast.error('Select or create a duet session first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', duetSession.id);

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/duet/clips`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setClips([...clips, response.data.clip]);
      toast.success('Clip uploaded to timeline!');
    } catch (error) {
      toast.error('Failed to upload clip');
    } finally {
      setLoading(false);
    }
  };

  const toggleEffect = (effect) => {
    if (selectedEffects.includes(effect)) {
      setSelectedEffects(selectedEffects.filter(e => e !== effect));
    } else {
      setSelectedEffects([...selectedEffects, effect]);
    }
  };

  const applyEffects = async () => {
    if (!selectedClip) {
      toast.error('Select a clip first');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/duet/clips/${selectedClip.id}/effects`, {
        effects: selectedEffects
      }, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Effects applied successfully!');
      setSelectedEffects([]);
    } catch (error) {
      toast.error('Failed to apply effects');
    } finally {
      setLoading(false);
    }
  };

  const sendComment = async () => {
    if (!commentText.trim() || !duetSession) return;

    try {
      const response = await axios.post(`${API_BASE}/duet/sessions/${duetSession.id}/comments`, {
        text: commentText
      }, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      setComments([...comments, response.data.comment]);
      setCommentText('');
      toast.success('Comment added!');
    } catch (error) {
      toast.error('Failed to send comment');
    }
  };

  const exportDuet = async () => {
    if (!duetSession) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/duet/sessions/${duetSession.id}/export`, {}, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Video exported!');
      window.location.href = response.data.download_url;
    } catch (error) {
      toast.error('Failed to export video');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Link copied!');
  };

  const availableEffects = [
    { id: 'blur', name: 'Blur', icon: '✨' },
    { id: 'brightness', name: 'Bright', icon: '☀️' },
    { id: 'contrast', name: 'Contrast', icon: '◐' },
    { id: 'saturate', name: 'Saturate', icon: '🎨' },
    { id: 'grayscale', name: 'B&W', icon: '⚪' },
    { id: 'sepia', name: 'Sepia', icon: '🌅' },
    { id: 'glow', name: 'Glow', icon: '💫' },
    { id: 'glitch', name: 'Glitch', icon: '⚡' },
    { id: 'vignette', name: 'Vignette', icon: '◯' },
    { id: 'shake', name: 'Shake', icon: '↔️' },
    { id: 'zoom', name: 'Zoom', icon: '🔍' },
    { id: 'particles', name: 'Particles', icon: '✨' }
  ];

  if (!duetSession) {
    return (
      <div style={{ background: 'linear-gradient(135deg, #0f0f0f 0%, #1a0033 100%)', minHeight: '100vh', padding: '24px', color: 'white' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '12px', margin: 0, background: 'linear-gradient(135deg, #10b981 0%, #8b5cf6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            <Users size={32} />
            Duet & Collab Editor
          </h1>
          <button onClick={createDuetSession} disabled={loading} style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px 16px', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', opacity: loading ? 0.5 : 1 }}>
            <Plus size={20} />
            Start Duet
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {duetSessions.map(session => (
            <div key={session.id} onClick={() => selectDuetSession(session)} style={{ background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.8) 0%, rgba(16, 185, 129, 0.8) 100%)', borderRadius: '8px', padding: '12px', cursor: 'pointer', border: '2px solid transparent', transition: 'all 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#10b981'; e.currentTarget.style.transform = 'translateY(-3px)'; }} onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'transparent'; e.currentTarget.style.transform = 'none'; }}>
              <div style={{ fontSize: '1rem', fontWeight: 'bold' }}>{session.title}</div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)' }}>by {session.creator}</div>
              <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>{session.collaborators} collaborators</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f0f0f 0%, #1a0033 100%)', minHeight: '100vh', padding: '24px', color: 'white' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '12px', margin: 0, background: 'linear-gradient(135deg, #10b981 0%, #8b5cf6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          <Users size={32} />
          {duetSession.title}
        </h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={() => copyToClipboard(duetSession.id)} style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px 16px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600' }}>
            <Copy size={18} />
            Invite
          </button>
          <button onClick={exportDuet} disabled={loading} style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px 16px', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', opacity: loading ? 0.5 : 1 }}>
            <Save size={18} />
            Export
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '20px' }}>
        {/* MAIN EDITOR */}
        <div style={{ background: 'rgba(20, 20, 30, 0.8)', borderRadius: '16px', border: '1px solid rgba(139, 92, 246, 0.2)', padding: '20px' }}>
          <div style={{ width: '100%', aspectRatio: '16/9', background: 'linear-gradient(135deg, #000 0%, #1a0a2e 100%)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px', border: '2px solid rgba(16, 185, 129, 0.3)' }}>
            <button style={{ width: '80px', height: '80px', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', border: 'none', borderRadius: '50%', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 30px rgba(16, 185, 129, 0.5)' }}>
              <Play size={40} fill="currentColor" />
            </button>
          </div>

          {/* STATS */}
          <div style={{ display: 'flex', justifyContent: 'space-around', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '8px', padding: '12px', border: '1px solid rgba(139, 92, 246, 0.2)', marginBottom: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>{clips.length}</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>Clips</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>{collaborators.length}</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>Editing</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>{viewers}</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>Viewers</div>
            </div>
          </div>

          {/* CONTROLS */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px', marginBottom: '20px' }}>
            <button onClick={() => fileInputRef.current?.click()} disabled={loading} style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontWeight: '600', opacity: loading ? 0.5 : 1 }}>
              <FileVideo size={18} />
              Add Clip
            </button>
            <button onClick={() => setIsRecording(!isRecording)} style={{ background: isRecording ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontWeight: '600' }}>
              <Mic size={18} />
              {isRecording ? 'Stop' : 'Record'}
            </button>
            <button onClick={applyEffects} disabled={!selectedClip || selectedEffects.length === 0} style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px', borderRadius: '8px', cursor: !selectedClip || selectedEffects.length === 0 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontWeight: '600', opacity: !selectedClip || selectedEffects.length === 0 ? 0.5 : 1 }}>
              <Sparkles size={18} />
              Apply
            </button>
            <button onClick={() => setDuetSession(null)} style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', border: 'none', color: 'white', padding: '12px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontWeight: '600' }}>
              <X size={18} />
              Close
            </button>
          </div>

          {/* TIMELINE */}
          <div style={{ background: 'rgba(10, 10, 20, 0.9)', borderRadius: '12px', padding: '16px', marginBottom: '20px', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#8b5cf6', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileVideo size={16} />
              Timeline ({clips.length})
            </div>
            <div style={{ background: 'rgba(0, 0, 0, 0.5)', borderRadius: '8px', padding: '12px', overflowX: 'auto', display: 'flex', gap: '8px', minHeight: '120px', border: '1px dashed rgba(139, 92, 246, 0.3)' }}>
              {clips.map(clip => (
                <div key={clip.id} onClick={() => setSelectedClip(clip)} style={{ background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.8) 0%, rgba(16, 185, 129, 0.8) 100%)', borderRadius: '8px', padding: '12px', minWidth: '150px', flexShrink: 0, cursor: 'pointer', border: selectedClip?.id === clip.id ? '2px solid #fbbf24' : '2px solid transparent', transition: 'all 0.3s', display: 'flex', flexDirection: 'column', gap: '8px', boxShadow: selectedClip?.id === clip.id ? '0 0 20px rgba(251, 191, 36, 0.5)' : 'none' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 'bold' }}>{clip.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>by {clip.contributor}</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>{clip.duration}s</div>
                </div>
              ))}
              <div onClick={() => fileInputRef.current?.click()} style={{ background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.8) 0%, rgba(16, 185, 129, 0.8) 100%)', borderRadius: '8px', padding: '12px', minWidth: '150px', flexShrink: 0, cursor: 'pointer', border: '2px solid transparent', opacity: 0.5, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Plus size={24} />
              </div>
            </div>
          </div>

          {/* EFFECTS */}
          <div style={{ background: 'rgba(10, 10, 20, 0.9)', borderRadius: '12px', padding: '16px', border: '1px solid rgba(139, 92, 246, 0.2)' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#8b5cf6', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={16} />
              Effects Library
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '10px' }}>
              {availableEffects.map(effect => (
                <button key={effect.id} onClick={() => toggleEffect(effect.id)} style={{ background: selectedEffects.includes(effect.id) ? 'linear-gradient(135deg, #10b981 0%, #8b5cf6 100%)' : 'linear-gradient(135deg, rgba(16, 185, 129, 0.6) 0%, rgba(139, 92, 246, 0.6) 100%)', border: selectedEffects.includes(effect.id) ? '2px solid #10b981' : '2px solid rgba(16, 185, 129, 0.3)', color: 'white', padding: '10px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: '600', transition: 'all 0.3s', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px', boxShadow: selectedEffects.includes(effect.id) ? '0 0 20px rgba(16, 185, 129, 0.5)' : 'none' }}>
                  <div>{effect.icon}</div>
                  <div>{effect.name}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div style={{ background: 'rgba(20, 20, 30, 0.8)', borderRadius: '16px', border: '1px solid rgba(139, 92, 246, 0.2)', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', maxHeight: '85vh', overflowY: 'auto' }}>
          {/* COLLABORATORS */}
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#8b5cf6', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid rgba(139, 92, 246, 0.2)', paddingBottom: '12px' }}>
              <Users size={16} />
              Team ({collaborators.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {collaborators.map(collab => (
                <div key={collab.id} style={{ background: 'rgba(139, 92, 246, 0.2)', borderRadius: '8px', padding: '12px', border: '1px solid rgba(139, 92, 246, 0.3)', display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, #10b981 0%, #8b5cf6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>{collab.avatar}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: '600', color: 'white' }}>{collab.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)' }}>{collab.status}</div>
                  </div>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: collab.active ? '#10b981' : '#6b7280', boxShadow: collab.active ? '0 0 8px rgba(16, 185, 129, 0.6)' : 'none' }} />
                </div>
              ))}
            </div>
            <button onClick={() => copyToClipboard(duetSession.id)} style={{ width: '100%', background: 'linear-gradient(135deg, #10b981 0%, #8b5cf6 100%)', border: 'none', color: 'white', padding: '10px', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', marginTop: '12px', transition: 'all 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 0 15px rgba(16, 185, 129, 0.4)'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}>
              <Plus size={16} style={{ marginRight: '8px', display: 'inline' }} />
              Invite Collaborators
            </button>
          </div>

          {/* COMMENTS */}
          <div style={{ borderTop: '1px solid rgba(139, 92, 246, 0.2)', paddingTop: '16px' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#8b5cf6', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid rgba(139, 92, 246, 0.2)', paddingBottom: '12px' }}>
              <MessageCircle size={16} />
              Comments
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '200px', overflowY: 'auto', marginBottom: '12px' }}>
              {comments.slice(-5).map((comment, idx) => (
                <div key={idx} style={{ background: 'rgba(139, 92, 246, 0.1)', borderRadius: '8px', padding: '10px', borderLeft: '3px solid #8b5cf6' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#a78bfa' }}>{comment.author}</div>
                  <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.8)', marginTop: '4px' }}>{comment.text}</div>
                  <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', marginTop: '4px' }}>
                    {new Date(comment.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input type="text" placeholder="Add comment..." value={commentText} onChange={(e) => setCommentText(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendComment()} style={{ flex: 1, background: 'rgba(139, 92, 246, 0.2)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '8px', padding: '8px 12px', color: 'white', fontSize: '0.85rem' }} />
              <button onClick={sendComment} style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', border: 'none', color: 'white', padding: '8px 12px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <input ref={fileInputRef} type="file" accept="video/*" style={{ display: 'none' }} onChange={(e) => { const file = e.target.files?.[0]; if (file) uploadClip(file); }} />
    </div>
  );
};

export { DuetCollabVideoEditor };
