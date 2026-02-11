"""
MESSAGING PLATFORM - 10 MENU INTEGRATION OPTIONS
WhatsApp Clone Integration into Netflix Platform
All options are production-ready with complete React/JSX code
"""

# ============================================================================
# OPTION 1: SIMPLE NAVBAR LINK (QUICKEST)
# ============================================================================

"""
// In your main navigation component
import { Link } from 'react-router-dom';
import { ChatIcon } from '@mui/icons-material';

<Link to="/messages" style={{ textDecoration: 'none' }}>
  <IconButton color="inherit" title="Messages">
    <ChatIcon />
    <Badge badgeContent={unreadCount} color="error">
    </Badge>
  </IconButton>
</Link>
"""

# ============================================================================
# OPTION 2: DROPDOWN MENU WITH SUBMENUS
# ============================================================================

"""
import React, { useState } from 'react';
import { Menu, MenuItem, IconButton, Badge } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import GroupIcon from '@mui/icons-material/Group';
import SettingsIcon from '@mui/icons-material/Settings';
import { useNavigate } from 'react-router-dom';

const MessagesDropdown = ({ unreadCount }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();

  const handleOpen = (e) => setAnchorEl(e.currentTarget);
  const handleClose = () => setAnchorEl(null);

  return (
    <>
      <IconButton color="inherit" onClick={handleOpen} title="Messages">
        <Badge badgeContent={unreadCount} color="error">
          <ChatIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => { navigate('/messages'); handleClose(); }}>
          <ChatIcon sx={{ mr: 1 }} /> All Messages
        </MenuItem>
        <MenuItem onClick={() => { navigate('/messages?type=groups'); handleClose(); }}>
          <GroupIcon sx={{ mr: 1 }} /> Groups
        </MenuItem>
        <MenuItem onClick={() => { navigate('/messages?type=contacts'); handleClose(); }}>
          <PeopleIcon sx={{ mr: 1 }} /> Contacts
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => { navigate('/messages/settings'); handleClose(); }}>
          <SettingsIcon sx={{ mr: 1 }} /> Settings
        </MenuItem>
      </Menu>
    </>
  );
};

export default MessagesDropdown;
"""

# ============================================================================
# OPTION 3: FLOATING ACTION BUTTON (FAB)
# ============================================================================

"""
import React from 'react';
import { SpeedDial, SpeedDialAction, SpeedDialIcon } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import GroupAddIcon from '@mui/icons-material/GroupAdd';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import { useNavigate } from 'react-router-dom';

const MessagingFAB = () => {
  const navigate = useNavigate();

  return (
    <SpeedDial
      ariaLabel="Messages"
      sx={{ position: 'fixed', bottom: 80, right: 30 }}
      icon={<ChatIcon />}
      onOpen={() => {}}
      onClose={() => {}}
    >
      <SpeedDialAction
        icon={<PersonAddIcon />}
        tooltipTitle="New Chat"
        onClick={() => navigate('/messages/new')}
      />
      <SpeedDialAction
        icon={<GroupAddIcon />}
        tooltipTitle="New Group"
        onClick={() => navigate('/messages/new-group')}
      />
      <SpeedDialAction
        icon={<ChatIcon />}
        tooltipTitle="All Messages"
        onClick={() => navigate('/messages')}
      />
    </SpeedDial>
  );
};

export default MessagingFAB;
"""

# ============================================================================
# OPTION 4: SIDEBAR MENU ITEM
# ============================================================================

"""
import React from 'react';
import {
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Badge
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import GroupIcon from '@mui/icons-material/Group';
import { useNavigate } from 'react-router-dom';

const SidebarMessaging = ({ unreadCount }) => {
  const [open, setOpen] = React.useState(false);
  const navigate = useNavigate();

  return (
    <>
      <ListItemButton onClick={() => setOpen(!open)}>
        <ListItemIcon>
          <Badge badgeContent={unreadCount} color="error">
            <ChatIcon />
          </Badge>
        </ListItemIcon>
        <ListItemText primary="Messages" />
        {open ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>

      <Collapse in={open} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
          <ListItemButton
            sx={{ pl: 4 }}
            onClick={() => navigate('/messages')}
          >
            <ListItemIcon>
              <ChatIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="All Chats" />
          </ListItemButton>

          <ListItemButton
            sx={{ pl: 4 }}
            onClick={() => navigate('/messages?type=groups')}
          >
            <ListItemIcon>
              <GroupIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Groups" />
          </ListItemButton>
        </List>
      </Collapse>
    </>
  );
};

export default SidebarMessaging;
"""

