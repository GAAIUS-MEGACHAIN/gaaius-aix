import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { AlertCircle, Send, Plus, Play, Download, Share2, Loader, CheckCircle, XCircle, Clock, Eye } from 'lucide-react';

const Container = styled.div`
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #e0e0e0;
  padding: 30px;
  border-radius: 12px;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
  
  h1 {
    font-size: 2.5em;
    background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }
  
  p {
    font-size: 1.1em;
    color: #a0a0a0;
  }
`;

const TabContainer = styled.div`
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  border-bottom: 2px solid #2a2a3e;
  padding-bottom: 0;
  overflow-x: auto;
`;

const Tab = styled.button`
  padding: 15px 25px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: ${props => props.active ? '#00d4ff' : '#a0a0a0'};
  cursor: pointer;
  font-size: 1em;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    color: #00d4ff;
  }
  
  ${props => props.active && `
    border-bottom-color: #00d4ff;
  `}
`;

const Content = styled.div`
  animation: fadeIn 0.3s ease;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const FormSection = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
  
  label {
    display: block;
    margin-bottom: 10px;
    color: #00d4ff;
    font-weight: 600;
    font-size: 0.95em;
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 0.95em;
  
  &:focus {
    outline: none;
    border-color: #00d4ff;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  }
  
  &::placeholder {
    color: #606060;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 0.95em;
  min-height: 120px;
  font-family: 'Inter', sans-serif;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #00d4ff;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  }
  
  &::placeholder {
    color: #606060;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 0.95em;
  
  &:focus {
    outline: none;
    border-color: #00d4ff;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  }
  
  option {
    background: #1a1a2e;
    color: #e0e0e0;
  }
`;

const GridRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #e0e0e0;
  
  input {
    cursor: pointer;
    accent-color: #00d4ff;
  }
`;

const Button = styled.button`
  padding: 12px 30px;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const SecondaryButton = styled(Button)`
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
  
  &:hover {
    background: rgba(0, 212, 255, 0.2);
  }
`;

const JobCard = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 15px;
`;

const JobHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  
  h3 {
    margin: 0;
    color: #00d4ff;
  }
`;

const StatusBadge = styled.span`
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
  
  ${props => {
    const statusMap = {
      'pending': 'background: rgba(255, 193, 7, 0.2); color: #ffc107;',
      'processing': 'background: rgba(0, 150, 255, 0.2); color: #00d4ff;',
      'completed': 'background: rgba(76, 175, 80, 0.2); color: #4caf50;',
      'failed': 'background: rgba(244, 67, 54, 0.2); color: #f44336;',
    };
    return statusMap[props.status] || statusMap['pending'];
  }}
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
  
  div {
    height: 100%;
    background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%);
    width: ${props => props.progress}%;
    transition: width 0.3s ease;
  }
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 30px;
`;

const ContentCard = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #00d4ff;
    box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2);
  }
`;

const ContentImage = styled.div`
  width: 100%;
  height: 150px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3em;
`;

const ContentInfo = styled.div`
  padding: 15px;
  
  h4 {
    margin: 0 0 8px 0;
    color: #00d4ff;
    font-size: 0.95em;
  }
  
  p {
    margin: 0 0 10px 0;
    color: #a0a0a0;
    font-size: 0.85em;
  }
`;

const ContentStats = styled.div`
  display: flex;
  gap: 10px;
  font-size: 0.8em;
  color: #808080;
  margin-bottom: 10px;
`;

const ContentActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 10px;
  
  button {
    flex: 1;
    padding: 8px;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    color: #00d4ff;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8em;
    transition: all 0.3s ease;
    
    &:hover {
      background: rgba(0, 212, 255, 0.2);
    }
  }
`;

const Alert = styled.div`
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.3);
  color: #f44336;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
`;

const TemplateGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
`;

const TemplateCard = styled.div`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #00d4ff;
    background: rgba(0, 212, 255, 0.1);
  }
  
  h4 {
    margin: 0 0 8px 0;
    color: #00d4ff;
    font-size: 0.95em;
  }
  
  p {
    margin: 0;
    color: #a0a0a0;
    font-size: 0.85em;
  }
