/**
 * MAIN NAVIGATION WITH ANALYTICS TAB
 * ================================================================================
 * Main menu component with all app tabs including the new Analytics menu tab
 * ================================================================================
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart3, MessageSquare, FileText, ImageIcon, Video, Music, Radio,
  Share2, Zap, Settings, User, Menu, X, ChevronRight, Plus, Home,
  TrendingUp, Activity, Users, Eye, Heart, Share, Lightbulb
} from 'lucide-react';
import AdvancedAnalyticsDashboard from './AdvancedAnalyticsDashboard';

// ============== TAB CONFIGURATIONS ==============

const MAIN_TABS = [
  {
    id: 'home',
    label: 'Home',
    icon: Home,
    description: 'Welcome to GAAIUS AI'
  },
  {
    id: 'chat',
    label: 'Chat',
    icon: MessageSquare,
    description: 'AI conversations and creativity'
  },
  {
    id: 'projects',
    label: 'Projects',
    icon: FileText,
    description: 'Create and manage projects'
  },
  {
    id: 'images',
    label: 'Images',
    icon: ImageIcon,
    description: 'Generate and edit images'
  },
  {
    id: 'documents',
    label: 'Documents',
    icon: FileText,
    description: 'Document creation studio'
  },
  {
    id: 'movies',
    label: 'Movies',
    icon: Video,
    description: 'Movie streaming platform'
  },
  {
    id: 'music',
    label: 'Music',
    icon: Music,
    description: 'Music and audio creation'
  },
  {
    id: 'podcasts',
    label: 'Podcasts',
    icon: Radio,
    description: 'Podcast creation and streaming'
  },
  {
    id: 'distribution',
    label: 'Distribution',
    icon: Share2,
    description: 'Distribute your content'
  },
  {
    id: 'marketplace',
    label: 'Marketplace',
    icon: Zap,
    description: 'Browse and sell content'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    description: 'Comprehensive analytics dashboard',
    isNew: true,
    isPremium: true
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    description: 'Account settings'
  },
];

// ============== ANALYTICS QUICK STATS ==============

const AnalyticsQuickStats = ({ stats }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-xl border border-blue-500/20">
      <div className="text-center">
        <Activity size={20} className="text-blue-400 mx-auto mb-2" />
        <p className="text-2xl font-bold text-white">{stats?.totalActivities || 0}</p>
        <p className="text-xs text-gray-400">Total Activities</p>
      </div>
      <div className="text-center">
        <Users size={20} className="text-purple-400 mx-auto mb-2" />
        <p className="text-2xl font-bold text-white">{stats?.activeSessions || 0}</p>
        <p className="text-xs text-gray-400">Sessions</p>
      </div>
      <div className="text-center">
        <TrendingUp size={20} className="text-green-400 mx-auto mb-2" />
        <p className="text-2xl font-bold text-white">{stats?.avgEngagement?.toFixed(1) || 0}</p>
        <p className="text-xs text-gray-400">Engagement</p>
      </div>
      <div className="text-center">
        <Eye size={20} className="text-pink-400 mx-auto mb-2" />
        <p className="text-2xl font-bold text-white">{stats?.featuresUsed || 0}</p>
        <p className="text-xs text-gray-400">Features</p>
      </div>
    </div>
  );
};

// ============== TAB BUTTON ==============

const TabButton = ({ tab, isActive, onClick, showBadge = false }) => {
  const Icon = tab.icon;
  
  return (
    <button
      onClick={onClick}
      className={`relative flex items-center justify-center lg:justify-start gap-3 px-4 py-3 rounded-lg transition-all duration-300 whitespace-nowrap ${
        isActive
          ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30'
          : 'text-gray-400 hover:text-white hover:bg-white/10 border border-transparent'
      }`}
      title={tab.description}
    >
      <Icon size={20} />
      <span className="hidden lg:inline text-sm font-medium">{tab.label}</span>
      
      {tab.isNew && (
        <span className="ml-2 px-2 py-1 text-xs font-bold bg-gradient-to-r from-yellow-400 to-orange-400 text-black rounded-full">
          NEW
        </span>
      )}
      
      {showBadge && (
        <span className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
          •
        </span>
      )}
    </button>
  );
};

// ============== MAIN NAVIGATION COMPONENT ==============

const MainNavigation = ({ children }) => {
  const [activeTab, setActiveTab] = useState('home');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [analyticsStats, setAnalyticsStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch analytics stats when analytics tab is viewed
  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchAnalyticsStats();
    }
  }, [activeTab]);

  const fetchAnalyticsStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analytics/platform-dashboard', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAnalyticsStats({
          totalActivities: data.totalActivities || 0,
          activeSessions: data.activeSessions || 0,
          avgEngagement: data.avgEngagement || 0,
          featuresUsed: data.featuresUsed || 0,
        });
      }
    } catch (error) {
      console.error('Failed to fetch analytics stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black overflow-hidden">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gray-900/50 border-r border-white/10 backdrop-blur-xl transition-all duration-300 flex flex-col overflow-y-auto`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className={`flex items-center gap-3 ${sidebarOpen ? '' : 'justify-center'}`}>
              <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <BarChart3 size={20} className="text-white" />
              </div>
              {sidebarOpen && (
                <div>
                  <p className="text-sm font-bold text-white">GAAIUS</p>
                  <p className="text-xs text-gray-400">Analytics</p>
                </div>
              )}
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 rounded lg:hidden"
            >
              {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <p className={`text-xs font-semibold text-gray-500 mb-3 px-2 ${!sidebarOpen && 'hidden'}`}>
            MAIN FEATURES
          </p>
          
          {MAIN_TABS.slice(0, 10).map(tab => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
              showBadge={tab.isNew}
            />
          ))}

          <div className="my-4 border-t border-white/10" />

          <p className={`text-xs font-semibold text-gray-500 mb-3 px-2 ${!sidebarOpen && 'hidden'}`}>
            ANALYTICS & ADMIN
          </p>

          {/* Analytics Tab - Highlighted */}
          <div className="relative">
            <TabButton
              key="analytics"
              tab={MAIN_TABS.find(t => t.id === 'analytics')}
              isActive={activeTab === 'analytics'}
              onClick={() => setActiveTab('analytics')}
              showBadge={true}
            />
            
            {sidebarOpen && activeTab === 'analytics' && (
              <div className="absolute -right-2 top-1/2 transform -translate-y-1/2 w-1 h-6 bg-gradient-to-b from-blue-500 to-purple-600 rounded-r-lg" />
            )}
          </div>

          {/* Settings */}
          <TabButton
            tab={MAIN_TABS.find(t => t.id === 'settings')}
            isActive={activeTab === 'settings'}
            onClick={() => setActiveTab('settings')}
          />
        </nav>

        {/* Footer */}
        <div className="border-t border-white/10 p-4 space-y-3">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-white truncate">User</p>
                <p className="text-xs text-gray-400">Pro Member</p>
              </div>
            )}
          </div>
          
          {sidebarOpen && (
            <button className="w-full px-3 py-2 text-xs font-semibold rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300">
              Upgrade Plan
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-gradient-to-r from-gray-900/50 to-gray-800/50 border-b border-white/10 backdrop-blur-xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                {MAIN_TABS.find(t => t.id === activeTab)?.label}
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                {MAIN_TABS.find(t => t.id === activeTab)?.description}
              </p>
            </div>
            
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-medium text-white transition-all duration-300">
              <Plus size={18} />
              Create New
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto">
          {activeTab === 'analytics' ? (
            <div>
              {analyticsStats && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">Quick Overview</h2>
                  <AnalyticsQuickStats stats={analyticsStats} />
                </div>
              )}
              <AdvancedAnalyticsDashboard />
            </div>
          ) : (
            <div className="p-8 text-center">
              <div className="inline-block p-8 rounded-2xl bg-white/5 border border-white/10 mb-6">
                {React.createElement(MAIN_TABS.find(t => t.id === activeTab)?.icon || Activity, {
                  size: 64,
                  className: 'text-gray-400'
                })}
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                {MAIN_TABS.find(t => t.id === activeTab)?.label} Coming Soon
              </h2>
              <p className="text-gray-400 mb-8">
                This feature is currently under development. Stay tuned!
              </p>
              
              {activeTab === 'analytics' && (
                <button
                  onClick={() => setActiveTab('analytics')}
                  className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300"
                >
                  View Analytics Dashboard
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MainNavigation;
