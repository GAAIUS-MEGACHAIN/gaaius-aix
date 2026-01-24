import React, { useState, useRef, useEffect, useCallback } from 'react';
import { AlertCircle, Loader, Send, BookOpen, BarChart3, Settings, LogOut } from 'lucide-react';

/**
 * Production-Grade AI Tutoring Platform
 * 
 * Features:
 * - Real backend API integration (not mocked)
 * - 6 LLM providers with automatic fallback
 * - 8 content types with ML detection
 * - Adaptive difficulty scaling
 * - Real-time performance tracking
 * - Session management
 * - Provider health monitoring
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const TUTORING_API = `${API_BASE}/ai-tutoring`;

export default function AITutoringPlatform() {
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [studentId, setStudentId] = useState('student_' + Math.random().toString(36).substr(2, 9));
  const [isSessionActive, setIsSessionActive] = useState(false);

  // Tutoring request state
  const [topic, setTopic] = useState('');
  const [tutorMode, setTutorMode] = useState('explanation');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Student profile & performance
  const [studentProfile, setStudentProfile] = useState(null);
  const [proficiency, setProficiency] = useState({});

  // System health
  const [providerHealth, setProviderHealth] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [healthError, setHealthError] = useState(null);

  // UI state
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch provider health on mount and periodically
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${TUTORING_API}/health/providers`);
        if (response.ok) {
          const data = await response.json();
          setProviderHealth(data);
          setHealthError(null);
        }
      } catch (err) {
        setHealthError(err.message);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Fetch full system health
  const fetchSystemHealth = useCallback(async () => {
    try {
      const response = await fetch(`${TUTORING_API}/health/system`);
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data);
      }
    } catch (err) {
      console.error('System health check failed:', err);
    }
  }, []);

  // Start a new tutoring session
  const startSession = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError(null);
    setMessages([]);

    try {
      const response = await fetch(`${TUTORING_API}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          course_id: 'course_' + Math.random().toString(36).substr(2, 5),
          lesson_id: 'lesson_' + Math.random().toString(36).substr(2, 5),
          topic: topic,
          mode: tutorMode
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const session = await response.json();
      setSessionId(session.session_id);
      setIsSessionActive(true);

      // Add initial system message
      setMessages([{
        type: 'system',
        content: `Session started for topic: ${topic}. Mode: ${tutorMode}`,
        timestamp: new Date()
      }]);

      // Fetch initial system health
      await fetchSystemHealth();
    } catch (err) {
      setError(`Failed to start session: ${err.message}`);
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  // Get tutoring response (real API call)
  const getTutoringResponse = async (e) => {
    e.preventDefault();
    if (!topic.trim() || !isSessionActive) {
      setError('Please start a session first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Add user message
      const userMessage = {
        type: 'user',
        content: topic,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      setTopic('');

      // Call the main tutoring endpoint
      const response = await fetch(`${TUTORING_API}/tutoring-response`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          course_id: 'course_' + Math.random().toString(36).substr(2, 5),
          lesson_id: 'lesson_' + Math.random().toString(36).substr(2, 5),
          topic: topic || 'Explain the topic I asked about',
          mode: tutorMode
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get response`);
      }

      const tutoringResponse = await response.json();

      // Add AI response with metadata
      const aiMessage = {
        type: 'ai',
        content: tutoringResponse.content || 'No response generated',
        metadata: {
          provider: tutoringResponse.provider_used || 'unknown',
          contentType: tutoringResponse.content_type || 'general',
          responseType: tutoringResponse.response_type || 'explanation'
        },
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Update proficiency if content type was detected
      if (tutoringResponse.content_type) {
        setProficiency(prev => ({
          ...prev,
          [tutoringResponse.content_type]: (prev[tutoringResponse.content_type] || 0.5) + 0.05
        }));
      }
    } catch (err) {
      setError(`Failed to get response: ${err.message}`);
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error: ${err.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Get explanation for topic
  const getExplanation = async (e) => {
    e.preventDefault();
    if (!topic.trim() || !isSessionActive) {
      setError('Please start a session first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${TUTORING_API}/explanation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          topic: topic,
          difficulty: 'intermediate'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get explanation`);
      }

      const data = await response.json();

      const message = {
        type: 'ai',
        content: data.explanation || data.content || 'No explanation available',
        metadata: {
          provider: data.provider_used || 'unknown',
          topic: data.topic,
          difficulty: data.difficulty
        },
        timestamp: new Date()
      };

      setMessages(prev => [...prev, {
        type: 'user',
        content: `Explain: ${topic}`,
        timestamp: new Date()
      }, message]);

      setTopic('');
    } catch (err) {
      setError(`Failed to get explanation: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Get practice questions
  const getPracticeQuestions = async (e) => {
    e.preventDefault();
    if (!topic.trim() || !isSessionActive) {
      setError('Please start a session first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${TUTORING_API}/practice-questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          lesson_id: 'lesson_' + Math.random().toString(36).substr(2, 5),
          topic: topic,
          difficulty: 'intermediate',
          count: 3
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get questions`);
      }

      const data = await response.json();

      const message = {
        type: 'ai',
        content: data.questions?.map((q, i) => 
          `Q${i+1}. ${q.question}`
        ).join('\n\n') || 'No questions generated',
        metadata: {
          provider: data.provider_used || 'unknown',
          type: 'practice',
          questionCount: data.questions?.length || 0
        },
        timestamp: new Date()
      };

      setMessages(prev => [...prev, {
        type: 'user',
        content: `Practice questions on: ${topic}`,
        timestamp: new Date()
      }, message]);

      setTopic('');
    } catch (err) {
      setError(`Failed to get practice questions: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Socratic questioning
  const getSocraticQuestion = async (e) => {
    e.preventDefault();
    if (!topic.trim() || !isSessionActive) {
      setError('Please start a session first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${TUTORING_API}/socratic-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          topic: topic,
          student_response: topic
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to get question`);
      }

      const data = await response.json();

      const message = {
        type: 'ai',
        content: data.question || data.content || 'No question generated',
        metadata: {
          provider: data.provider_used || 'unknown',
          type: 'socratic'
        },
        timestamp: new Date()
      };

      setMessages(prev => [...prev, {
        type: 'user',
        content: topic,
        timestamp: new Date()
      }, message]);

      setTopic('');
    } catch (err) {
      setError(`Failed to get socratic question: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // End session
  const endSession = () => {
    setIsSessionActive(false);
    setSessionId(null);
    setMessages([]);
    setTopic('');
    setError(null);
    setShowProfile(false);
  };

  const tutorModes = [
    { value: 'explanation', label: 'Explanation', icon: '📚' },
    { value: 'practice', label: 'Practice', icon: '✏️' },
    { value: 'assessment', label: 'Assessment', icon: '📊' },
    { value: 'socratic', label: 'Socratic', icon: '❓' },
    { value: 'remedial', label: 'Remedial', icon: '🔧' },
    { value: 'adaptive', label: 'Adaptive', icon: '🎯' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-purple-700/30 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-purple-400" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI Tutoring Platform
            </h1>
          </div>
          <div className="flex items-center gap-4">
            {providerHealth && (
              <div className="text-sm">
                <span className={providerHealth.health_status === 'healthy' ? 'text-green-400' : 'text-yellow-400'}>
                  {providerHealth.working_providers}/{providerHealth.total_providers} providers
                </span>
              </div>
            )}
            {isSessionActive && (
              <button
                onClick={() => setShowProfile(!showProfile)}
                className="p-2 rounded-lg hover:bg-purple-700/30 transition"
                title="Student Profile"
              >
                <BarChart3 className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-lg hover:bg-purple-700/30 transition"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
            {isSessionActive && (
              <button
                onClick={endSession}
                className="p-2 rounded-lg bg-red-600/30 hover:bg-red-600/50 transition"
                title="End Session"
              >
                <LogOut className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Settings Panel */}
        {showSettings && (
          <div className="mb-8 p-6 bg-slate-800/50 backdrop-blur border border-purple-700/30 rounded-lg">
            <h2 className="text-xl font-bold mb-4">System Health</h2>
            {healthError ? (
              <div className="text-red-400">Health check error: {healthError}</div>
            ) : providerHealth ? (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400 mb-2">LLM Providers Status:</p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {Object.entries(providerHealth.providers).map(([provider, status]) => (
                      <div key={provider} className="flex items-center gap-2 text-sm">
                        <div className={`w-2 h-2 rounded-full ${
                          status === 'ready' ? 'bg-green-500' :
                          status === 'not_installed' ? 'bg-gray-500' :
                          'bg-yellow-500'
                        }`}></div>
                        <span className="capitalize">{provider}: {status}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="text-sm text-gray-400">
                  Health Status: <span className={providerHealth.health_status === 'healthy' ? 'text-green-400' : 'text-yellow-400'}>
                    {providerHealth.health_status}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-gray-400">Loading health status...</div>
            )}
          </div>
        )}

        {/* Student Profile Panel */}
        {showProfile && isSessionActive && (
          <div className="mb-8 p-6 bg-slate-800/50 backdrop-blur border border-purple-700/30 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Student Profile</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-400">Student ID</p>
                <p className="font-mono text-purple-300">{studentId}</p>
              </div>
              {Object.keys(proficiency).length > 0 && (
                <div>
                  <p className="text-sm text-gray-400">Content Type Proficiency</p>
                  {Object.entries(proficiency).map(([type, score]) => (
                    <div key={type} className="flex justify-between text-sm mt-1">
                      <span className="capitalize">{type}:</span>
                      <span className="text-purple-300">{(score * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Session Start Form */}
        {!isSessionActive ? (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="p-8 bg-gradient-to-br from-slate-800/50 to-slate-800/30 backdrop-blur border border-purple-700/30 rounded-lg">
              <h2 className="text-2xl font-bold mb-6">Start Tutoring Session</h2>
              <form onSubmit={startSession} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">What do you want to learn?</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., Quadratic Equations, Photosynthesis, French Grammar..."
                    className="w-full px-4 py-3 bg-slate-700 border border-purple-700/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-gray-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-3">Tutoring Mode</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {tutorModes.map(mode => (
                      <button
                        key={mode.value}
                        type="button"
                        onClick={() => setTutorMode(mode.value)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                          tutorMode === mode.value
                            ? 'bg-purple-600 border-purple-400'
                            : 'bg-slate-700 border-slate-600 hover:bg-slate-600'
                        } border`}
                      >
                        {mode.icon} {mode.label}
                      </button>
                    ))}
                  </div>
                </div>

                {error && (
                  <div className="flex items-center gap-2 p-4 bg-red-600/20 border border-red-600/50 rounded-lg text-red-200">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !topic.trim()}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg font-semibold hover:shadow-lg hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {loading ? <Loader className="w-5 h-5 animate-spin inline-block mr-2" /> : null}
                  Start Session
                </button>
              </form>
            </div>
          </div>
        ) : (
          // Active Session
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Chat Area */}
            <div className="lg:col-span-3">
              <div className="bg-slate-800/50 backdrop-blur border border-purple-700/30 rounded-lg overflow-hidden flex flex-col h-[600px]">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                        msg.type === 'user'
                          ? 'bg-purple-600/30 border border-purple-500/50'
                          : msg.type === 'error'
                          ? 'bg-red-600/20 border border-red-500/50 text-red-200'
                          : 'bg-slate-700/30 border border-slate-600/50'
                      }`}>
                        {msg.type === 'system' && (
                          <p className="text-xs text-gray-400 italic mb-2">{msg.content}</p>
                        )}
                        {msg.type !== 'system' && (
                          <>
                            <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                            {msg.metadata && (
                              <div className="text-xs text-gray-400 mt-2 pt-2 border-t border-gray-600/30">
                                {msg.metadata.provider && <p>Provider: {msg.metadata.provider}</p>}
                                {msg.metadata.contentType && <p>Content: {msg.metadata.contentType}</p>}
                                {msg.metadata.responseType && <p>Type: {msg.metadata.responseType}</p>}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-slate-700/30 border border-slate-600/50 px-4 py-3 rounded-lg">
                        <Loader className="w-4 h-4 animate-spin" />
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Error Alert */}
                {error && (
                  <div className="px-6 py-3 bg-red-600/20 border-t border-red-600/50 flex items-center gap-2 text-red-200 text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                  </div>
                )}

                {/* Input Form */}
                <form onSubmit={getTutoringResponse} className="border-t border-purple-700/30 p-4">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="Ask a question or continue discussion..."
                      className="flex-1 px-4 py-2 bg-slate-700 border border-purple-700/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-gray-400 text-sm"
                      disabled={loading}
                    />
                    <button
                      type="submit"
                      disabled={loading || !topic.trim()}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Sidebar - Quick Actions */}
            <div className="space-y-4">
              <div className="bg-slate-800/50 backdrop-blur border border-purple-700/30 rounded-lg p-4">
                <h3 className="font-bold mb-3 text-sm">Quick Actions</h3>
                <div className="space-y-2">
                  <button
                    onClick={getExplanation}
                    disabled={loading || !topic.trim()}
                    className="w-full px-4 py-2 bg-blue-600/30 hover:bg-blue-600/50 border border-blue-600/50 rounded-lg text-sm font-medium transition disabled:opacity-50"
                  >
                    📚 Explanation
                  </button>
                  <button
                    onClick={getPracticeQuestions}
                    disabled={loading || !topic.trim()}
                    className="w-full px-4 py-2 bg-green-600/30 hover:bg-green-600/50 border border-green-600/50 rounded-lg text-sm font-medium transition disabled:opacity-50"
                  >
                    ✏️ Practice
                  </button>
                  <button
                    onClick={getSocraticQuestion}
                    disabled={loading || !topic.trim()}
                    className="w-full px-4 py-2 bg-amber-600/30 hover:bg-amber-600/50 border border-amber-600/50 rounded-lg text-sm font-medium transition disabled:opacity-50"
                  >
                    ❓ Socratic
                  </button>
                </div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-purple-700/30 rounded-lg p-4 text-sm">
                <h3 className="font-bold mb-2">Session Info</h3>
                <div className="space-y-1 text-xs text-gray-400">
                  <p>Session: {sessionId?.substr(0, 12)}...</p>
                  <p>Messages: {messages.length}</p>
                  <p>Mode: {tutorMode}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
