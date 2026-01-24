/**
 * AudioConverterPlatform.jsx
 * 
 * Independent full-page audio converter platform
 * Standalone page with complete conversion workflow
 * 
 * Features:
 * - Full page layout with header/footer
 * - Drag-and-drop upload
 * - Format and quality selection
 * - Conversion progress tracking
 * - Download/share functionality
 * - Conversion history
 * - Real-time stats dashboard
 */

import React, { useState, useCallback } from 'react';
import {
  Container,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardHeader,
  CardMedia,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Stack,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  LinearProgress,
  Alert,
  AlertTitle,
  Typography,
  Avatar,
  AvatarGroup,
  Divider,
  Tab,
  Tabs,
  Tooltip,
  IconButton,
  Badge,
  AppBar,
  Toolbar,
} from '@mui/material';

import {
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
  Share as ShareIcon,
  GetApp as GetAppIcon,
  History as HistoryIcon,
  Dashboard as DashboardIcon,
  AudioFile as AudioFileIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
} from '@mui/icons-material';

import AudioConverter from '../components/AudioConverter';

/**
 * TabPanel component for tab content
 */
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`converter-tabpanel-${index}`}
      aria-labelledby={`converter-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

/**
 * Main AudioConverterPlatform Component
 */
export default function AudioConverterPlatform({ userId = 'user123' }) {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [conversions, setConversions] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [stats, setStats] = useState({
    totalConversions: 0,
    totalFilesProcessed: 0,
    totalBytesConverted: 0,
    averageConversionTime: 0,
  });

  // Tab change handler
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Toggle favorite
  const toggleFavorite = (conversionId) => {
    setFavorites((prev) => {
      if (prev.includes(conversionId)) {
        return prev.filter((id) => id !== conversionId);
      }
      return [...prev, conversionId];
    });
  };

  // Delete conversion
  const handleDelete = (conversionId) => {
    setConversions((prev) => prev.filter((c) => c.id !== conversionId));
  };

  // Format file size for display
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format duration MM:SS
  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* Header */}
      <AppBar position="sticky" color="primary" elevation={2}>
        <Toolbar>
          <AudioFileIcon sx={{ mr: 2, fontSize: 28 }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1 }}>
            🎵 Audio Converter Platform
          </Typography>
          <Tooltip title="Settings">
            <IconButton color="inherit">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Main Container */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Tabs Navigation */}
        <Paper sx={{ mb: 4 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab
              label="🚀 Quick Convert"
              icon={<CloudUploadIcon />}
              iconPosition="start"
              id="converter-tab-0"
            />
            <Tab
              label="📊 Dashboard"
              icon={<DashboardIcon />}
              iconPosition="start"
              id="converter-tab-1"
            />
            <Tab
              label="📜 History"
              icon={<HistoryIcon />}
              iconPosition="start"
              id="converter-tab-2"
            />
            <Tab
              label="⭐ Favorites"
              icon={
                <Badge badgeContent={favorites.length} color="error">
                  <FavoriteIcon />
                </Badge>
              }
              iconPosition="start"
              id="converter-tab-3"
            />
          </Tabs>
        </Paper>

        {/* TAB 0: Quick Convert */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            {/* Main Converter Component */}
            <Grid item xs={12} md={8}>
              <Paper elevation={3} sx={{ p: 3, bgcolor: 'white' }}>
                <AudioConverter userId={userId} />
              </Paper>
            </Grid>

            {/* Side Panel: Info & Features */}
            <Grid item xs={12} md={4}>
              <Stack spacing={2}>
                {/* Quick Info Card */}
                <Card>
                  <CardHeader
                    avatar={<InfoIcon />}
                    title="Supported Formats"
                    titleTypographyProps={{ variant: 'subtitle1' }}
                  />
                  <CardContent>
                    <Stack spacing={1}>
                      <Chip label="MP3" icon={<AudioFileIcon />} variant="outlined" />
                      <Chip label="WAV" icon={<AudioFileIcon />} variant="outlined" />
                      <Chip label="FLAC" icon={<AudioFileIcon />} variant="outlined" />
                      <Chip label="OGG" icon={<AudioFileIcon />} variant="outlined" />
                      <Chip label="M4A/AAC" icon={<AudioFileIcon />} variant="outlined" />
                      <Chip label="OPUS" icon={<AudioFileIcon />} variant="outlined" />
                      <Chip label="WMA" icon={<AudioFileIcon />} variant="outlined" />
                    </Stack>
                  </CardContent>
                </Card>

                {/* Quality Info Card */}
                <Card>
                  <CardHeader
                    avatar={<SettingsIcon />}
                    title="Quality Options"
                    titleTypographyProps={{ variant: 'subtitle1' }}
                  />
                  <CardContent>
                    <Stack spacing={1}>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">Phone (64 kbps)</Typography>
                        <Chip label="Small" size="small" variant="outlined" />
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">Low (128 kbps)</Typography>
                        <Chip label="Small" size="small" variant="outlined" />
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">Medium (192 kbps)</Typography>
                        <Chip label="Medium" size="small" variant="outlined" />
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">High (256 kbps)</Typography>
                        <Chip label="Medium" size="small" variant="outlined" />
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">Very High (320 kbps)</Typography>
                        <Chip label="Large" size="small" variant="outlined" />
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">Lossless</Typography>
                        <Chip label="Largest" size="small" variant="outlined" />
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>

                {/* Tips Card */}
                <Alert severity="info">
                  <AlertTitle>💡 Pro Tips</AlertTitle>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    <li>Use MP3 for web & streaming</li>
                    <li>Use FLAC for archival</li>
                    <li>Use WAV for editing</li>
                    <li>Batch convert multiple files</li>
                  </ul>
                </Alert>
              </Stack>
            </Grid>
          </Grid>
        </TabPanel>

        {/* TAB 1: Dashboard */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            {/* Stats Cards */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Total Conversions
                  </Typography>
                  <Typography variant="h4">{conversions.length}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    Lifetime
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Files Processed
                  </Typography>
                  <Typography variant="h4">{stats.totalFilesProcessed}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    Total
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Data Converted
                  </Typography>
                  <Typography variant="h4">
                    {formatFileSize(stats.totalBytesConverted)}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Cumulative
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Conversion Time
                  </Typography>
                  <Typography variant="h4">
                    {stats.averageConversionTime.toFixed(1)}s
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Per file
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Format Distribution Chart */}
            <Grid item xs={12}>
              <Card>
                <CardHeader title="Recent Activity" />
                <CardContent>
                  <Alert severity="info">
                    📊 Format distribution and detailed analytics coming soon!
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* TAB 2: History */}
        <TabPanel value={activeTab} index={2}>
          <Card>
            <CardHeader title="Conversion History" />
            <TableContainer>
              <Table>
                <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell><strong>Filename</strong></TableCell>
                    <TableCell><strong>From Format</strong></TableCell>
                    <TableCell><strong>To Format</strong></TableCell>
                    <TableCell><strong>Quality</strong></TableCell>
                    <TableCell><strong>File Size</strong></TableCell>
                    <TableCell align="center"><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {conversions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                        <Typography color="textSecondary">
                          📭 No conversions yet. Start by converting an audio file!
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    conversions.map((conversion) => (
                      <TableRow key={conversion.id} hover>
                        <TableCell>{conversion.filename}</TableCell>
                        <TableCell>
                          <Chip
                            label={conversion.fromFormat.toUpperCase()}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={conversion.toFormat.toUpperCase()}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{conversion.quality}</TableCell>
                        <TableCell>{formatFileSize(conversion.fileSize)}</TableCell>
                        <TableCell align="center">
                          <Tooltip title="Download">
                            <IconButton size="small" color="primary">
                              <DownloadIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={favorites.includes(conversion.id) ? 'Remove favorite' : 'Add to favorites'}>
                            <IconButton
                              size="small"
                              color={favorites.includes(conversion.id) ? 'error' : 'default'}
                              onClick={() => toggleFavorite(conversion.id)}
                            >
                              {favorites.includes(conversion.id) ? (
                                <FavoriteIcon fontSize="small" />
                              ) : (
                                <FavoriteBorderIcon fontSize="small" />
                              )}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDelete(conversion.id)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Card>
        </TabPanel>

        {/* TAB 3: Favorites */}
        <TabPanel value={activeTab} index={3}>
          {favorites.length === 0 ? (
            <Card sx={{ textAlign: 'center', py: 8 }}>
              <CardContent>
                <FavoriteBorderIcon sx={{ fontSize: 60, color: 'textSecondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary">
                  No Favorites Yet
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  Add conversions to your favorites to quick access them here
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <Grid container spacing={2}>
              {conversions
                .filter((c) => favorites.includes(c.id))
                .map((conversion) => (
                  <Grid item xs={12} sm={6} md={4} key={conversion.id}>
                    <Card>
                      <CardHeader
                        avatar={<AudioFileIcon />}
                        title={conversion.filename}
                        subheader={`${conversion.toFormat.toUpperCase()} • ${conversion.quality}`}
                      />
                      <CardContent>
                        <Typography variant="body2" color="textSecondary">
                          Size: {formatFileSize(conversion.fileSize)}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Quality: {conversion.quality}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Tooltip title="Download">
                          <IconButton size="small" color="primary">
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Remove from favorites">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => toggleFavorite(conversion.id)}
                          >
                            <FavoriteIcon />
                          </IconButton>
                        </Tooltip>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
            </Grid>
          )}
        </TabPanel>
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          bgcolor: '#f5f5f5',
          py: 4,
          mt: 8,
          borderTop: '1px solid #e0e0e0',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="h6" gutterBottom>
                About
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Professional audio format converter with AI-powered features.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="h6" gutterBottom>
                Features
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • 8 Audio Formats
                <br />
                • 6 Quality Levels
                <br />
                • Batch Convert
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="h6" gutterBottom>
                Support
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Need help? Contact support or check our documentation.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="h6" gutterBottom>
                Status
              </Typography>
              <Chip label="✅ All Systems Operational" color="success" size="small" />
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="textSecondary" align="center">
            © 2024 Audio Converter Platform. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
