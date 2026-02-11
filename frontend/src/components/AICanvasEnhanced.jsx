import React, { useState, useEffect, useCallback, useRef } from 'react';
import styled from 'styled-components';
import { Wand2, Search, Filter, Download, Share2, Loader, MessageSquare, Lightbulb, Zap } from 'lucide-react';
import axios from 'axios';

const EnhancedCanvasContainer = styled.div`
  display: flex;
  height: 100vh;
  background: #0a0e27;
  color: white;
  font-family: 'Inter', system-ui, sans-serif;
`;

const TemplatesSidebar = styled.div`
  width: 300px;
  background: linear-gradient(180deg, #1a1f3a 0%, #0f1219 100%);
  border-right: 1px solid #2a2f45;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  @media (max-width: 1200px) {
    width: 250px;
  }
`;

const SidebarHeader = styled.div`
  padding: 16px;
  border-bottom: 1px solid #2a2f45;

  h3 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    color: #8b5cf6;
    letter-spacing: 0.5px;
  }
`;

const SearchBox = styled.div`
  position: relative;
  
  input {
    width: 100%;
    padding: 8px 12px 8px 36px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 6px;
    color: white;
    font-size: 13px;
    transition: all 0.2s;

    &::placeholder {
      color: rgba(255, 255, 255, 0.4);
    }

    &:focus {
      outline: none;
      background: rgba(255, 255, 255, 0.08);
      border-color: #8b5cf6;
      box-shadow: 0 0 12px rgba(139, 92, 246, 0.2);
    }
  }

  svg {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 16px;
    color: rgba(139, 92, 246, 0.5);
  }
`;

const CategoryTabs = styled.div`
  display: flex;
  gap: 8px;
  padding: 12px 12px;
  border-bottom: 1px solid #2a2f45;
  overflow-x: auto;

  &::-webkit-scrollbar {
    height: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #8b5cf6;
    border-radius: 2px;
  }
`;

const CategoryTab = styled.button`
  padding: 6px 12px;
  background: ${props => props.active ? '#8b5cf6' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.active ? '#8b5cf6' : 'rgba(139, 92, 246, 0.3)'};
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#8b5cf6' : 'rgba(139, 92, 246, 0.2)'};
  }
`;

const TemplatesList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #8b5cf6;
    border-radius: 3px;

    &:hover {
      background: #a78bfa;
    }
  }
`;

const TemplateCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: #8b5cf6;
    transform: translateX(4px);
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.15);
  }
`;

const TemplatePreview = styled.div`
  width: 100%;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    animation: moveGradient 20s linear infinite;
  }

  @keyframes moveGradient {
    0% { transform: translate(0, 0); }
    100% { transform: translate(20px, 20px); }
  }
`;

const TemplateInfo = styled.div`
  padding: 10px;

  h4 {
    margin: 0 0 4px 0;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  p {
    margin: 0;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.6);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

const ApplyButton = styled.button`
  width: 100%;
  padding: 8px;
  margin-top: 8px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const MainCanvas = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
  border-right: 1px solid #2a2f45;
`;

const CanvasToolbar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid #2a2f45;
  gap: 12px;

  button {
    padding: 8px 16px;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }

    svg {
      width: 16px;
      height: 16px;
    }
  }
`;

