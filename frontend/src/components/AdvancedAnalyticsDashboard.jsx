/**
 * ADVANCED ANALYTICS DASHBOARD
 * ================================================================================
 * Comprehensive analytics platform tracking all user activities across all features
 * 
 * Features:
 * - Real-time activity tracking (Chat, Projects, Images, Documents, Movies, Podcasts, etc.)
 * - Advanced visualizations and charts
 * - AI-powered insights using Groq
 * - Comparative analysis and trends
 * - User behavior patterns
 * - Feature adoption metrics
 * - Cohort analysis
 * - Predictive analytics
 * - Beautiful modern UI with glassmorphism
 * - Responsive design
 * - Dark mode support
 * ================================================================================
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import {
  TrendingUp, TrendingDown, Activity, Users, Zap, Calendar, Clock,
  BarChart3, PieChart as PieChartIcon, Map, MessageSquare, Layers,
  Eye, Share2, Heart, Download, Upload, AlertCircle, Lightbulb,
  Target, Flame, Award, ChevronDown, ChevronRight, Filter, Settings,
  RefreshCw, Download as DownloadIcon, Printer, Mail
} from 'lucide-react';

// ============== CONSTANTS ==============

const FEATURES = [
  { id: 'chat', label: 'Chat', icon: MessageSquare, color: '#3B82F6' },
  { id: 'projects', label: 'Projects', icon: Layers, color: '#8B5CF6' },
  { id: 'images', label: 'Images', icon: Eye, color: '#EC4899' },
  { id: 'documents', label: 'Documents', icon: Download, color: '#F59E0B' },
  { id: 'movies', label: 'Movies', icon: Activity, color: '#EF4444' },
  { id: 'podcasts', label: 'Podcasts', icon: Zap, color: '#10B981' },
  { id: 'music', label: 'Music', icon: Zap, color: '#06B6D4' },
  { id: 'live_streams', label: 'Live Streams', icon: Activity, color: '#F43F5E' },
];

const INSIGHT_TYPES = {
  'usage_pattern': 'Usage Pattern',
  'anomaly_detected': 'Anomaly',
  'engagement_spike': 'Engagement Spike',
  'churn_risk': 'Churn Risk',
  'opportunity': 'Opportunity',
  'milestone': 'Milestone',
};

// ============== ADVANCED METRICS CARD ==============

const MetricsCard = ({ icon: Icon, label, value, change, unit = '', color = '#3B82F6' }) => {
  const isPositive = change >= 0;
  
  return (
    <div className="relative overflow-hidden rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6 hover:from-white/15 hover:to-white/10 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10">
      {/* Background glow */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-500" />
      
      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-400 mb-2">{label}</p>
          <p className="text-3xl font-bold text-white">{value}{unit}</p>
          
          {change !== undefined && (
            <div className="flex items-center gap-2 mt-3">
              {isPositive ? (
                <TrendingUp size={16} className="text-green-500" />
              ) : (
                <TrendingDown size={16} className="text-red-500" />
              )}
              <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
                {isPositive ? '+' : ''}{change.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
        
        <div className="p-3 rounded-xl bg-gradient-to-br from-white/20 to-white/10">
          <Icon size={24} style={{ color }} />
        </div>
      </div>
    </div>
  );
};

// ============== INSIGHT CARD ==============

const InsightCard = ({ insight }) => {
  const getInsightColor = (type) => {
    const colors = {
      'usage_pattern': 'from-blue-500/20 to-blue-600/20',
      'anomaly_detected': 'from-yellow-500/20 to-orange-600/20',
      'engagement_spike': 'from-green-500/20 to-emerald-600/20',
      'churn_risk': 'from-red-500/20 to-pink-600/20',
      'opportunity': 'from-purple-500/20 to-indigo-600/20',
      'milestone': 'from-yellow-500/20 to-amber-600/20',
    };
    return colors[type] || colors['usage_pattern'];
  };
  
  const getInsightIcon = (type) => {
    const icons = {
      'usage_pattern': Activity,
      'anomaly_detected': AlertCircle,
      'engagement_spike': Flame,
      'churn_risk': AlertCircle,
      'opportunity': Lightbulb,
      'milestone': Award,
    };
    return icons[type] || Activity;
  };
  
  const Icon = getInsightIcon(insight.insight_type);
  
  return (
    <div className={`rounded-xl bg-gradient-to-br ${getInsightColor(insight.insight_type)} border border-white/20 p-4 hover:border-white/40 transition-all duration-300`}>
      <div className="flex items-start gap-3">
        <Icon size={20} className="text-white mt-1 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white">{INSIGHT_TYPES[insight.insight_type]}</p>
          <p className="text-xs text-gray-300 mt-1">{insight.description}</p>
          {insight.recommended_action && (
            <p className="text-xs text-gray-200 mt-2 font-medium">💡 {insight.recommended_action}</p>
          )}
        </div>
      </div>
    </div>
  );
};

// ============== ADVANCED ANALYTICS DASHBOARD ==============

const AdvancedAnalyticsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');
  const [dashboardData, setDashboardData] = useState(null);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics/platform-dashboard?timeRange=${timeRange}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch analytics');
      
      const data = await response.json();
      setDashboardData(data);
      
      // Fetch insights
      const insightsResponse = await fetch('/api/analytics/insights', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights || []);
      }
    } catch (err) {
      setError(err.message);
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  // Initialize WebSocket for real-time updates
  useEffect(() => {
    fetchDashboardData();
    
    // WebSocket for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    wsRef.current = new WebSocket(`${protocol}//${window.location.host}/ws/analytics`);
    
    wsRef.current.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        setDashboardData(prev => prev ? { ...prev, ...update } : update);
      } catch (e) {
        console.error('WebSocket message error:', e);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-4 animate-pulse">
            <Activity size={32} className="text-white" />
          </div>
          <p className="text-white text-lg">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
        <div className="text-center">
          <AlertCircle size={48} className="text-red-500 mx-auto mb-4" />
          <p className="text-white text-lg">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-blob" />
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-blob animation-delay-2000" />
        <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-blob animation-delay-4000" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="border-b border-white/10 backdrop-blur-xl bg-gradient-to-r from-gray-900/50 to-gray-800/50 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Analytics Dashboard
                </h1>
                <p className="text-gray-400 mt-2">Comprehensive platform activity and user insights</p>
              </div>
              
              <div className="flex items-center gap-3">
                <button
                  onClick={fetchDashboardData}
                  className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-all duration-300"
                >
                  <RefreshCw size={20} />
                </button>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between gap-4 flex-wrap">
              {/* Time range selector */}
              <div className="flex items-center gap-2 bg-white/5 rounded-lg p-1 border border-white/10">
                {['7d', '30d', '90d', '1y'].map(range => (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={`px-3 py-1 rounded transition-all duration-300 ${
                      timeRange === range
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    {range}
                  </button>
                ))}
              </div>

              {/* Export buttons */}
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-300 border border-white/10">
                  <DownloadIcon size={16} />
                  <span className="text-sm">Export</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Tabs */}
          <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'features', label: 'Features', icon: Layers },
              { id: 'trends', label: 'Trends', icon: TrendingUp },
              { id: 'insights', label: 'AI Insights', icon: Lightbulb },
              { id: 'comparison', label: 'Comparison', icon: Activity },
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-white/10'
                  }`}
                >
                  <Icon size={18} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && dashboardData && (
            <div className="space-y-8">
              {/* Top Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricsCard
                  icon={Activity}
                  label="Total Activities"
                  value={dashboardData.totalActivities || 0}
                  change={dashboardData.activityGrowth || 0}
                  color="#3B82F6"
                />
                <MetricsCard
                  icon={Users}
                  label="Active Sessions"
                  value={dashboardData.activeSessions || 0}
                  change={dashboardData.sessionGrowth || 0}
                  color="#8B5CF6"
                />
                <MetricsCard
                  icon={Zap}
                  label="Engagement Score"
                  value={(dashboardData.avgEngagement || 0).toFixed(1)}
                  unit="/100"
                  change={dashboardData.engagementChange || 0}
                  color="#EC4899"
                />
                <MetricsCard
                  icon={TrendingUp}
                  label="Features Used"
                  value={dashboardData.featuresUsed || 0}
                  change={dashboardData.featureAdoption || 0}
                  color="#F59E0B"
                />
              </div>

              {/* Charts Row */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Activity Timeline */}
                <div className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6">
                  <h3 className="text-lg font-semibold mb-4">Activity Timeline</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={dashboardData.timeSeriesData || []}>
                      <defs>
                        <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" />
                      <YAxis stroke="rgba(255,255,255,0.5)" />
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.8)', border: '1px solid rgba(255,255,255,0.1)' }} />
                      <Area type="monotone" dataKey="value" stroke="#3B82F6" fillOpacity={1} fill="url(#colorActivity)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Feature Distribution */}
                <div className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6">
                  <h3 className="text-lg font-semibold mb-4">Feature Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={dashboardData.featureDistribution || []}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {FEATURES.map((feature, index) => (
                          <Cell key={`cell-${index}`} fill={feature.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.8)', border: '1px solid rgba(255,255,255,0.1)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {FEATURES.map(feature => {
                  const featureData = dashboardData.featureMetrics?.[feature.id];
                  return (
                    <div
                      key={feature.id}
                      onClick={() => setSelectedFeature(feature.id)}
                      className={`rounded-xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-4 cursor-pointer transition-all duration-300 hover:from-white/15 hover:to-white/10 hover:border-white/40 ${
                        selectedFeature === feature.id ? 'ring-2 ring-blue-500' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-sm">{feature.label}</h4>
                        <feature.icon size={20} style={{ color: feature.color }} />
                      </div>
                      <p className="text-2xl font-bold">{featureData?.totalActivities || 0}</p>
                      <p className="text-xs text-gray-400 mt-2">Activities</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* FEATURES TAB */}
          {activeTab === 'features' && dashboardData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {FEATURES.map(feature => {
                  const featureData = dashboardData.featureMetrics?.[feature.id];
                  if (!featureData) return null;
                  
                  return (
                    <div
                      key={feature.id}
                      className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6 hover:from-white/15 hover:to-white/10 transition-all duration-300"
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 rounded-lg" style={{ backgroundColor: `${feature.color}20` }}>
                          <feature.icon size={24} style={{ color: feature.color }} />
                        </div>
                        <h3 className="text-lg font-semibold">{feature.label}</h3>
                      </div>
                      
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Total Activities</span>
                          <span className="font-bold">{featureData.totalActivities}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Avg Engagement</span>
                          <span className="font-bold">{featureData.avgEngagement?.toFixed(1)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Success Rate</span>
                          <span className="font-bold">{featureData.successRate?.toFixed(1)}%</span>
                        </div>
                        <div className="h-1 bg-white/10 rounded-full overflow-hidden mt-3">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${featureData.successRate || 0}%`,
                              background: `linear-gradient(90deg, ${feature.color}, ${feature.color}dd)`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TRENDS TAB */}
          {activeTab === 'trends' && dashboardData && (
            <div className="space-y-6">
              <div className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6">
                <h3 className="text-lg font-semibold mb-4">Activity Trends</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={dashboardData.trendData || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                    <YAxis stroke="rgba(255,255,255,0.5)" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.8)', border: '1px solid rgba(255,255,255,0.1)' }} />
                    <Legend />
                    <Line type="monotone" dataKey="growth" stroke="#3B82F6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="momentum" stroke="#8B5CF6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* AI INSIGHTS TAB */}
          {activeTab === 'insights' && (
            <div className="space-y-4">
              {insights.length > 0 ? (
                insights.map((insight, idx) => (
                  <InsightCard key={idx} insight={insight} />
                ))
              ) : (
                <div className="text-center py-12">
                  <Lightbulb size={48} className="text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400">No insights available yet. Keep using the platform!</p>
                </div>
              )}
            </div>
          )}

          {/* COMPARISON TAB */}
          {activeTab === 'comparison' && dashboardData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6">
                  <h3 className="text-lg font-semibold mb-4">Period Comparison</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-400 mb-2">Current Period</p>
                      <p className="text-2xl font-bold">{dashboardData.currentPeriodActivities || 0} activities</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400 mb-2">Previous Period</p>
                      <p className="text-2xl font-bold">{dashboardData.previousPeriodActivities || 0} activities</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400 mb-2">Growth Rate</p>
                      <p className={`text-2xl font-bold ${dashboardData.growthRate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {dashboardData.growthRate >= 0 ? '+' : ''}{dashboardData.growthRate?.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/20 p-6">
                  <h3 className="text-lg font-semibold mb-4">Engagement Metrics</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={dashboardData.engagementMetrics || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" />
                      <YAxis stroke="rgba(255,255,255,0.5)" />
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.8)', border: '1px solid rgba(255,255,255,0.1)' }} />
                      <Bar dataKey="value" fill="#3B82F6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;