`;

const PrioritySelector = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const PriorityButton = styled.button`
  flex: 1;
  padding: 10px;
  background: ${props => props.selected ? 'rgba(0, 212, 255, 0.3)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.selected ? '#00d4ff' : 'rgba(0, 212, 255, 0.2)'};
  color: ${props => props.selected ? '#00d4ff' : '#a0a0a0'};
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #00d4ff;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #606060;
  
  p {
    font-size: 1.1em;
    margin-bottom: 20px;
  }
`;

const ContentGenerationPipeline = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [formData, setFormData] = useState({
    contentType: 'VIDEO',
    title: '',
    prompt: '',
    description: '',
    aiProvider: 'groq',
    style: '',
    duration: '',
    withSubtitles: false,
    withTranscript: false,
    autoPublish: false,
    tags: '',
    priority: 5,
  });
  
  const [jobs, setJobs] = useState([]);
  const [content, setContent] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const API_BASE = 'http://localhost:8000/api';
  const userId = localStorage.getItem('userId') || 'default-user';

  useEffect(() => {
    loadJobs();
    loadContent();
    loadTemplates();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/content-generation/jobs?user_id=${userId}`);
      setJobs(response.data.jobs || []);
    } catch (err) {
      console.error('Error loading jobs:', err);
    }
  };

  const loadContent = async () => {
    try {
      const response = await axios.get(`${API_BASE}/content-generation/library?user_id=${userId}`);
      setContent(response.data.library || []);
    } catch (err) {
      console.error('Error loading content:', err);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/content-generation/templates`);
      setTemplates(response.data.templates || []);
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `${API_BASE}/content-generation/request/create`,
        {
          user_id: userId,
          content_type: formData.contentType,
          title: formData.title,
          prompt: formData.prompt,
          description: formData.description,
          ai_provider: formData.aiProvider,
          style: formData.style,
          duration: formData.duration ? parseInt(formData.duration) : null,
          with_subtitles: formData.withSubtitles,
          with_transcript: formData.withTranscript,
          auto_publish: formData.autoPublish,
          tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
          priority: formData.priority,
        }
      );

      const requestId = response.data.request.id;

      // Start generation job
      const jobResponse = await axios.post(
        `${API_BASE}/content-generation/job/start`,
        { request_id: requestId }
      );

      setFormData({
        contentType: 'VIDEO',
        title: '',
        prompt: '',
        description: '',
        aiProvider: 'groq',
        style: '',
        duration: '',
        withSubtitles: false,
        withTranscript: false,
        autoPublish: false,
        tags: '',
        priority: 5,
      });

      await loadJobs();
      setActiveTab('jobs');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create request');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyTemplate = (template) => {
    setFormData(prev => ({
      ...prev,
      contentType: template.content_type,
      aiProvider: template.ai_provider,
      prompt: template.prompt_template,
      title: `${template.name} - New`,
    }));
    setSelectedTemplate(template.id);
    setActiveTab('create');
  };

  const getContentIcon = (type) => {
    const icons = {
      'VIDEO': '🎬',
      'MUSIC': '🎵',
      'IMAGE': '🖼️',
      'AUDIO': '🔊',
      'DOCUMENT': '📄',
      'COURSE_LESSON': '📚',
      'MOVIE': '🎥',
      'PODCAST': '🎙️',
      'ANIMATION': '✨',
      'INTERACTIVE': '🎮',
      'CANVAS': '🎨',
      'SOCIAL_POST': '📱',
    };
    return icons[type] || '📦';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'pending': <Clock size={16} />,
      'processing': <Loader size={16} className="spin" />,
      'completed': <CheckCircle size={16} />,
      'failed': <XCircle size={16} />,
    };
    return icons[status] || null;
  };

  return (
    <Container>
      <Header>
        <h1>🎬 Content Generation Studio</h1>
        <p>Create unlimited videos, music, images, and more with AI</p>
      </Header>

      <TabContainer>
        <Tab active={activeTab === 'create'} onClick={() => setActiveTab('create')}>
          Create Content
        </Tab>
        <Tab active={activeTab === 'jobs'} onClick={() => setActiveTab('jobs')}>
          Active Jobs ({jobs.length})
        </Tab>
        <Tab active={activeTab === 'library'} onClick={() => setActiveTab('library')}>
          Content Library ({content.length})
        </Tab>
        <Tab active={activeTab === 'templates'} onClick={() => setActiveTab('templates')}>
          Templates ({templates.length})
        </Tab>
      </TabContainer>

      <Content>
        {error && (
          <Alert>
            <AlertCircle size={20} />
            <span>{error}</span>
          </Alert>
        )}

        {activeTab === 'create' && (
          <FormSection>
            <h2>Create New Content</h2>
            <form onSubmit={handleCreateRequest}>
              <FormGroup>
                <label>Content Type</label>
                <Select
                  value={formData.contentType}
                  onChange={(e) => setFormData(prev => ({ ...prev, contentType: e.target.value }))}
                >
                  <option value="VIDEO">📹 Video</option>
                  <option value="MUSIC">🎵 Music</option>
                  <option value="IMAGE">🖼️ Image</option>
                  <option value="AUDIO">🔊 Audio</option>
                  <option value="DOCUMENT">📄 Document</option>
                  <option value="COURSE_LESSON">📚 Course Lesson</option>
                  <option value="MOVIE">🎬 Movie</option>
                  <option value="PODCAST">🎙️ Podcast</option>
                  <option value="ANIMATION">✨ Animation</option>
                  <option value="INTERACTIVE">🎮 Interactive</option>
                  <option value="CANVAS">🎨 Canvas</option>
                  <option value="SOCIAL_POST">📱 Social Post</option>
                </Select>
              </FormGroup>

              <GridRow>
                <FormGroup>
                  <label>Title</label>
                  <Input
                    type="text"
                    placeholder="Content title..."
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    required
                  />
                </FormGroup>

                <FormGroup>
                  <label>AI Provider</label>
                  <Select
                    value={formData.aiProvider}
                    onChange={(e) => setFormData(prev => ({ ...prev, aiProvider: e.target.value }))}
                  >
                    <option value="groq">🚀 Groq</option>
                    <option value="openai">🤖 OpenAI</option>
                    <option value="cohere">🧠 Cohere</option>
                    <option value="ollama">🦙 Ollama</option>
                    <option value="huggingface">🤗 HuggingFace</option>
                  </Select>
                </FormGroup>
              </GridRow>

              <FormGroup>
                <label>Prompt / Description</label>
                <TextArea
                  placeholder="Describe what you want to create..."
                  value={formData.prompt}
                  onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
                  required
                />
              </FormGroup>

              <GridRow>
                <FormGroup>
                  <label>Style / Tone</label>
                  <Input
                    type="text"
                    placeholder="e.g., cinematic, educational, casual..."
                    value={formData.style}
                    onChange={(e) => setFormData(prev => ({ ...prev, style: e.target.value }))}
                  />
                </FormGroup>

                <FormGroup>
                  <label>Duration (seconds)</label>
                  <Input
                    type="number"
                    placeholder="300"
                    value={formData.duration}
                    onChange={(e) => setFormData(prev => ({ ...prev, duration: e.target.value }))}
                  />
                </FormGroup>
              </GridRow>

              <FormGroup>
                <label>Priority</label>
                <PrioritySelector>
                  {[1, 3, 5, 8, 10].map(p => (
                    <PriorityButton
                      key={p}
                      selected={formData.priority === p}
                      onClick={() => setFormData(prev => ({ ...prev, priority: p }))}
                    >
                      {p === 1 ? '🟢 Low' : p === 3 ? '🟡 Medium' : p === 5 ? '🔵 Normal' : p === 8 ? '🟠 High' : '🔴 Urgent'}
                    </PriorityButton>
                  ))}
                </PrioritySelector>
              </FormGroup>

              <FormGroup>
                <label>Tags</label>
                <Input
                  type="text"
                  placeholder="tag1, tag2, tag3..."
                  value={formData.tags}
                  onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                />
              </FormGroup>

              <FormGroup>
                <CheckboxLabel>
                  <input
                    type="checkbox"
                    checked={formData.withSubtitles}
                    onChange={(e) => setFormData(prev => ({ ...prev, withSubtitles: e.target.checked }))}
                  />
                  Include Subtitles
                </CheckboxLabel>
                <CheckboxLabel>
                  <input
                    type="checkbox"
                    checked={formData.withTranscript}
                    onChange={(e) => setFormData(prev => ({ ...prev, withTranscript: e.target.checked }))}
                  />
                  Generate Transcript
                </CheckboxLabel>
                <CheckboxLabel>
                  <input
                    type="checkbox"
                    checked={formData.autoPublish}
                    onChange={(e) => setFormData(prev => ({ ...prev, autoPublish: e.target.checked }))}
                  />
                  Auto Publish When Ready
                </CheckboxLabel>
              </FormGroup>

              <Button type="submit" disabled={loading}>
                {loading ? <Loader size={20} /> : <Send size={20} />}
                {loading ? 'Creating...' : 'Create Content'}
              </Button>
            </form>
          </FormSection>
        )}

        {activeTab === 'jobs' && (
          <div>
            {jobs.length === 0 ? (
              <EmptyState>
                <p>No active jobs yet. Create your first content to get started!</p>
              </EmptyState>
            ) : (
              jobs.map(job => (
                <JobCard key={job.id}>
                  <JobHeader>
                    <h3>{job.request?.title || 'Untitled'}</h3>
                    <StatusBadge status={job.status}>
                      {getStatusIcon(job.status)} {job.status}
                    </StatusBadge>
                  </JobHeader>
                  
                  <ProgressBar progress={job.progress}>
                    <div />
                  </ProgressBar>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em', color: '#a0a0a0' }}>
                    <span>Progress: {job.progress}%</span>
                    <span>Current Stage: {job.current_stage}</span>
                  </div>
                </JobCard>
              ))
            )}
          </div>
        )}

        {activeTab === 'library' && (
          <div>
            {content.length === 0 ? (
              <EmptyState>
                <p>Your content library is empty. Create some content to see it here!</p>
              </EmptyState>
            ) : (
              <ContentGrid>
                {content.map(item => (
                  <ContentCard key={item.id}>
                    <ContentImage>{getContentIcon(item.content_type)}</ContentImage>
                    <ContentInfo>
                      <h4>{item.title}</h4>
                      <p>{item.content_type}</p>
                      <ContentStats>
                        <span>📊 {item.views || 0} views</span>
                        <span>❤️ {item.likes || 0} likes</span>
                      </ContentStats>
                      <ContentActions>
                        <button><Eye size={14} /> View</button>
                        <button><Download size={14} /> Download</button>
                        <button><Share2 size={14} /> Share</button>
                      </ContentActions>
                    </ContentInfo>
                  </ContentCard>
                ))}
              </ContentGrid>
            )}
          </div>
        )}

        {activeTab === 'templates' && (
          <div>
            {templates.length === 0 ? (
              <EmptyState>
                <p>No templates available yet.</p>
              </EmptyState>
            ) : (
              <TemplateGrid>
                {templates.map(template => (
                  <TemplateCard
                    key={template.id}
                    onClick={() => handleApplyTemplate(template)}
                  >
                    <h4>{template.name}</h4>
                    <p>{template.description}</p>
                    <p style={{ marginTop: '10px', color: '#00d4ff' }}>
                      {template.content_type} • {template.ai_provider}
                    </p>
                  </TemplateCard>
                ))}
              </TemplateGrid>
            )}
          </div>
        )}
      </Content>

      <style>{`
        .spin {
          animation: spin 2s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Container>
  );
};

export default ContentGenerationPipeline;