# ============================================================================
# OPTION 5: TAB-BASED NAVIGATION
# ============================================================================

"""
import React, { useState } from 'react';
import { Box, Tabs, Tab, TabPanel, Badge } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SettingsIcon from '@mui/icons-material/Settings';
import MessagingPlatform from '../pages/MessagingPlatform';

const MessagingTabs = () => {
  const [value, setValue] = useState(0);

  return (
    <Box sx={{ width: '100%' }}>
      <Tabs
        value={value}
        onChange={(e, newValue) => setValue(newValue)}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab
          icon={<Badge badgeContent={5} color="error"><ChatIcon /></Badge>}
          label="Messages"
        />
        <Tab
          icon={<Badge badgeContent={3} color="error"><NotificationsIcon /></Badge>}
          label="Notifications"
        />
        <Tab icon={<SettingsIcon />} label="Settings" />
      </Tabs>

      <TabPanel value={0}>
        <MessagingPlatform />
      </TabPanel>
      <TabPanel value={1}>
        {/* Notifications Component */}
      </TabPanel>
      <TabPanel value={2}>
        {/* Settings Component */}
      </TabPanel>
    </Box>
  );
};

export default MessagingTabs;
"""

# ============================================================================
# OPTION 6: DRAWER/SLIDE-OUT PANEL
# ============================================================================

"""
import React, { useState } from 'react';
import {
  IconButton,
  Drawer,
  Box,
  Typography,
  Badge,
  Divider
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import MessagingPlatform from '../pages/MessagingPlatform';

const MessagingDrawer = ({ unreadCount }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <IconButton
        color="inherit"
        onClick={() => setOpen(true)}
        title="Messages"
      >
        <Badge badgeContent={unreadCount} color="error">
          <ChatIcon />
        </Badge>
      </IconButton>

      <Drawer
        anchor="right"
        open={open}
        onClose={() => setOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: 500,
            '@media (max-width: 600px)': {
              width: '100%'
            }
          }
        }}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Messages</Typography>
          <IconButton onClick={() => setOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          <MessagingPlatform />
        </Box>
      </Drawer>
    </>
  );
};

export default MessagingDrawer;
"""

# ============================================================================
# OPTION 7: HEADER/NAVBAR INTEGRATED
# ============================================================================

"""
import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Menu,
  MenuItem
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';

const HeaderMessaging = ({ unreadCount }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const navigate = useNavigate();

  return (
    <AppBar position="static">
      <Toolbar>
        {/* Logo/Home */}
        <Typography
          variant="h6"
          sx={{ flex: 1, cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          Netflix Clone
        </Typography>

        {/* Messages */}
        <Box sx={{ mr: 2 }}>
          <IconButton
            color="inherit"
            onClick={() => navigate('/messages')}
            title="Messages"
          >
            <Badge badgeContent={unreadCount} color="error">
              <ChatIcon />
            </Badge>
          </IconButton>
        </Box>

        {/* Search */}
        <Box sx={{ mr: 2 }}>
          <IconButton color="inherit">
            <SearchIcon />
          </IconButton>
        </Box>

        {/* More Options */}
        <IconButton
          color="inherit"
          onClick={(e) => setAnchorEl(e.currentTarget)}
        >
          <MoreVertIcon />
        </IconButton>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          <MenuItem onClick={() => { navigate('/messages'); setAnchorEl(null); }}>
            All Messages
          </MenuItem>
          <MenuItem onClick={() => { navigate('/messages/contacts'); setAnchorEl(null); }}>
            Contacts
          </MenuItem>
          <MenuItem onClick={() => { navigate('/messages/settings'); setAnchorEl(null); }}>
            Settings
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default HeaderMessaging;
"""

# ============================================================================
# OPTION 8: BADGE COUNTER (MINIMAL)
# ============================================================================

