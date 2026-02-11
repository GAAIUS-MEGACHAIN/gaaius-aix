import React, { useState, useRef, useEffect, useCallback, useReducer } from 'react';
import styled from 'styled-components';
import { debounce } from 'lodash';
import axios from 'axios';

const CANVAS_API = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8000';

const canvasReducer = (state, action) => {
  switch (action.type) {
    case 'SET_DESIGN':
      return { ...state, currentDesign: action.payload, selectedElement: null };
    case 'SET_PAGE':
      return { ...state, currentPageId: action.payload, selectedElement: null };
    case 'ADD_ELEMENT':
      return { ...state, elements: [...state.elements, action.payload] };
    case 'UPDATE_ELEMENT':
      return {
        ...state,
        elements: state.elements.map(el =>
          el.id === action.payload.id ? { ...el, ...action.payload.updates } : el
        )
      };
    case 'DELETE_ELEMENT':
      return {
        ...state,
        elements: state.elements.filter(el => el.id !== action.payload),
        selectedElement: state.selectedElement === action.payload ? null : state.selectedElement
      };
    case 'SELECT_ELEMENT':
      return { ...state, selectedElement: action.payload };
    case 'SET_TOOL':
      return { ...state, activeTool: action.payload };
    case 'SET_ZOOM':
      return { ...state, zoom: action.payload };
    default:
      return state;
  }
};

const CanvasContainer = styled.div`
  display: flex;
  height: 100vh;
  background: #1a1a1a;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
`;

const Sidebar = styled.div`
  width: 280px;
  background: #0d0d0d;
  border-right: 1px solid #333;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const TopBar = styled.div`
  height: 60px;
  background: #1a1a1a;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  flex: 1;
`;

const TopBarButton = styled.button`
  background: transparent;
  border: 1px solid #444;
  color: #fff;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    background: #333;
    border-color: #666;
  }

  &:active {
    transform: scale(0.98);
  }
`;

const EditorArea = styled.div`
  flex: 1;
  display: flex;
  overflow: hidden;
