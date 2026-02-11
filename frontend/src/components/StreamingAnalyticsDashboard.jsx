/**
 * Real-Time Analytics Dashboard Component
 * Live streaming analytics with Amagi-like features
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { Users, TrendingUp, DollarSign, Activity, Eye, Heart, Share2, MessageSquare } from 'lucide-react';

const COLORS = ['#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'];

const StreamingAnalyticsDashboard = ({ contentId = null }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [contentMetrics, setContentMetrics] = useState(null);
  const [trendingContent, setTrendingContent] = useState([]);
  const [revenueBreakdown, setRevenueBreakdown] = useState(null);
  const [engagement, setEngagement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const wsRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/analytics/dashboard`);
        const data = await response.json();
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard:', error);
      }
    };

    const fetchTrending = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/analytics/trending?limit=10`);
        const data = await response.json();
        setTrendingContent(data.trending);
      } catch (error) {
        console.error('Error fetching trending:', error);
      }
    };

    const fetchRevenue = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/analytics/revenue`);
        const data = await response.json();
        setRevenueBreakdown(data);
      } catch (error) {
        console.error('Error fetching revenue:', error);
      }
    };

    const fetchEngagement = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/analytics/audience`);
        const data = await response.json();
        setEngagement(data);
      } catch (error) {
        console.error('Error fetching engagement:', error);
      }
    };

    // Initial fetch
    fetchDashboard();
    fetchTrending();
    fetchRevenue();
    fetchEngagement();
    setLoading(false);

    // Refresh every 5 seconds
    const dashboardInterval = setInterval(fetchDashboard, 5000);
    const trendingInterval = setInterval(fetchTrending, 10000);
    const revenueInterval = setInterval(fetchRevenue, 15000);
    const engagementInterval = setInterval(fetchEngagement, 15000);

    return () => {
      clearInterval(dashboardInterval);
      clearInterval(trendingInterval);
      clearInterval(revenueInterval);
      clearInterval(engagementInterval);
    };
  }, []);

  // Fetch specific content metrics if contentId provided
  useEffect(() => {
    if (!contentId) return;

    const fetchContentMetrics = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/analytics/content/${contentId}`);
        const data = await response.json();
        setContentMetrics(data);
      } catch (error) {
        console.error('Error fetching content metrics:', error);
      }
    };

    fetchContentMetrics();
    const interval = setInterval(fetchContentMetrics, 5000);
    return () => clearInterval(interval);
  }, [contentId]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const clientId = Math.random().toString(36).substr(2, 9);
      const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/ws/analytics/${clientId}`;
      
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Analytics WebSocket connected');
        // Subscribe to updates
        wsRef.current.send(JSON.stringify({
          command: 'subscribe',
          metrics_type: 'all'
        }));
      };

      wsRef.current.onmessage = (event) => {
        const update = JSON.parse(event.data);
        // Handle real-time updates
        if (update.type === 'dashboard_update') {
          setDashboardData(prev => ({
            ...prev,
            views: { ...prev?.views, total: update.total_views }
          }));
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    try {
      connectWebSocket();
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-white text-2xl">Loading Analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Real-Time Analytics Dashboard
          </h1>
          <p className="text-slate-400">
            Live streaming metrics for views, engagement, and revenue
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Views Card */}
          <div className="bg-gradient-to-br from-blue-900 to-blue-800 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Total Views</p>
                <p className="text-3xl font-bold mt-2">
                  {dashboardData?.views?.total?.toLocaleString() || 0}
                </p>
                <p className="text-slate-400 text-xs mt-2">Live tracking</p>
              </div>
              <Eye className="w-12 h-12 opacity-20" />
            </div>
          </div>

          {/* Unique Viewers */}
          <div className="bg-gradient-to-br from-purple-900 to-purple-800 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Unique Viewers</p>
                <p className="text-3xl font-bold mt-2">
                  {dashboardData?.views?.unique?.toLocaleString() || 0}
                </p>
                <p className="text-slate-400 text-xs mt-2">Real-time</p>
              </div>
              <Users className="w-12 h-12 opacity-20" />
            </div>
          </div>

          {/* Revenue */}
          <div className="bg-gradient-to-br from-green-900 to-green-800 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Total Revenue</p>
                <p className="text-3xl font-bold mt-2">
                  ${dashboardData?.revenue?.total?.toFixed(2) || 0}
                </p>
                <p className="text-slate-400 text-xs mt-2">All sources</p>
              </div>
              <DollarSign className="w-12 h-12 opacity-20" />
            </div>
          </div>

          {/* Engagement Score */}
          <div className="bg-gradient-to-br from-orange-900 to-orange-800 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Engagement Score</p>
                <p className="text-3xl font-bold mt-2">
                  {dashboardData?.engagement?.avg_score?.toFixed(1) || 0}
                </p>
                <p className="text-slate-400 text-xs mt-2">Weighted avg</p>
              </div>
              <Activity className="w-12 h-12 opacity-20" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-slate-700 flex gap-4">
          {['overview', 'content', 'revenue', 'trending'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-semibold transition-colors ${
                activeTab === tab
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Views Over Time */}
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-white text-lg font-semibold mb-4">Views Over Time</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={dashboardData?.views?.trend || []}>
                  <defs>
                    <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                  <Area
                    type="monotone"
                    dataKey="views"
                    stroke="#3B82F6"
                    fillOpacity={1}
                    fill="url(#colorViews)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Engagement Breakdown */}
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-white text-lg font-semibold mb-4">Engagement Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Likes', value: 35 },
                      { name: 'Shares', value: 25 },
                      { name: 'Comments', value: 20 },
                      { name: 'Saves', value: 20 }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {COLORS.map((color, index) => (
                      <Cell key={`cell-${index}`} fill={color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'content' && contentMetrics && (
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-white text-lg font-semibold mb-6">Content Performance</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-400 text-sm">Views</p>
                <p className="text-2xl font-bold text-white">
                  {contentMetrics?.performance?.views || 0}
                </p>
              </div>
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-400 text-sm">Unique Viewers</p>
                <p className="text-2xl font-bold text-white">
                  {contentMetrics?.performance?.unique_viewers || 0}
                </p>
              </div>
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-400 text-sm">Completion Rate</p>
                <p className="text-2xl font-bold text-white">
                  {contentMetrics?.performance?.completion_rate || 0}
                </p>
              </div>
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-400 text-sm">Engagement Score</p>
                <p className="text-2xl font-bold text-white">
                  {contentMetrics?.performance?.engagement_score?.toFixed(1) || 0}
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'revenue' && revenueBreakdown && (
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-white text-lg font-semibold mb-6">Revenue Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* By Source */}
              <div>
                <h4 className="text-white font-semibold mb-4">By Source</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(revenueBreakdown?.by_source || {}).map(([name, value]) => ({ name, value }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis stroke="#94A3B8" />
                    <YAxis stroke="#94A3B8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                    <Bar dataKey="value" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Top Creators */}
              <div>
                <h4 className="text-white font-semibold mb-4">Top Creators</h4>
                <div className="space-y-3">
                  {revenueBreakdown?.top_creators?.slice(0, 5).map((creator, idx) => (
                    <div key={idx} className="flex justify-between bg-slate-700 p-3 rounded">
                      <span className="text-slate-300">{creator[0]}</span>
                      <span className="text-white font-semibold">${creator[1].toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trending' && (
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-white text-lg font-semibold mb-6">Trending Content</h3>
            <div className="space-y-3">
              {trendingContent.map((content, idx) => (
                <div key={idx} className="bg-slate-700 rounded p-4 hover:bg-slate-600 transition">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white font-semibold">#{idx + 1}</span>
                    <TrendingUp className="w-5 h-5 text-green-400" />
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-slate-400">Views</p>
                      <p className="text-white font-semibold">{content.views}</p>
                    </div>
                    <div>
                      <p className="text-slate-400">Engagement</p>
                      <p className="text-white font-semibold">{content.engagement_score.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-slate-400">Revenue</p>
                      <p className="text-white font-semibold">${content.revenue.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamingAnalyticsDashboard;