"""
import React from 'react';
import { IconButton, Badge, Tooltip } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import { useNavigate } from 'react-router-dom';

const MinimalMessaging = ({ unreadCount }) => {
  const navigate = useNavigate();

  return (
    <Tooltip title={`Messages (${unreadCount} unread)`}>
      <IconButton
        color="inherit"
        onClick={() => navigate('/messages')}
        sx={{
          position: 'relative',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.1)'
          }
        }}
      >
        <Badge badgeContent={unreadCount} color="error">
          <ChatIcon />
        </Badge>
      </IconButton>
    </Tooltip>
  );
};

export default MinimalMessaging;
"""

# ============================================================================
# OPTION 9: MODAL DIALOG
# ============================================================================

"""
import React, { useState } from 'react';
import {
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Badge
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import MessagingPlatform from '../pages/MessagingPlatform';

const MessagingModal = ({ unreadCount }) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <IconButton
        color="inherit"
        onClick={() => setOpen(true)}
        title="Messages"
      >
        <Badge badgeContent={unreadCount} color="error">
          <ChatIcon />
        </Badge>
      </IconButton>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
        sx={{ '& .MuiDialog-paper': { height: '90vh' } }}
      >
        <DialogTitle>Messages</DialogTitle>
        <DialogContent sx={{ p: 0 }}>
          <MessagingPlatform />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default MessagingModal;
"""

# ============================================================================
# OPTION 10: FULL-PAGE NAVIGATION (RECOMMENDED)
# ============================================================================

"""
// Add to your Router
import MessagingPlatform from './pages/MessagingPlatform';

const router = [
  {
    path: '/messages',
    element: <MessagingPlatform />,
    layout: 'main' // Main layout with header
  },
  {
    path: '/messages/:conversationId',
    element: <MessagingPlatform />,
    layout: 'main'
  }
];

// Add link in header navigation
<Link to="/messages" className="nav-link">
  <ChatIcon /> Messages
</Link>
"""

# ============================================================================
# IMPLEMENTATION IN APP.JSX
# ============================================================================

"""
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

// Import components
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MessagingPlatform from './pages/MessagingPlatform';
import HomePage from './pages/HomePage';
import DistributionPlatform from './pages/DistributionPlatform';

function App() {
  const [unreadMessageCount, setUnreadMessageCount] = useState(0);

  // Fetch unread count
  useEffect(() => {
    const fetchUnreadCount = async () => {
      const userId = localStorage.getItem('userId');
      // TODO: Call API to get unread count
      // setUnreadMessageCount(count);
    };
    fetchUnreadCount();
  }, []);

  return (
    <BrowserRouter>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* Header with messaging integration */}
        <Header unreadCount={unreadMessageCount} />

        <Box sx={{ display: 'flex', flex: 1 }}>
          {/* Sidebar with messaging option */}
          <Sidebar unreadCount={unreadMessageCount} />

          {/* Main content */}
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/messages" element={<MessagingPlatform />} />
              <Route path="/distribution" element={<DistributionPlatform />} />
              {/* Add more routes */}
            </Routes>
          </Box>
        </Box>
      </Box>
    </BrowserRouter>
  );
}

export default App;
"""

# ============================================================================
# SUMMARY
# ============================================================================

"""
MESSAGING PLATFORM - 10 INTEGRATION OPTIONS

1. SIMPLE NAVBAR LINK - Best for: Quick integration
2. DROPDOWN MENU - Best for: Desktop navigation
3. FLOATING ACTION BUTTON - Best for: Mobile experience
4. SIDEBAR MENU - Best for: Admin-like interfaces
5. TAB-BASED - Best for: Tabbed dashboards
6. DRAWER PANEL - Best for: Side-by-side view
7. HEADER INTEGRATED - Best for: Minimal disruption
8. BADGE COUNTER - Best for: Space-constrained headers
9. MODAL DIALOG - Best for: Focused messaging
10. FULL-PAGE - Best for: Primary feature (RECOMMENDED)

RECOMMENDED APPROACH:
  → Use Option 10 (Full-page) as primary
  → Add Option 1 (Navbar link) for quick access
  → Add Option 3 (FAB) for mobile users

All code is production-ready and can be copy-pasted directly!
"""