const CanvasArea = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: auto;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      linear-gradient(rgba(139, 92, 246, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(139, 92, 246, 0.05) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none;
  }
`;

const CanvasFrame = styled.div`
  width: ${props => props.width || 1280}px;
  height: ${props => props.height || 720}px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(139, 92, 246, 0.2);
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
`;

const AISidebar = styled.div`
  width: 320px;
  background: linear-gradient(180deg, #1a1f3a 0%, #0f1219 100%);
  border-left: 1px solid #2a2f45;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const AIPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #8b5cf6;
    border-radius: 3px;
  }
`;

const AISection = styled.div`
  padding: 16px;
  border-bottom: 1px solid #2a2f45;

  h4 {
    margin: 0 0 12px 0;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    color: #8b5cf6;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
`;

const SuggestionCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: #8b5cf6;
  }

  p {
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    color: rgba(255, 255, 255, 0.8);
  }

  small {
    color: rgba(139, 92, 246, 0.8);
    font-size: 11px;
    margin-top: 6px;
    display: block;
  }
`;

const AIChat = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ChatMessage = styled.div`
  background: ${props => props.bot ? 'rgba(139, 92, 246, 0.15)' : 'rgba(255, 255, 255, 0.05)'};
  border-left: 2px solid ${props => props.bot ? '#8b5cf6' : 'transparent'};
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
  word-wrap: break-word;
`;

const ChatInput = styled.div`
  display: flex;
  gap: 6px;
  padding: 12px;
  border-top: 1px solid #2a2f45;

  input {
    flex: 1;
    padding: 8px 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 4px;
    color: white;
    font-size: 12px;

    &::placeholder {
      color: rgba(255, 255, 255, 0.3);
    }

    &:focus {
      outline: none;
      background: rgba(255, 255, 255, 0.08);
      border-color: #8b5cf6;
    }
  }

  button {
    padding: 6px 12px;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    border: none;
    border-radius: 4px;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 14px;
      height: 14px;
    }

    &:hover {
      opacity: 0.9;
    }
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

export default function AICanvasEnhanced() {
  const [templates, setTemplates] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('social_media');
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [designDimensions, setDesignDimensions] = useState({ width: 1280, height: 720 });

  const categories = [
    'social_media',
    'business',
    'marketing',
    'education',
    'events',
    'print'
  ];

  // Load templates
  useEffect(() => {
    loadTemplates();
  }, [selectedCategory]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/ai-canvas/templates/category/${selectedCategory}`);
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
      // Fallback: show sample templates
      setSampleTemplates();
    } finally {
      setLoading(false);
    }
  };

  const setSampleTemplates = () => {
    setTemplates([
      {
        id: '1',
        name: 'Instagram Post',
        category: 'social_media',
        dimensions: { width: 1080, height: 1080 },
        description: 'Perfect for Instagram feeds'
      },
      {
        id: '2',
        name: 'Business Card',
        category: 'business',
        dimensions: { width: 1050, height: 600 },
        description: 'Professional business card'
      },
      {
        id: '3',
        name: 'Email Header',
        category: 'marketing',
        dimensions: { width: 600, height: 200 },
        description: 'Email marketing header'
      }
    ]);
  };

  const applyTemplate = async (template) => {
    try {
      setDesignDimensions(template.dimensions);
      setChatMessages(prev => [...prev, {
        type: 'bot',
        message: `Applied template: ${template.name}. I've set up the canvas with ${template.dimensions.width}x${template.dimensions.height}px dimensions.`
      }]);
      
      // Generate AI suggestions for this template
      await generateAISuggestions(template);
    } catch (error) {
      console.error('Failed to apply template:', error);
    }
  };

  const generateAISuggestions = async (template) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/ai-canvas/design-ai/suggestions', {
        category: template.category,
        purpose: template.description,
        style: 'modern'
      });

      const suggestions_data = response.data.suggestions || {};
      setSuggestions([
        { type: 'layout', content: suggestions_data.layout || 'Use clean grid layout' },
        { type: 'colors', content: suggestions_data.colors || 'Choose 2-3 complementary colors' },
        { type: 'typography', content: suggestions_data.typography || 'Use sans-serif fonts' }
      ]);
    } catch (error) {
      console.error('Failed to generate suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatMessages(prev => [...prev, { type: 'user', message: userMessage }]);
    setChatInput('');
    setLoading(true);

    try {
      // Simulate AI response
      const response = await axios.post('/api/ai-canvas/design-ai/brainstorm', {
        topic: userMessage,
        count: 3
      });

      const botMessage = `Here are some design ideas for "${userMessage}":
${response.data.ideas?.brainstorm ? response.data.ideas.brainstorm.substring(0, 200) + '...' : 'I can help you brainstorm design ideas.'}`;

      setChatMessages(prev => [...prev, { type: 'bot', message: botMessage }]);
    } catch (error) {
      setChatMessages(prev => [...prev, {
        type: 'bot',
        message: 'I can help you brainstorm design ideas, generate content, and optimize layouts. What would you like to create?'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <EnhancedCanvasContainer>
      {/* Templates Sidebar */}
      <TemplatesSidebar>
        <SidebarHeader>
          <h3>📋 Templates</h3>
          <SearchBox>
            <Search size={16} />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchBox>
        </SidebarHeader>

        <CategoryTabs>
          {categories.map(cat => (
            <CategoryTab
              key={cat}
              active={selectedCategory === cat}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat.replace('_', ' ').charAt(0).toUpperCase() + cat.replace('_', ' ').slice(1)}
            </CategoryTab>
          ))}
        </CategoryTabs>

        <TemplatesList>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
              <LoadingSpinner />
            </div>
          ) : filteredTemplates.length > 0 ? (
            filteredTemplates.map(template => (
              <TemplateCard key={template.id}>
                <TemplatePreview>
                  {template.name}
                </TemplatePreview>
                <TemplateInfo>
                  <h4>{template.name}</h4>
                  <p>{template.description}</p>
                </TemplateInfo>
                <ApplyButton onClick={() => applyTemplate(template)}>
                  Apply Template
                </ApplyButton>
              </TemplateCard>
            ))
          ) : (
            <div style={{ padding: '12px', fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
              No templates found
            </div>
          )}
        </TemplatesList>
      </TemplatesSidebar>

      {/* Main Canvas */}
      <MainCanvas>
        <CanvasToolbar>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button title="Export Design">
              <Download size={16} /> Export
            </button>
            <button title="Share Design">
              <Share2 size={16} /> Share
            </button>
          </div>
          <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
            {designDimensions.width} × {designDimensions.height}px
          </div>
        </CanvasToolbar>

        <CanvasArea>
          <CanvasFrame width={designDimensions.width} height={designDimensions.height}>
            <div style={{ color: '#ccc', textAlign: 'center' }}>
              <Wand2 size={48} style={{ marginBottom: '12px', opacity: 0.5 }} />
              <p>Canvas ready for design</p>
              <small style={{ opacity: 0.6 }}>Select a template to get started</small>
            </div>
          </CanvasFrame>
        </CanvasArea>
      </MainCanvas>

      {/* AI Assistant Sidebar */}
      <AISidebar>
        <AISection>
          <h4>
            <Lightbulb size={14} /> AI Suggestions
          </h4>
          {suggestions.length > 0 ? (
            suggestions.map((sugg, idx) => (
              <SuggestionCard key={idx}>
                <p>{sugg.content}</p>
                <small>{sugg.type}</small>
              </SuggestionCard>
            ))
          ) : (
            <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
              Apply a template to see AI suggestions
            </p>
          )}
        </AISection>

        <AISection>
          <h4>
            <MessageSquare size={14} /> Design Assistant
          </h4>
          <AIChat>
            {chatMessages.map((msg, idx) => (
              <ChatMessage key={idx} bot={msg.type === 'bot'}>
                <strong>{msg.type === 'bot' ? '🤖 AI:' : 'You:'}</strong> {msg.message}
              </ChatMessage>
            ))}
          </AIChat>

          <ChatInput>
            <input
              type="text"
              placeholder="Ask me anything..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
            />
            <button onClick={handleChatSubmit} disabled={loading}>
              {loading ? <LoadingSpinner /> : <Zap size={14} />}
            </button>
          </ChatInput>
        </AISection>
      </AISidebar>
    </EnhancedCanvasContainer>
  );
}
