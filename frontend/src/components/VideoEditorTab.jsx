import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Trash2, Download, Play, Star, ThumbsUp, ThumbsDown } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  min-height: 100vh;
`;

const Section = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const Label = styled.label`
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
`;

const Input = styled.input`
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }
`;

const Select = styled.select`
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  background: white;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }
`;

const TextArea = styled.textarea`
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  
  &:focus {
    outline: none;
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const Button = styled.button`
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  
  ${props => props.primary ? `
    background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
    color: white;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
  ` : `
    background: #f3f4f6;
    color: #374151;
    
    &:hover {
      background: #e5e7eb;
    }
  `}
`;

const ProjectGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const ProjectCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
  
  &:hover {
    border-color: #ef4444;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
  }
`;

const ProjectTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
`;

const ProjectMeta = styled.p`
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
`;

const ProjectActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  background: #f3f4f6;
  color: #374151;
  flex: 1;
  justify-content: center;
  
  &:hover {
    background: #e5e7eb;
  }
`;

const RecommendationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const RecommendationCard = styled.div`
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #fecaca;
`;

const RecTitle = styled.h4`
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 600;
  color: #991b1b;
`;

const RecMeta = styled.p`
  margin: 0 0 10px 0;
  font-size: 12px;
  color: #b45454;
`;

const RecReason = styled.p`
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #7f1d1d;
  font-style: italic;
`;

const FeedbackButtons = styled.div`
  display: flex;
  gap: 8px;
`;

const FeedbackBtn = styled.button`
  padding: 6px 8px;
  border: 1px solid #fca5a5;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  
  &:hover {
    background: #fef2f2;
    border-color: #dc2626;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
`;

const VideoEditorTab = () => {
  const [projects, setProjects] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    resolution: '1080p'
  });

  useEffect(() => {
    loadProjects();
    loadRecommendations();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/video/projects');
      setProjects(response.data.projects || []);
    } catch (error) {
      setProjects([
        { id: 1, title: 'Summer Vlog', description: 'Beach trip highlights', resolution: '4K', segments: 12, audioTracks: 2, duration: '15:30' },
        { id: 2, title: 'Tutorial Series', description: 'React advanced patterns', resolution: '1080p', segments: 8, audioTracks: 1, duration: '45:00' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const response = await axios.get('/api/v1/recommendation/videos');
      setRecommendations(response.data.recommendations || []);
    } catch (error) {
      setRecommendations([
        { id: 'v1', title: 'Advanced Color Grading', type: 'tutorial', score: 4.8, reason: 'Based on your editing style' },
        { id: 'v2', title: 'Motion Graphics Essentials', type: 'course', score: 4.6, reason: 'Popular with editors like you' },
        { id: 'v3', title: 'Audio Mixing Pro', type: 'guide', score: 4.7, reason: 'Complements your projects' },
        { id: 'v4', title: 'Premiere Pro Shortcuts', type: 'tips', score: 4.5, reason: 'Trending in community' }
      ]);
    }
  };

  const createProject = () => {
    if (!formData.title.trim()) {
      toast.error('Project title required');
      return;
    }
    
    const newProject = {
      id: Date.now(),
      ...formData,
      segments: 0,
      audioTracks: 1,
      duration: '0:00',
      createdAt: new Date().toISOString()
    };
    
    setProjects([newProject, ...projects]);
    setFormData({ title: '', description: '', resolution: '1080p' });
    toast.success('Project created');
  };

  const deleteProject = (id) => {
    setProjects(projects.filter(p => p.id !== id));
    toast.success('Project deleted');
  };

  const provideFeedback = (id, feedback) => {
    toast.success(`Marked as ${feedback}`);
  };

  return (
    <Container>
      <Section>
        <SectionTitle>
          <Plus size={20} />
          New Project
        </SectionTitle>
        
        <FormGrid>
          <FormGroup>
            <Label>Project Title</Label>
            <Input 
              type="text"
              placeholder="My awesome project"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Resolution</Label>
            <Select 
              value={formData.resolution}
              onChange={(e) => setFormData({...formData, resolution: e.target.value})}
            >
              <option>1080p</option>
              <option>2K</option>
              <option>4K</option>
            </Select>
          </FormGroup>
        </FormGrid>
        
        <FormGroup>
          <Label>Description</Label>
          <TextArea 
            placeholder="What is this project about?"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
        </FormGroup>
        
        <ButtonGroup>
          <Button primary onClick={createProject}>
            <Plus size={16} />
            Create Project
          </Button>
        </ButtonGroup>
      </Section>

      <Section>
        <SectionTitle>
          <Tv size={20} />
          Your Projects
        </SectionTitle>
        
        {projects.length === 0 ? (
          <EmptyState>No projects yet. Create your first video project above!</EmptyState>
        ) : (
          <ProjectGrid>
            {projects.map(project => (
              <ProjectCard key={project.id}>
                <ProjectTitle>{project.title}</ProjectTitle>
                <ProjectMeta>
                  {project.description && <div>{project.description}</div>}
                  <div>Resolution: {project.resolution}</div>
                  <div>Segments: {project.segments} | Audio: {project.audioTracks}</div>
                  <div>Duration: {project.duration}</div>
                </ProjectMeta>
                <ProjectActions>
                  <ActionButton><Play size={14} /> Open</ActionButton>
                  <ActionButton><Download size={14} /> Export</ActionButton>
                  <ActionButton onClick={() => deleteProject(project.id)}><Trash2 size={14} /> Delete</ActionButton>
                </ProjectActions>
              </ProjectCard>
            ))}
          </ProjectGrid>
        )}
      </Section>

      <Section>
        <SectionTitle>
          <Star size={20} />
          Recommended for You
        </SectionTitle>
        
        {recommendations.length === 0 ? (
          <EmptyState>No recommendations available</EmptyState>
        ) : (
          <RecommendationGrid>
            {recommendations.map(rec => (
              <RecommendationCard key={rec.id}>
                <RecTitle>{rec.title}</RecTitle>
                <RecMeta>
                  <span>{rec.type}</span>  <span> {rec.score}</span>
                </RecMeta>
                <RecReason>"{rec.reason}"</RecReason>
                <FeedbackButtons>
                  <FeedbackBtn onClick={() => provideFeedback(rec.id, 'liked')}>
                    <ThumbsUp size={14} /> Like
                  </FeedbackBtn>
                  <FeedbackBtn onClick={() => provideFeedback(rec.id, 'disliked')}>
                    <ThumbsDown size={14} /> Skip
                  </FeedbackBtn>
                </FeedbackButtons>
              </RecommendationCard>
            ))}
          </RecommendationGrid>
        )}
      </Section>
    </Container>
  );
};

export default VideoEditorTab;
