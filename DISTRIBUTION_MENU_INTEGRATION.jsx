/**
 * MENU INTEGRATION FOR DISTRIBUTION PLATFORM
 * Add Distribution tab to your main navigation menu
 * 
 * This file shows all the ways to integrate the distribution
 * platform into your existing menu/navigation
 */

// ============================================================================
// OPTION 1: REACT ROUTER INTEGRATION (RECOMMENDED)
// ============================================================================

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import DistributionPlatform from './pages/DistributionPlatform';

// Main App Component
export function App() {
  const userId = "user_123"; // From authentication
  
  return (
    <Router>
      <nav className="navbar">
        <ul>
          <li><Link to="/">🏠 Home</Link></li>
          <li><Link to="/movies">🎬 Movies</Link></li>
          <li><Link to="/videos">🎥 Videos</Link></li>
          <li><Link to="/music">🎵 Music</Link></li>
          <li><Link to="/distribution">📤 Distribution</Link></li> {/* NEW */}
          <li><Link to="/profile">👤 Profile</Link></li>
        </ul>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/movies" element={<Movies />} />
        <Route path="/videos" element={<Videos />} />
        <Route path="/music" element={<Music />} />
        <Route path="/distribution" element={<DistributionPlatform userId={userId} />} /> {/* NEW */}
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
}


// ============================================================================
// OPTION 2: SIMPLE NAVBAR INTEGRATION
// ============================================================================

import styled from 'styled-components';

const NavBar = styled.nav`
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
`;

const NavItem = styled.a`
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
  cursor: pointer;
  font-weight: 500;

  &:hover {
    background: rgba(0, 212, 255, 0.2);
    color: #00d4ff;
  }

  &.active {
    background: #00d4ff;
    color: #1e3c72;
  }
`;

export function SimpleNavBar({ currentPage, onNavigate }) {
  return (
    <NavBar>
      <NavItem 
        active={currentPage === 'home'}
        onClick={() => onNavigate('home')}
      >
        🏠 Home
      </NavItem>
      <NavItem 
        active={currentPage === 'movies'}
        onClick={() => onNavigate('movies')}
      >
        🎬 Movies
      </NavItem>
      <NavItem 
        active={currentPage === 'videos'}
        onClick={() => onNavigate('videos')}
      >
        🎥 Videos
      </NavItem>
      <NavItem 
        active={currentPage === 'music'}
        onClick={() => onNavigate('music')}
      >
        🎵 Music
      </NavItem>
      <NavItem 
        active={currentPage === 'distribution'}
        onClick={() => onNavigate('distribution')}
      >
        📤 Distribution
      </NavItem>
      <NavItem 
        active={currentPage === 'profile'}
        onClick={() => onNavigate('profile')}
      >
        👤 Profile
      </NavItem>
    </NavBar>
  );
}


// ============================================================================
// OPTION 3: DROPDOWN MENU INTEGRATION
// ============================================================================

export function DropdownNavigation() {
  const [openMenu, setOpenMenu] = React.useState(null);

  return (
    <nav className="navbar-dropdown">
      {/* Main Menu Items */}
      <div className="menu-section">
        <h4>Create & Monetize</h4>
        <ul>
          <li>
            <button 
              onMouseEnter={() => setOpenMenu('distribution')}
              onMouseLeave={() => setOpenMenu(null)}
            >
              📤 Distribution & Monetization
            </button>
            
            {openMenu === 'distribution' && (
              <div className="submenu">
                <a href="/distribution">📤 Upload Content</a>
                <a href="/distribution?tab=projects">📚 My Distributions</a>
                <a href="/distribution?tab=royalties">💰 Earnings</a>
                <a href="/distribution?tab=settings">⚙️ Settings</a>
              </div>
            )}
          </li>
        </ul>
      </div>

      {/* Browse Menu Items */}
      <div className="menu-section">
        <h4>Browse</h4>
        <ul>
          <li><a href="/movies">🎬 Movies</a></li>
          <li><a href="/videos">🎥 Videos</a></li>
          <li><a href="/music">🎵 Music</a></li>
        </ul>
      </div>
    </nav>
  );
}


// ============================================================================
// OPTION 4: DASHBOARD WIDGET INTEGRATION
// ============================================================================

/**
 * Add Distribution widget to existing dashboard
 * Shows quick access to distribution features
 */
export function DashboardWidget({ userId }) {
  const [stats, setStats] = React.useState(null);

  React.useEffect(() => {
    // Fetch artist stats
    fetch(`/api/v1/distribution/artist/profile/${userId}`)
      .then(r => r.json())
      .then(data => setStats(data));
  }, [userId]);

  return (
    <div className="dashboard-widget distribution-widget">
      <h3>🎵 Distribution Center</h3>
      
      {stats && (
        <>
          <div className="stat-row">
            <span>Projects:</span>
            <strong>{stats.total_projects}</strong>
          </div>
          <div className="stat-row">
            <span>Earnings:</span>
            <strong>${stats.total_revenue}</strong>
          </div>
          <div className="stat-row">
            <span>This Month:</span>
            <strong>{stats.projects_this_month}</strong>
          </div>
          <div className="stat-row">
            <span>Status:</span>
            <strong>{stats.is_pro ? '⭐ Pro' : 'Free'}</strong>
          </div>
        </>
      )}

      <div className="widget-actions">
        <button className="btn-primary" onClick={() => navigate('/distribution')}>
          📤 Upload New
        </button>
        <button className="btn-secondary" onClick={() => navigate('/distribution?tab=projects')}>
          📚 View All
        </button>
      </div>
    </div>
  );
}


// ============================================================================
// OPTION 5: SIDEBAR INTEGRATION
// ============================================================================

import { Sidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';

export function SidebarNavigation({ userId }) {
  return (
    <Sidebar>
      <Menu>
        <MenuItem>🏠 Home</MenuItem>
        
        <SubMenu label="🎬 Content">
          <MenuItem>Movies</MenuItem>
          <MenuItem>Videos</MenuItem>
          <MenuItem>Music</MenuItem>
        </SubMenu>

        <SubMenu label="📤 Distribution & Monetize">
          <MenuItem icon="📤">Upload Content</MenuItem>
          <MenuItem icon="📚">My Distributions</MenuItem>
          <MenuItem icon="💰">Earnings</MenuItem>
          <MenuItem icon="⭐">Upgrade Pro</MenuItem>
        </SubMenu>

        <MenuItem>👤 Profile</MenuItem>
      </Menu>
    </Sidebar>
  );
}


// ============================================================================
// OPTION 6: TAB INTEGRATION (For existing tab component)
// ============================================================================

export function ContentTabsWithDistribution({ userId }) {
  const [activeTab, setActiveTab] = React.useState('home');

  const tabs = [
    { id: 'home', label: '🏠 Home', component: Home },
    { id: 'movies', label: '🎬 Movies', component: Movies },
    { id: 'videos', label: '🎥 Videos', component: Videos },
    { id: 'music', label: '🎵 Music', component: Music },
    { id: 'distribution', label: '📤 Distribution', component: DistributionPlatform },
    { id: 'profile', label: '👤 Profile', component: Profile }
  ];

  const ActiveComponent = tabs.find(t => t.id === activeTab)?.component || Home;

  return (
    <div className="tabs-container">
      <div className="tabs-header">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tabs-content">
        <ActiveComponent userId={userId} />
      </div>
    </div>
  );
}


// ============================================================================
// OPTION 7: MODAL/DRAWER ACCESS
// ============================================================================

export function DistributionModal({ isOpen, onClose, userId }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <DistributionPlatform userId={userId} />
      </div>
    </div>
  );
}

// Usage:
export function MainApp({ userId }) {
  const [showDistributionModal, setShowDistributionModal] = React.useState(false);

  return (
    <>
      <NavBar>
        <button 
          onClick={() => setShowDistributionModal(true)}
          className="distribution-button"
        >
          📤 Distribution
        </button>
      </NavBar>

      <DistributionModal 
        isOpen={showDistributionModal}
        onClose={() => setShowDistributionModal(false)}
        userId={userId}
      />
    </>
  );
}


// ============================================================================
// OPTION 8: FLOATING ACTION BUTTON
// ============================================================================

import styled from 'styled-components';

const FloatingButton = styled.button`
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 999;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }
`;

export function FloatingDistributionButton({ onClick }) {
  return (
    <FloatingButton onClick={onClick} title="Distribution & Monetization">
      📤
    </FloatingButton>
  );
}


// ============================================================================
// OPTION 9: FULL PAGE WITH SIDEBAR
// ============================================================================

export function DistributionPage({ userId }) {
  return (
    <div className="page-layout">
      <div className="sidebar">
        <div className="sidebar-header">📤 Distribution</div>
        <nav className="sidebar-menu">
          <a href="#dashboard">📊 Dashboard</a>
          <a href="#upload">📤 Upload</a>
          <a href="#projects">📚 My Projects</a>
          <a href="#earnings">💰 Earnings</a>
          <a href="#upgrade">⭐ Upgrade Pro</a>
          <a href="#support">🆘 Support</a>
        </nav>
      </div>

      <div className="main-content">
        <DistributionPlatform userId={userId} />
      </div>
    </div>
  );
}


// ============================================================================
// OPTION 10: QUICK BUTTON GROUPS
// ============================================================================

export function QuickActionButtons({ userId }) {
  return (
    <div className="quick-actions">
      <button className="action-btn primary" title="Upload New Content">
        <span>📤</span>
        <span>Upload</span>
      </button>
      
      <button className="action-btn secondary" title="View My Distributions">
        <span>📚</span>
        <span>Projects</span>
      </button>
      
      <button className="action-btn secondary" title="Check Earnings">
        <span>💰</span>
        <span>Earnings</span>
      </button>
      
      <button className="action-btn secondary" title="Full Distribution Platform">
        <span>📤</span>
        <span>Platform</span>
      </button>
    </div>
  );
}


// ============================================================================
// CSS STYLING FOR INTEGRATION
// ============================================================================

const styles = `
/* Navbar Styling */
.navbar {
  display: flex;
  justify-content: space-around;
  padding: 1rem;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.navbar ul {
  list-style: none;
  display: flex;
  gap: 1rem;
}

.navbar a {
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.navbar a:hover {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

/* Dashboard Widget */
.distribution-widget {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #00d4ff;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.widget-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

/* Tabs */
.tabs-header {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-button.active {
  border-bottom-color: #00d4ff;
  color: #00d4ff;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.secondary {
  background: #f0f0f0;
  color: #1e3c72;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
`;

export default styles;