`;

const Canvas = styled.div`
  flex: 1;
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  overflow: auto;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CanvasWorkspace = styled.div`
  position: relative;
  background: #fff;
  transform: scale(${props => props.zoom}%);
  transform-origin: top left;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const ElementContainer = styled.div`
  position: absolute;
  left: ${props => props.x}px;
  top: ${props => props.y}px;
  width: ${props => props.width}px;
  height: ${props => props.height}px;
  border: ${props => props.selected ? '2px solid #2563eb' : '1px solid #ddd'};
  background: ${props => props.background || 'transparent'};
  transform: ${props => `scale(${props.scaleX}, ${props.scaleY}) rotate(${props.rotation}deg)`};
  cursor: ${props => props.selected ? 'move' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: ${props => props.selected ? '0 0 0 6px rgba(37, 99, 235, 0.1)' : 'none'};
  border-radius: ${props => props.radius || 0}px;

  &:hover {
    border-color: #2563eb;
  }
`;

const TextElement = styled.div`
  font-size: ${props => props.fontSize}px;
  font-family: ${props => props.fontFamily};
  font-weight: ${props => props.fontWeight};
  color: ${props => props.color};
  text-align: ${props => props.textAlign};
  width: 100%;
  height: 100%;
  word-wrap: break-word;
  padding: 8px;
  box-sizing: border-box;
`;

const RightPanel = styled.div`
  width: 320px;
  background: #0d0d0d;
  border-left: 1px solid #333;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
`;

const PanelSection = styled.div`
  padding: 16px;
  border-bottom: 1px solid #333;
`;

const SectionTitle = styled.h3`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #888;
`;

const ToolButton = styled.button`
  width: 100%;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: ${props => props.active ? '#2563eb' : '#222'};
  border: 1px solid ${props => props.active ? '#2563eb' : '#333'};
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  text-align: left;

  &:hover {
    background: ${props => props.active ? '#1d4ed8' : '#333'};
    border-color: #555;
  }
`;

const ColorInput = styled.input`
  width: 100%;
  height: 40px;
  border: 1px solid #333;
  border-radius: 4px;
  cursor: pointer;
  background: ${props => props.value};
  margin-bottom: 8px;
`;

const RangeInput = styled.input`
  width: 100%;
  margin-bottom: 8px;
  cursor: pointer;
`;

const Label = styled.label`
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const PropertyInput = styled.input`
  width: 100%;
  padding: 8px;
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  border-radius: 4px;
  font-size: 13px;
  margin-bottom: 8px;

  &:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
`;

const SelectInput = styled.select`
  width: 100%;
  padding: 8px;
  background: #1a1a1a;
  border: 1px solid #333;
  color: #fff;
  border-radius: 4px;
  font-size: 13px;
  margin-bottom: 8px;

  option {
    background: #1a1a1a;
    color: #fff;
  }

  &:focus {
    outline: none;
    border-color: #2563eb;
  }
`;

const LayerItem = styled.div`
  padding: 10px 12px;
  background: ${props => props.selected ? '#2563eb' : '#1a1a1a'};
  border: 1px solid ${props => props.selected ? '#2563eb' : '#333'};
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 6px;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.selected ? '#1d4ed8' : '#222'};
    border-color: #555;
  }
`;

const ResizeHandle = styled.div`
  position: absolute;
  width: 8px;
  height: 8px;
  background: #2563eb;
  border: 1px solid #fff;
  border-radius: 1px;
  cursor: ${props => props.type};
  
  &.nw { top: -4px; left: -4px; }
  &.ne { top: -4px; right: -4px; }
  &.sw { bottom: -4px; left: -4px; }
  &.se { bottom: -4px; right: -4px; }
`;

const AICanvas = ({ userId, onDesignChange }) => {
  const [state, dispatch] = useReducer(canvasReducer, {
    currentDesign: null,
    currentPageId: null,
    elements: [],
    selectedElement: null,
    activeTool: 'select',
    zoom: 100
  });

  const [designs, setDesigns] = useState([]);
  const [showNewDesignModal, setShowNewDesignModal] = useState(false);
  const [designTitle, setDesignTitle] = useState('');
  const canvasRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    loadDesigns();
  }, []);

  const loadDesigns = async () => {
    try {
      const response = await axios.get(`${CANVAS_API}/api/ai-canvas/designs`);
      setDesigns(response.data || []);
    } catch (error) {
      console.error('Failed to load designs:', error);
    }
  };

  const createNewDesign = async () => {
    if (!designTitle.trim()) return;

    try {
      const response = await axios.post(`${CANVAS_API}/api/ai-canvas/designs`, {
        title: designTitle,
        description: ''
      });
      
      setDesigns([...designs, response.data]);
      dispatch({ type: 'SET_DESIGN', payload: response.data });
      dispatch({ type: 'SET_PAGE', payload: response.data.pages[0]?.id });
      setShowNewDesignModal(false);
      setDesignTitle('');
    } catch (error) {
      console.error('Failed to create design:', error);
    }
  };

  const addElement = useCallback((type) => {
    const newElement = {
      id: Math.random().toString(36),
      type,
      x: 100,
      y: 100,
      width: 200,
      height: 100,
      rotation: 0,
      scaleX: 1,
      scaleY: 1,
      zIndex: state.elements.length,
      background: type === 'shape' ? '#2563eb' : 'transparent',
      content: type === 'text' ? 'Double click to edit' : '',
      fontSize: 16,
      fontFamily: 'Arial',
      fontWeight: 400,
      color: '#000000',
      textAlign: 'left',
      radius: 0
    };

    dispatch({ type: 'ADD_ELEMENT', payload: newElement });
  }, [state.elements.length]);

  const handleElementMouseDown = useCallback((e, elementId) => {
    e.preventDefault();
    dispatch({ type: 'SELECT_ELEMENT', payload: elementId });
    setIsDragging(true);
    setDragOffset({
      x: e.clientX,
      y: e.clientY
    });
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !state.selectedElement) return;

    const deltaX = e.clientX - dragOffset.x;
    const deltaY = e.clientY - dragOffset.y;

    dispatch({
      type: 'UPDATE_ELEMENT',
      payload: {
        id: state.selectedElement,
        updates: {
          x: state.elements.find(el => el.id === state.selectedElement)?.x + deltaX,
          y: state.elements.find(el => el.id === state.selectedElement)?.y + deltaY
        }
      }
    });

    setDragOffset({ x: e.clientX, y: e.clientY });
  }, [isDragging, state.selectedElement, dragOffset, state.elements]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const selectedElementData = state.elements.find(el => el.id === state.selectedElement);

  const handleExport = async () => {
    if (!state.currentDesign) return;

    try {
      const response = await axios.post(
        `${CANVAS_API}/api/ai-canvas/designs/${state.currentDesign.id}/export`,
        {
          format: 'png',
          pageId: state.currentPageId,
          width: 1920,
          height: 1080,
          background: '#ffffff'
        },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `design-${Date.now()}.png`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Failed to export design:', error);
    }
  };

  return (
    <CanvasContainer>
      {/* Left Sidebar - Tools */}
      <Sidebar>
        <PanelSection>
          <SectionTitle>Tools</SectionTitle>
          <ToolButton
            active={state.activeTool === 'select'}
            onClick={() => dispatch({ type: 'SET_TOOL', payload: 'select' })}
          >
            ↖️ Select
          </ToolButton>
          <ToolButton
            active={state.activeTool === 'text'}
            onClick={() => {
              dispatch({ type: 'SET_TOOL', payload: 'text' });
              addElement('text');
            }}
          >
            T Text
          </ToolButton>
          <ToolButton
            active={state.activeTool === 'shape'}
            onClick={() => {
              dispatch({ type: 'SET_TOOL', payload: 'shape' });
              addElement('shape');
            }}
          >
            ⬜ Shape
          </ToolButton>
          <ToolButton
            active={state.activeTool === 'image'}
            onClick={() => {
              dispatch({ type: 'SET_TOOL', payload: 'image' });
              addElement('image');
            }}
          >
            🖼️ Image
          </ToolButton>
        </PanelSection>

        <PanelSection>
          <SectionTitle>Designs</SectionTitle>
          <ToolButton onClick={() => setShowNewDesignModal(true)}>+ New Design</ToolButton>
          <div style={{ marginTop: '12px' }}>
            {designs.slice(0, 5).map(design => (
              <LayerItem
                key={design.id}
                selected={state.currentDesign?.id === design.id}
                onClick={() => dispatch({ type: 'SET_DESIGN', payload: design })}
              >
                {design.title}
              </LayerItem>
            ))}
          </div>
        </PanelSection>
      </Sidebar>

      {/* Main Content */}
      <MainContent>
        {/* Top Bar */}
        <TopBar>
          <Title>
            {state.currentDesign?.title || 'AI Canvas'}
          </Title>
          <TopBarButton onClick={() => dispatch({ type: 'SET_ZOOM', payload: Math.max(50, state.zoom - 10) })}>
            - Zoom Out
          </TopBarButton>
          <div style={{ minWidth: '60px', textAlign: 'center' }}>{state.zoom}%</div>
          <TopBarButton onClick={() => dispatch({ type: 'SET_ZOOM', payload: Math.min(200, state.zoom + 10) })}>
            Zoom In +
          </TopBarButton>
          <TopBarButton onClick={handleExport}>Export</TopBarButton>
        </TopBar>

        {/* Editor Area */}
        <EditorArea>
          {/* Canvas */}
          <Canvas ref={canvasRef}>
            <CanvasWorkspace zoom={state.zoom}>
              {state.elements.map(element => (
                <ElementContainer
                  key={element.id}
                  x={element.x}
                  y={element.y}
                  width={element.width}
                  height={element.height}
                  scaleX={element.scaleX}
                  scaleY={element.scaleY}
                  rotation={element.rotation}
                  radius={element.radius}
                  background={element.background}
                  selected={state.selectedElement === element.id}
                  onMouseDown={(e) => handleElementMouseDown(e, element.id)}
                >
                  {element.type === 'text' && (
                    <TextElement
                      fontSize={element.fontSize}
                      fontFamily={element.fontFamily}
                      fontWeight={element.fontWeight}
                      color={element.color}
                      textAlign={element.textAlign}
                    >
                      {element.content}
                    </TextElement>
                  )}
                  {state.selectedElement === element.id && (
                    <>
                      <ResizeHandle className="nw" />
                      <ResizeHandle className="ne" />
                      <ResizeHandle className="sw" />
                      <ResizeHandle className="se" />
                    </>
                  )}
                </ElementContainer>
              ))}
            </CanvasWorkspace>
          </Canvas>

          {/* Right Panel - Properties */}
          <RightPanel>
            {selectedElementData ? (
              <>
                <PanelSection>
                  <SectionTitle>Element Properties</SectionTitle>
                  
                  <Label>Name</Label>
                  <PropertyInput
                    type="text"
                    value={selectedElementData.name || selectedElementData.type}
                    onChange={(e) =>
                      dispatch({
                        type: 'UPDATE_ELEMENT',
                        payload: { id: state.selectedElement, updates: { name: e.target.value } }
                      })
                    }
                  />

                  <Label>Position X</Label>
                  <PropertyInput
                    type="number"
                    value={Math.round(selectedElementData.x)}
                    onChange={(e) =>
                      dispatch({
                        type: 'UPDATE_ELEMENT',
                        payload: { id: state.selectedElement, updates: { x: parseFloat(e.target.value) } }
                      })
                    }
                  />

                  <Label>Position Y</Label>
                  <PropertyInput
                    type="number"
                    value={Math.round(selectedElementData.y)}
                    onChange={(e) =>
                      dispatch({
                        type: 'UPDATE_ELEMENT',
                        payload: { id: state.selectedElement, updates: { y: parseFloat(e.target.value) } }
                      })
                    }
                  />

                  <Label>Width</Label>
                  <PropertyInput
                    type="number"
                    value={Math.round(selectedElementData.width)}
                    onChange={(e) =>
                      dispatch({
                        type: 'UPDATE_ELEMENT',
                        payload: { id: state.selectedElement, updates: { width: parseFloat(e.target.value) } }
                      })
                    }
                  />

                  <Label>Height</Label>
                  <PropertyInput
                    type="number"
                    value={Math.round(selectedElementData.height)}
                    onChange={(e) =>
                      dispatch({
                        type: 'UPDATE_ELEMENT',
                        payload: { id: state.selectedElement, updates: { height: parseFloat(e.target.value) } }
                      })
                    }
                  />

                  <Label>Rotation</Label>
                  <RangeInput
                    type="range"
                    min="0"
                    max="360"
                    value={selectedElementData.rotation}
                    onChange={(e) =>
                      dispatch({
                        type: 'UPDATE_ELEMENT',
                        payload: { id: state.selectedElement, updates: { rotation: parseFloat(e.target.value) } }
                      })
                    }
                  />
                </PanelSection>

                {selectedElementData.type === 'text' && (
                  <PanelSection>
                    <SectionTitle>Text Options</SectionTitle>
                    
                    <Label>Content</Label>
                    <PropertyInput
                      type="text"
                      value={selectedElementData.content}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { content: e.target.value } }
                        })
                      }
                    />

                    <Label>Font Family</Label>
                    <SelectInput
                      value={selectedElementData.fontFamily}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { fontFamily: e.target.value } }
                        })
                      }
                    >
                      <option>Arial</option>
                      <option>Helvetica</option>
                      <option>Times New Roman</option>
                      <option>Courier New</option>
                      <option>Georgia</option>
                      <option>Verdana</option>
                    </SelectInput>

                    <Label>Font Size</Label>
                    <PropertyInput
                      type="number"
                      value={selectedElementData.fontSize}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { fontSize: parseFloat(e.target.value) } }
                        })
                      }
                    />

                    <Label>Font Weight</Label>
                    <SelectInput
                      value={selectedElementData.fontWeight}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { fontWeight: parseInt(e.target.value) } }
                        })
                      }
                    >
                      <option value={400}>Normal</option>
                      <option value={600}>Bold</option>
                      <option value={700}>Extra Bold</option>
                      <option value={300}>Light</option>
                    </SelectInput>

                    <Label>Color</Label>
                    <ColorInput
                      type="color"
                      value={selectedElementData.color}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { color: e.target.value } }
                        })
                      }
                    />

                    <Label>Text Align</Label>
                    <SelectInput
                      value={selectedElementData.textAlign}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { textAlign: e.target.value } }
                        })
                      }
                    >
                      <option value="left">Left</option>
                      <option value="center">Center</option>
                      <option value="right">Right</option>
                      <option value="justify">Justify</option>
                    </SelectInput>
                  </PanelSection>
                )}

                {selectedElementData.type === 'shape' && (
                  <PanelSection>
                    <SectionTitle>Shape Options</SectionTitle>
                    
                    <Label>Fill Color</Label>
                    <ColorInput
                      type="color"
                      value={selectedElementData.background}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { background: e.target.value } }
                        })
                      }
                    />

                    <Label>Border Radius</Label>
                    <RangeInput
                      type="range"
                      min="0"
                      max="50"
                      value={selectedElementData.radius}
                      onChange={(e) =>
                        dispatch({
                          type: 'UPDATE_ELEMENT',
                          payload: { id: state.selectedElement, updates: { radius: parseFloat(e.target.value) } }
                        })
                      }
                    />
                  </PanelSection>
                )}

                <PanelSection>
                  <ToolButton onClick={() => dispatch({ type: 'DELETE_ELEMENT', payload: state.selectedElement })}>
                    🗑️ Delete
                  </ToolButton>
                </PanelSection>
              </>
            ) : (
              <PanelSection>
                <SectionTitle>Select Element</SectionTitle>
                <p style={{ fontSize: '13px', color: '#666' }}>
                  Click an element on the canvas to view and edit its properties
                </p>
              </PanelSection>
            )}
          </RightPanel>
        </EditorArea>
      </MainContent>

      {/* New Design Modal */}
      {showNewDesignModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            background: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '8px',
            padding: '32px',
            minWidth: '400px'
          }}>
            <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600' }}>Create New Design</h2>
            <PropertyInput
              type="text"
              placeholder="Design title..."
              value={designTitle}
              onChange={(e) => setDesignTitle(e.target.value)}
              autoFocus
            />
            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <TopBarButton onClick={() => setShowNewDesignModal(false)}>Cancel</TopBarButton>
              <TopBarButton onClick={createNewDesign} style={{ flex: 1, background: '#2563eb', borderColor: '#2563eb' }}>
                Create
              </TopBarButton>
            </div>
          </div>
        </div>
      )}
    </CanvasContainer>
  );
};

export default AICanvas;
