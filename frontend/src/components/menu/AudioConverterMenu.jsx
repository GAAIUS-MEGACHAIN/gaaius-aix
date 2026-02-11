import React, { useState } from 'react';
import AudioConverter from './AudioConverter';
import {
  // Option 1: Navbar Button
  AppBar,
  Toolbar,
  Button,
  // Option 2: Sidebar Menu
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  // Option 3: FAB
  Fab,
  // Option 4: Dropdown
  Menu,
  MenuItem,
  // Option 5: Tabs
  Tabs,
  Tab,
  // Option 6: Card Grid
  Grid,
  Card,
  CardContent,
  CardActionArea,
  // Option 7: Floating Menu
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  // Option 8: Badge
  Badge,
  Icon,
  // Option 9: Chip
  Chip,
  Stack,
  // Option 10: Modal
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
} from '@mui/material';
import {
  Music as MusicIcon,
  Convert as ConvertIcon,
  AudioFile as AudioFileIcon,
  Queue as QueueIcon,
} from '@mui/icons-material';

export const AudioConverterMenuOptions = {
  // OPTION 1: Navbar Button (Top-right in header)
  Option1NavbarButton: () => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <Button
          color="inherit"
          startIcon={<ConvertIcon />}
          onClick={() => setOpen(true)}
          sx={{ mr: 2 }}
        >
          Audio Converter
        </Button>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 2: Sidebar Menu Item
  Option2SidebarMenu: () => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <ListItem
          button
          onClick={() => setOpen(true)}
          sx={{
            '&:hover': { backgroundColor: '#f5f5f5' },
          }}
        >
          <ListItemIcon>
            <ConvertIcon />
          </ListItemIcon>
          <ListItemText
            primary="Audio Converter"
            secondary="Convert audio formats"
          />
        </ListItem>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 3: Floating Action Button (Bottom-right)
  Option3FloatingButton: () => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <Fab
          color="primary"
          aria-label="convert audio"
          onClick={() => setOpen(true)}
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            zIndex: 999,
          }}
        >
          <ConvertIcon />
        </Fab>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 4: Dropdown Menu
  Option4DropdownMenu: () => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [open, setOpen] = useState(false);

    return (
      <>
        <Button
          onClick={(e) => setAnchorEl(e.currentTarget)}
          endIcon={<ConvertIcon />}
        >
          Tools
        </Button>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          <MenuItem onClick={() => { setOpen(true); setAnchorEl(null); }}>
            <AudioFileIcon sx={{ mr: 2 }} />
            Audio Converter
          </MenuItem>
        </Menu>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 5: Tabbed Interface
  Option5TabbedInterface: () => {
    const [tabValue, setTabValue] = useState(0);

    return (
      <Box>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Upload" />
          <Tab label="Audio Converter" icon={<ConvertIcon />} />
          <Tab label="History" />
        </Tabs>
        {tabValue === 1 && <AudioConverter open={true} onClose={() => {}} />}
      </Box>
    );
  },

  // OPTION 6: Card Grid (Dashboard)
  Option6CardGrid: () => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardActionArea onClick={() => setOpen(true)}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <ConvertIcon
                    sx={{
                      fontSize: 48,
                      color: '#1976d2',
                      mb: 2,
                    }}
                  />
                  <Typography variant="h6">Audio Converter</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Convert between MP3, WAV, FLAC, OGG, M4A, AAC & more
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        </Grid>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 7: Speed Dial (Floating Menu)
  Option7SpeedDial: () => {
    const [open, setOpen] = useState(false);
    const [converterOpen, setConverterOpen] = useState(false);

    return (
      <>
        <SpeedDial
          ariaLabel="Tools"
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            zIndex: 999,
          }}
          icon={<SpeedDialIcon />}
        >
          <SpeedDialAction
            icon={<ConvertIcon />}
            tooltipTitle="Audio Converter"
            onClick={() => setConverterOpen(true)}
          />
          <SpeedDialAction
            icon={<MusicIcon />}
            tooltipTitle="Music Library"
          />
        </SpeedDial>
        <AudioConverter open={converterOpen} onClose={() => setConverterOpen(false)} />
      </>
    );
  },

  // OPTION 8: Badge Notification
  Option8BadgeNotification: () => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <Badge badgeContent={0} color="primary">
          <Button
            startIcon={<ConvertIcon />}
            onClick={() => setOpen(true)}
            variant="outlined"
          >
            Audio Tools
          </Button>
        </Badge>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 9: Chip Group (Horizontal)
  Option9ChipGroup: () => {
    const [open, setOpen] = useState(false);

    return (
      <>
        <Stack direction="row" spacing={1}>
          <Chip
            icon={<ConvertIcon />}
            label="Audio Converter"
            onClick={() => setOpen(true)}
            variant="outlined"
            color="primary"
          />
          <Chip
            icon={<MusicIcon />}
            label="Music Library"
            variant="outlined"
          />
        </Stack>
        <AudioConverter open={open} onClose={() => setOpen(false)} />
      </>
    );
  },

  // OPTION 10: Modal Launcher (Card with Info)
  Option10ModalLauncher: () => {
    const [infoOpen, setInfoOpen] = useState(false);
    const [converterOpen, setConverterOpen] = useState(false);

    return (
      <>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setInfoOpen(true)}
        >
          🎵 Audio Converter
        </Button>

        <Dialog open={infoOpen} onClose={() => setInfoOpen(false)}>
          <DialogTitle>Audio Converter</DialogTitle>
          <DialogContent>
            <Typography variant="body2" sx={{ mt: 2 }}>
              Convert your audio files to multiple formats with custom quality settings.
            </Typography>
            <Typography variant="caption" sx={{ mt: 2, display: 'block' }}>
              Supported: MP3 • WAV • FLAC • OGG • M4A • AAC • WMA • OPUS
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setInfoOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                setInfoOpen(false);
                setConverterOpen(true);
              }}
              variant="contained"
            >
              Open Converter
            </Button>
          </DialogActions>
        </Dialog>

        <AudioConverter open={converterOpen} onClose={() => setConverterOpen(false)} />
      </>
    );
  },
};

// Complete Navbar Integration Example
export const AudioConverterNavbar = () => {
  const [converterOpen, setConverterOpen] = useState(false);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Platform
          </Typography>
          <Button
            color="inherit"
            startIcon={<ConvertIcon />}
            onClick={() => setConverterOpen(true)}
          >
            Audio Converter
          </Button>
        </Toolbar>
      </AppBar>
      <AudioConverter open={converterOpen} onClose={() => setConverterOpen(false)} />
    </>
  );
};

// Complete Sidebar Integration Example
export const AudioConverterSidebar = () => {
  const [converterOpen, setConverterOpen] = useState(false);

  return (
    <>
      <Drawer variant="permanent" anchor="left">
        <List>
          <ListItem
            button
            onClick={() => setConverterOpen(true)}
          >
            <ListItemIcon>
              <ConvertIcon />
            </ListItemIcon>
            <ListItemText primary="Audio Converter" />
          </ListItem>
        </List>
      </Drawer>
      <AudioConverter open={converterOpen} onClose={() => setConverterOpen(false)} />
    </>
  );
};

export default AudioConverterMenuOptions;
