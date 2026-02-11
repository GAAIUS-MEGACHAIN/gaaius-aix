import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Globe, FileText, BarChart3, Copy } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  min-height: 100vh;
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.8rem;
  }
`;

const Button = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
  }
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  color: #333;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin: 15px 0;
`;

const StatBox = styled.div`
  background: ${props => props.color || '#f0f0f0'};
  padding: 15px;
  border-radius: 8px;
  text-align: center;

  & > div:first-child {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 5px;
  }

  & > div:last-child {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
  }
`;

const LanguageGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 15px 0;
`;

const LanguageBadge = styled.div`
  background: #D1FAE5;
  color: #065F46;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: bold;
  text-align: center;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;

  & > button {
    flex: 1;
  }
`;

const SmallButton = styled.button`
  background: #10B981;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: all 0.3s;

  &:hover {
    background: #059669;
    transform: translateY(-1px);
  }
`;

const FormContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 600px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #10B981;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #10B981;
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  min-height: 100px;
  resize: vertical;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #10B981;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #10B981;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #059669;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const SUPPORTED_LANGUAGES = [
  'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
  'Dutch', 'Russian', 'Japanese', 'Chinese (Mandarin)', 'Korean',
  'Arabic', 'Hindi', 'Turkish', 'Polish', 'Swedish', 'Norwegian',
  'Danish', 'Finnish', 'Czech', 'Hungarian', 'Romanian'
];

const TranslationTab = () => {
  const [projects, setProjects] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    title: '',
    sourceLanguage: 'English',
    targetLanguages: [],
    content: ''
  });

  const mockProjects = [
    {
      id: 1,
      title: 'Website Copy Localization',
      sourceLanguage: 'English',
      targetLanguages: ['Spanish', 'French', 'German', 'Japanese'],
      words: 5240,
      completed: 75,
      status: 'In Progress'
    },
    {
      id: 2,
      title: 'Mobile App Strings',
      sourceLanguage: 'English',
      targetLanguages: ['Chinese (Mandarin)', 'Korean', 'Portuguese'],
      words: 2150,
      completed: 100,
      status: 'Complete'
    },
    {
      id: 3,
      title: 'Marketing Campaign',
      sourceLanguage: 'English',
      targetLanguages: ['Spanish', 'French', 'German', 'Italian'],
      words: 3890,
      completed: 45,
      status: 'In Progress'
    },
    {
      id: 4,
      title: 'Technical Documentation',
      sourceLanguage: 'English',
      targetLanguages: ['Russian', 'Japanese', 'German'],
      words: 8500,
      completed: 60,
      status: 'In Progress'
    }
  ];

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/translation/projects`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setProjects(response.data.projects || mockProjects);
    } catch (error) {
      console.error('Error fetching projects:', error);
      setProjects(mockProjects);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLanguageToggle = (language) => {
    setFormData(prev => ({
      ...prev,
      targetLanguages: prev.targetLanguages.includes(language)
        ? prev.targetLanguages.filter(l => l !== language)
        : [...prev.targetLanguages, language]
    }));
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();

    if (!formData.title || formData.targetLanguages.length === 0) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/translation/create`,
        {
          title: formData.title,
          sourceLanguage: formData.sourceLanguage,
          targetLanguages: formData.targetLanguages,
          content: formData.content
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const newProject = {
        id: projects.length + 1,
        title: formData.title,
        sourceLanguage: formData.sourceLanguage,
        targetLanguages: formData.targetLanguages,
        words: formData.content.split(' ').length,
        completed: 0,
        status: 'Pending'
      };

      setProjects(prev => [newProject, ...prev]);
      setFormData({ title: '', sourceLanguage: 'English', targetLanguages: [], content: '' });
      setShowCreateForm(false);
      toast.success('Translation project created!');
      fetchProjects();
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
    }
  };

  if (loading) {
    return <Container><Title><Globe /> Loading projects...</Title></Container>;
  }

  return (
    <Container>
      <Header>
        <Title>
          <Globe /> Translation Management
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> New Project
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create Translation Project</h2>
          <form onSubmit={handleCreateProject}>
            <FormGroup>
              <Label>Project Title *</Label>
              <Input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., Website Localization"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Source Language</Label>
              <Select
                name="sourceLanguage"
                value={formData.sourceLanguage}
                onChange={handleInputChange}
              >
                {SUPPORTED_LANGUAGES.map(lang => (
                  <option key={lang} value={lang}>{lang}</option>
                ))}
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Target Languages * (Select at least one)</Label>
              <LanguageGrid>
                {SUPPORTED_LANGUAGES.filter(l => l !== formData.sourceLanguage).map(lang => (
                  <div key={lang}>
                    <input
                      type="checkbox"
                      id={lang}
                      checked={formData.targetLanguages.includes(lang)}
                      onChange={() => handleLanguageToggle(lang)}
                    />
                    <label htmlFor={lang} style={{ marginLeft: '8px', cursor: 'pointer' }}>
                      {lang}
                    </label>
                  </div>
                ))}
              </LanguageGrid>
            </FormGroup>

            <FormGroup>
              <Label>Content to Translate</Label>
              <Textarea
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                placeholder="Paste the content you want to translate..."
              />
            </FormGroup>

            <SubmitButton type="submit">Create Project</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {projects.map(project => (
          <Card key={project.id}>
            <CardTitle>
              <FileText size={20} /> {project.title}
            </CardTitle>

            <StatsGrid>
              <StatBox color="#D1FAE5">
                <div>Word Count</div>
                <div>{project.words.toLocaleString()}</div>
              </StatBox>
              <StatBox color="#D1FAE5">
                <div>Progress</div>
                <div>{project.completed}%</div>
              </StatBox>
            </StatsGrid>

            <div style={{ marginTop: '15px' }}>
              <strong>Languages:</strong>
              <LanguageGrid>
                {project.targetLanguages.map(lang => (
                  <LanguageBadge key={lang}>{lang}</LanguageBadge>
                ))}
              </LanguageGrid>
            </div>

            <div style={{ marginTop: '15px', padding: '10px', background: '#F0FDF4', borderRadius: '6px', fontSize: '0.9rem', color: '#166534' }}>
              <strong>Status:</strong> {project.status}
            </div>

            <ButtonGroup>
              <SmallButton>
                <FileText size={16} /> Edit
              </SmallButton>
              <SmallButton>
                <BarChart3 size={16} /> Progress
              </SmallButton>
            </ButtonGroup>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default TranslationTab;
