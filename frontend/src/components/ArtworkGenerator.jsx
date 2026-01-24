import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Check as CheckIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import axios from 'axios';

/**
 * ArtworkGenerator Component
 * Generates AI artwork for music, videos, and movies
 * Uses Replicate API with Stable Diffusion models
 */

const ArtworkGenerator = ({ uploadType = 'music', uploadTitle = '', onSelect }) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedArtwork, setSelectedArtwork] = useState(null);
  const [generatedArtworks, setGeneratedArtworks] = useState([]);
  
  // Form fields
  const [formData, setFormData] = useState({
    uploadType: uploadType,
    title: uploadTitle,
    artist: '',
    genre: 'electronic',
    mood: 'energetic',
    style: 'professional',
    description: '',
  });

  const handleOpen = () => {
    setError(null);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const generateArtwork = async () => {
    setLoading(true);
    setError(null);

    try {
      let endpoint = '';
      let payload = {};

      switch (formData.uploadType) {
        case 'music':
          endpoint = '/api/v1/artwork/music-cover';
          payload = {
            user_id: localStorage.getItem('userId') || 'user-' + Math.random(),
            song_title: formData.title,
            artist_name: formData.artist,
            genre: formData.genre,
            mood: formData.mood,
            style: formData.style,
          };
          break;

        case 'video':
          endpoint = '/api/v1/artwork/video-thumbnail';
          payload = {
            user_id: localStorage.getItem('userId') || 'user-' + Math.random(),
            video_title: formData.title,
            description: formData.description,
            style: formData.style,
          };
          break;

        case 'movie':
          endpoint = '/api/v1/artwork/movie-poster';
          payload = {
            user_id: localStorage.getItem('userId') || 'user-' + Math.random(),
            movie_title: formData.title,
            genre: formData.genre,
            mood: formData.mood,
            description: formData.description,
          };
          break;

        default:
          throw new Error('Invalid upload type');
      }

      const response = await axios.post(endpoint, payload);
      setGeneratedArtworks(response.data);
      setError(null);

    } catch (err) {
      console.error('Error generating artwork:', err);
      setError(err.response?.data?.detail || 'Failed to generate artwork');
      setGeneratedArtworks([]);
    } finally {
      setLoading(false);
    }
  };

  const selectArtwork = (artwork) => {
    setSelectedArtwork(artwork.id);
    if (onSelect) {
      onSelect(artwork);
    }
  };

  const downloadArtwork = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const deleteArtwork = async (artworkId) => {
    try {
      await axios.delete(`/api/v1/artwork/artwork/${artworkId}`);
      setGeneratedArtworks(prev => prev.filter(art => art.id !== artworkId));
    } catch (err) {
      console.error('Error deleting artwork:', err);
      setError('Failed to delete artwork');
    }
  };

  return (
    <>
      {/* Button to open generator */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleOpen}
        sx={{ mb: 2 }}
      >
        🎨 Generate AI Artwork
      </Button>

      {/* Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          AI Artwork Generator - {uploadType.charAt(0).toUpperCase() + uploadType.slice(1)}
        </DialogTitle>

        <DialogContent sx={{ pt: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {generatedArtworks.length === 0 && !loading && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generate Artwork for Your {uploadType === 'music' ? 'Song' : uploadType === 'video' ? 'Video' : 'Movie'}
              </Typography>

              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                {/* Common fields */}
                <TextField
                  label="Title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  fullWidth
                  required
                  placeholder={
                    uploadType === 'music' ? 'Song Title' :
                    uploadType === 'video' ? 'Video Title' :
                    'Movie Title'
                  }
                />

                {/* Music-specific fields */}
                {uploadType === 'music' && (
                  <>
                    <TextField
                      label="Artist Name"
                      name="artist"
                      value={formData.artist}
                      onChange={handleInputChange}
                      fullWidth
                      required
                    />

                    <FormControl fullWidth>
                      <InputLabel>Genre</InputLabel>
                      <Select
                        name="genre"
                        value={formData.genre}
                        onChange={handleInputChange}
                        label="Genre"
                      >
                        <MenuItem value="electronic">Electronic</MenuItem>
                        <MenuItem value="hip-hop">Hip-Hop</MenuItem>
                        <MenuItem value="rock">Rock</MenuItem>
                        <MenuItem value="pop">Pop</MenuItem>
                        <MenuItem value="jazz">Jazz</MenuItem>
                        <MenuItem value="classical">Classical</MenuItem>
                        <MenuItem value="ambient">Ambient</MenuItem>
                        <MenuItem value="indie">Indie</MenuItem>
                      </Select>
                    </FormControl>
                  </>
                )}

                {/* Video-specific fields */}
                {uploadType === 'video' && (
                  <TextField
                    label="Description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    fullWidth
                    multiline
                    rows={3}
                    required
                    placeholder="Describe what the video is about"
                  />
                )}

                {/* Movie-specific fields */}
                {uploadType === 'movie' && (
                  <>
                    <FormControl fullWidth>
                      <InputLabel>Genre</InputLabel>
                      <Select
                        name="genre"
                        value={formData.genre}
                        onChange={handleInputChange}
                        label="Genre"
                      >
                        <MenuItem value="drama">Drama</MenuItem>
                        <MenuItem value="action">Action</MenuItem>
                        <MenuItem value="horror">Horror</MenuItem>
                        <MenuItem value="comedy">Comedy</MenuItem>
                        <MenuItem value="thriller">Thriller</MenuItem>
                        <MenuItem value="sci-fi">Sci-Fi</MenuItem>
                        <MenuItem value="fantasy">Fantasy</MenuItem>
                      </Select>
                    </FormControl>

                    <TextField
                      label="Description"
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      fullWidth
                      multiline
                      rows={3}
                      required
                      placeholder="Plot summary or description"
                    />
                  </>
                )}

                {/* Common optional fields */}
                {uploadType !== 'video' && (
                  <FormControl fullWidth>
                    <InputLabel>Mood</InputLabel>
                    <Select
                      name="mood"
                      value={formData.mood}
                      onChange={handleInputChange}
                      label="Mood"
                    >
                      <MenuItem value="energetic">Energetic</MenuItem>
                      <MenuItem value="calm">Calm</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="bright">Bright</MenuItem>
                      <MenuItem value="melancholic">Melancholic</MenuItem>
                      <MenuItem value="dramatic">Dramatic</MenuItem>
                    </Select>
                  </FormControl>
                )}

                <FormControl fullWidth>
                  <InputLabel>Style</InputLabel>
                  <Select
                    name="style"
                    value={formData.style}
                    onChange={handleInputChange}
                    label="Style"
                  >
                    <MenuItem value="professional">Professional</MenuItem>
                    <MenuItem value="abstract">Abstract</MenuItem>
                    <MenuItem value="cinematic">Cinematic</MenuItem>
                    <MenuItem value="vintage">Vintage</MenuItem>
                    <MenuItem value="modern">Modern</MenuItem>
                    <MenuItem value="minimal">Minimal</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          )}

          {/* Generated Artworks Grid */}
          {generatedArtworks.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 2 }}>
                Generated Artworks (Select One)
              </Typography>

              <Grid container spacing={2}>
                {generatedArtworks.map((artwork) => (
                  <Grid item xs={12} sm={6} key={artwork.id}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        border: selectedArtwork === artwork.id ? '3px solid #1976d2' : 'none',
                        transition: 'all 0.3s',
                        '&:hover': {
                          boxShadow: 6,
                          transform: 'translateY(-4px)',
                        },
                      }}
                      onClick={() => selectArtwork(artwork)}
                    >
                      <CardMedia
                        component="img"
                        height={uploadType === 'video' ? '200' : '300'}
                        image={artwork.url}
                        alt={`Artwork ${artwork.id}`}
                        sx={{ objectFit: 'cover' }}
                      />

                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Chip
                            label={artwork.artwork_type}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          {selectedArtwork === artwork.id && (
                            <Chip
                              icon={<CheckIcon />}
                              label="Selected"
                              color="success"
                              variant="filled"
                              size="small"
                            />
                          )}
                        </Box>

                        <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 1 }}>
                          {artwork.width}x{artwork.height}px
                        </Typography>

                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                          <Tooltip title="Download">
                            <IconButton
                              size="small"
                              onClick={() => downloadArtwork(artwork.url, `${artwork.artwork_type}.png`)}
                            >
                              <DownloadIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>

                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              onClick={() => deleteArtwork(artwork.id)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => setGeneratedArtworks([])}
                sx={{ mt: 2 }}
              >
                Generate More
              </Button>
            </Box>
          )}

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Generating AI artwork...</Typography>
                <Typography variant="caption" color="textSecondary">
                  This may take 1-3 minutes
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose}>
            Close
          </Button>
          {generatedArtworks.length === 0 && !loading && (
            <Button
              onClick={generateArtwork}
              variant="contained"
              color="primary"
              disabled={!formData.title || (uploadType === 'music' && !formData.artist)}
            >
              Generate Artwork
            </Button>
          )}
          {selectedArtwork && (
            <Button
              onClick={() => {
                handleClose();
              }}
              variant="contained"
              color="success"
            >
              Use Selected Artwork
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ArtworkGenerator;
