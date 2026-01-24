import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import axios from 'axios';

const AudioConverter = ({ open = false, onClose }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [selectedFormat, setSelectedFormat] = useState('mp3');
  const [selectedBitrate, setSelectedBitrate] = useState('256');
  const [loading, setLoading] = useState(false);
  const [converting, setConverting] = useState(false);
  const [error, setError] = useState(null);
  const [convertedFile, setConvertedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [fileInfo, setFileInfo] = useState(null);
  const [conversionHistory, setConversionHistory] = useState([]);

  const SUPPORTED_FORMATS = [
    { name: 'MP3', value: 'mp3', lossless: false },
    { name: 'WAV', value: 'wav', lossless: true },
    { name: 'FLAC', value: 'flac', lossless: true },
    { name: 'OGG Vorbis', value: 'ogg', lossless: false },
    { name: 'M4A/AAC', value: 'm4a', lossless: false },
    { name: 'AAC', value: 'aac', lossless: false },
    { name: 'Opus', value: 'opus', lossless: false },
    { name: 'WMA', value: 'wma', lossless: false },
  ];

  const BITRATES = [
    { label: 'Phone (64 kbps)', value: '64', quality: 'low' },
    { label: 'Good (128 kbps)', value: '128', quality: 'good' },
    { label: 'Very Good (192 kbps)', value: '192', quality: 'very_good' },
    { label: 'Excellent (256 kbps)', value: '256', quality: 'excellent' },
    { label: 'Highest (320 kbps)', value: '320', quality: 'highest' },
    { label: 'Lossless', value: 'lossless', quality: 'lossless' },
  ];

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', 'user123'); // Use actual user ID

      const response = await axios.post('/api/v1/audio/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadedFile(response.data);
      setFileInfo({
        name: response.data.filename,
        format: response.data.format.toUpperCase(),
        size: formatFileSize(response.data.file_size),
        duration: formatDuration(response.data.duration),
        bitrate: response.data.bitrate ? `${response.data.bitrate} kbps` : 'N/A',
        sampleRate: response.data.sample_rate ? `${response.data.sample_rate} Hz` : 'N/A',
        channels: response.data.channels === 1 ? 'Mono' : `${response.data.channels}ch`,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload audio file');
    } finally {
      setLoading(false);
    }
  };

  const handleConvert = async () => {
    if (!uploadedFile) {
      setError('Please upload an audio file first');
      return;
    }

    setConverting(true);
    setError(null);

    try {
      const response = await axios.post('/api/v1/audio/convert', {
        user_id: 'user123',
        audio_file_id: uploadedFile.id,
        target_format: selectedFormat,
        target_bitrate: selectedBitrate,
      });

      setConvertedFile(response.data);
      setConversionHistory([response.data, ...conversionHistory]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Conversion failed');
    } finally {
      setConverting(false);
    }
  };

  const handleDownload = (filename) => {
    // In real app, this would trigger a server-side download
    const link = document.createElement('a');
    link.href = `/api/v1/audio/download/${filename}`;
    link.download = filename;
    link.click();
  };

  const handleDelete = async (fileId) => {
    try {
      await axios.delete(`/api/v1/audio/delete/${fileId}`);
      setConversionHistory(conversionHistory.filter((f) => f.id !== fileId));
    } catch (err) {
      setError('Failed to delete file');
    }
  };

  const handleReset = () => {
    setUploadedFile(null);
    setFileInfo(null);
    setConvertedFile(null);
    setError(null);
    setSelectedFormat('mp3');
    setSelectedBitrate('256');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>🎵 Audio Converter</DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {/* Upload Section */}
        {!uploadedFile ? (
          <Paper
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            sx={{
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              border: '2px dashed',
              borderColor: dragActive ? '#1976d2' : '#ccc',
              backgroundColor: dragActive ? '#f5f5f5' : '#fafafa',
              transition: 'all 0.3s',
              mb: 3,
            }}
          >
            <CloudUploadIcon sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
            <Typography variant="h6">Drag & drop your audio file here</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              Supported: MP3, WAV, FLAC, OGG, M4A, AAC, WMA, OPUS
            </Typography>
            <Button
              variant="contained"
              sx={{ mt: 2 }}
              component="label"
            >
              Browse Files
              <input
                type="file"
                hidden
                accept="audio/*"
                onChange={(e) => handleFileUpload(e.target.files[0])}
              />
            </Button>
          </Paper>
        ) : (
          <>
            {/* File Info */}
            <Card sx={{ mb: 3, backgroundColor: '#f5f5f5' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CheckCircleIcon sx={{ color: 'green', mr: 2 }} />
                  <Typography variant="h6">{fileInfo.name}</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Format</Typography>
                    <Typography variant="body2">{fileInfo.format}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Size</Typography>
                    <Typography variant="body2">{fileInfo.size}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Duration</Typography>
                    <Typography variant="body2">{fileInfo.duration}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Bitrate</Typography>
                    <Typography variant="body2">{fileInfo.bitrate}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Sample Rate</Typography>
                    <Typography variant="body2">{fileInfo.sampleRate}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Channels</Typography>
                    <Typography variant="body2">{fileInfo.channels}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Conversion Options */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Convert To</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Format</InputLabel>
                      <Select
                        value={selectedFormat}
                        label="Format"
                        onChange={(e) => setSelectedFormat(e.target.value)}
                      >
                        {SUPPORTED_FORMATS.map((fmt) => (
                          <MenuItem key={fmt.value} value={fmt.value}>
                            {fmt.name}
                            {fmt.lossless && ' (Lossless)'}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Quality</InputLabel>
                      <Select
                        value={selectedBitrate}
                        label="Quality"
                        onChange={(e) => setSelectedBitrate(e.target.value)}
                      >
                        {BITRATES.map((br) => (
                          <MenuItem key={br.value} value={br.value}>
                            {br.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Converted File */}
            {convertedFile && (
              <Card sx={{ mb: 3, backgroundColor: '#e8f5e9' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CheckCircleIcon sx={{ color: 'green', mr: 2 }} />
                    <Typography variant="h6">Conversion Complete!</Typography>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="caption" color="textSecondary">Filename</Typography>
                      <Typography variant="body2">{convertedFile.filename}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="caption" color="textSecondary">Size</Typography>
                      <Typography variant="body2">{formatFileSize(convertedFile.file_size)}</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
                <CardActions>
                  <Button
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload(convertedFile.filename)}
                  >
                    Download
                  </Button>
                </CardActions>
              </Card>
            )}

            {/* Conversion History */}
            {conversionHistory.length > 0 && (
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Conversion History</Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Filename</TableCell>
                          <TableCell>Format</TableCell>
                          <TableCell>Bitrate</TableCell>
                          <TableCell>Size</TableCell>
                          <TableCell align="right">Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {conversionHistory.map((file) => (
                          <TableRow key={file.id}>
                            <TableCell>{file.filename}</TableCell>
                            <TableCell>
                              <Chip
                                label={file.format.toUpperCase()}
                                size="small"
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>{file.bitrate} kbps</TableCell>
                            <TableCell>{formatFileSize(file.file_size)}</TableCell>
                            <TableCell align="right">
                              <Tooltip title="Download">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDownload(file.filename)}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDelete(file.id)}
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Tooltip>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {converting && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CircularProgress size={24} sx={{ mr: 2 }} />
              <Typography>Converting audio...</Typography>
            </Box>
            <LinearProgress />
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {uploadedFile && !convertedFile && (
          <Button
            onClick={handleReset}
            variant="outlined"
            disabled={converting}
          >
            Reset
          </Button>
        )}
        {uploadedFile && (
          <Button
            onClick={handleConvert}
            variant="contained"
            disabled={converting || loading}
          >
            {converting ? 'Converting...' : 'Convert'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default AudioConverter;
