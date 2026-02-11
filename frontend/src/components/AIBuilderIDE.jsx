import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import {
  Plus, Save, Play, Trash2, Folder, File, Search, Settings,
  ChevronDown, ChevronRight, Terminal, Code, Copy, Check,
  AlertCircle, Loader, FolderOpen, RefreshCw, X
} from 'lucide-react';

const Container = styled.div`
  display: flex;
  height: 100vh;
  background: #0d1117;
  color: #c9d1d9;
  font-family: 'Fira Code', monospace;
`;

const Sidebar = styled.div`
  width: 250px;
  background: #010409;
  border-right: 1px solid #30363d;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const SidebarHeader = styled.div`
  padding: 16px;
  border-bottom: 1px solid #30363d;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
`;

const FileTree = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 8px;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  margin: 2px 0;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  
  ${props => props.selected && `
    background: #1f6feb;
    color: #fff;
  `}
  
  &:hover {
    background: rgba(31, 111, 235, 0.3);
  }
`;

const FileIcon = styled.span`
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
`;

const EditorContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #0d1117;
`;

const EditorTabs = styled.div`
  display: flex;
  gap: 0;
  background: #161b22;
  border-bottom: 1px solid #30363d;
  overflow-x: auto;
  padding: 0 8px;
`;

const EditorTab = styled.div`
  padding: 10px 16px;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  
  ${props => props.active && `
    border-bottom-color: #1f6feb;
    color: #58a6ff;
  `}
  
  &:hover {
    background: rgba(31, 111, 235, 0.1);
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #c9d1d9;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  
  &:hover {
    color: #f85149;
  }
`;

const EditorContent = styled.div`
  flex: 1;
  overflow: hidden;
`;

const BottomPanel = styled.div`
  height: 200px;
  border-top: 1px solid #30363d;
  background: #010409;
  display: flex;
  flex-direction: column;
`;

const TerminalHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-bottom: 1px solid #30363d;
  background: #161b22;
  font-size: 12px;
  font-weight: 600;
`;

const TerminalOutput = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  font-size: 12px;
  line-height: 1.5;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-word;
`;

const ControlBar = styled.div`
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
  flex-wrap: wrap;
`;

const Button = styled.button`
  padding: 6px 12px;
  background: #1f6feb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: #388bfd;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SecondaryButton = styled(Button)`
  background: transparent;
  border: 1px solid #30363d;
  color: #c9d1d9;
  
  &:hover {
    background: rgba(31, 111, 235, 0.1);
    border-color: #58a6ff;
  }
`;

const SelectInput = styled.select`
  padding: 6px 8px;
  background: #0d1117;
  color: #c9d1d9;
  border: 1px solid #30363d;
  border-radius: 4px;
  font-size: 12px;
  
  &:focus {
    outline: none;
    border-color: #58a6ff;
  }
`;

const TextInput = styled.input`
  padding: 6px 8px;
  background: #0d1117;
  color: #c9d1d9;
  border: 1px solid #30363d;
  border-radius: 4px;
  font-size: 12px;
  
  &:focus {
    outline: none;
    border-color: #58a6ff;
  }
`;

const AIBuilderIDE = () => {
  const [projectId, setProjectId] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [openFiles, setOpenFiles] = useState([]);
  const [terminalOutput, setTerminalOutput] = useState('');
  const [language, setLanguage] = useState('python');
  const [executing, setExecuting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [newFileName, setNewFileName] = useState('');
  const [showNewFile, setShowNewFile] = useState(false);
  const editorRef = useRef(null);

  const API_BASE = 'http://localhost:8000/api';
  const userId = localStorage.getItem('userId') || 'user-' + Math.random().toString(36).substr(2, 9);

  // Create project on mount or when needed
  useEffect(() => {
    if (!projectId) {
      createDefaultProject();
    }
  }, []);

  const createDefaultProject = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/ai-builder/project/create`, {
        user_id: userId,
        name: 'My Project',
        description: 'AI Builder Project',
        template: 'python'
      });
      
      setProjectId(response.data.project.id);
      setProjectName(response.data.project.name);
      await loadFileTree(response.data.project.id);
    } catch (err) {
      setError('Failed to create project: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const loadFileTree = async (id) => {
    try {
      const response = await axios.get(`${API_BASE}/ai-builder/project/${id}/tree`);
      const flattenTree = (items, prefix = '') => {
        let result = [];
        items?.forEach(item => {
          const path = prefix ? `${prefix}/${item.name}` : item.name;
          result.push({ ...item, fullPath: path });
          if (item.children) {
            result = [...result, ...flattenTree(item.children, path)];
          }
        });
        return result;
      };
      
      setFiles(flattenTree(response.data.tree));
    } catch (err) {
      setError('Failed to load files');
    }
  };

  const openFile = async (file) => {
    try {
      if (file.type !== 'file') return;
      
      const response = await axios.get(
        `${API_BASE}/ai-builder/project/${projectId}/files/${file.fullPath}`
      );
      
      setFileContent(response.data.content);
      setSelectedFile(file);
      
      if (!openFiles.find(f => f.fullPath === file.fullPath)) {
        setOpenFiles([...openFiles, file]);
      }
    } catch (err) {
      setError('Failed to open file');
    }
  };

  const saveFile = async () => {
    if (!selectedFile) return;
    
    try {
      await axios.put(
        `${API_BASE}/ai-builder/project/${projectId}/files/${selectedFile.fullPath}`,
        { content: fileContent }
      );
      setError('');
    } catch (err) {
      setError('Failed to save file');
    }
  };

  const executeCode = async () => {
    if (!selectedFile) {
      setError('Select a file to execute');
      return;
    }

    setExecuting(true);
    setTerminalOutput('$ Executing...\n');

    try {
      const response = await axios.post(
        `${API_BASE}/ai-builder/project/${projectId}/execute`,
        {
          code: fileContent,
          language: getLanguageFromFile(selectedFile.fullPath),
          timeout: 30
        }
      );

      const job = response.data.job;
      setTerminalOutput(`$ ${selectedFile.name}\n${job.output}${job.error ? '\n[ERROR]\n' + job.error : ''}`);
      setError('');
    } catch (err) {
      setTerminalOutput(`[ERROR] ${err.response?.data?.detail || err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  const getLanguageFromFile = (filename) => {
    if (filename.endsWith('.py')) return 'python';
    if (filename.endsWith('.js')) return 'javascript';
    if (filename.endsWith('.sh')) return 'bash';
    return 'python';
  };

  const createNewFile = async () => {
    if (!newFileName.trim()) return;

    try {
      await axios.post(
        `${API_BASE}/ai-builder/project/${projectId}/files`,
        {
          path: newFileName,
          content: '',
          is_directory: false
        }
      );
      
      setNewFileName('');
      setShowNewFile(false);
      await loadFileTree(projectId);
    } catch (err) {
      setError('Failed to create file');
    }
  };

  const deleteFile = async (file) => {
    try {
      await axios.delete(
        `${API_BASE}/ai-builder/project/${projectId}/files/${file.fullPath}`
      );
      
      setOpenFiles(openFiles.filter(f => f.fullPath !== file.fullPath));
      if (selectedFile?.fullPath === file.fullPath) {
        setSelectedFile(null);
        setFileContent('');
      }
      
      await loadFileTree(projectId);
    } catch (err) {
      setError('Failed to delete file');
    }
  };

  const closeFile = (file) => {
    const newOpenFiles = openFiles.filter(f => f.fullPath !== file.fullPath);
    setOpenFiles(newOpenFiles);
    
    if (selectedFile?.fullPath === file.fullPath) {
      setSelectedFile(newOpenFiles[newOpenFiles.length - 1] || null);
      if (selectedFile) {
        openFile(selectedFile);
      }
    }
  };

  return (
    <Container>
      {/* Sidebar - File Explorer */}
      <Sidebar>
        <SidebarHeader>
          <Folder size={16} />
          Files
        </SidebarHeader>
        
        <ControlBar style={{ borderBottom: '1px solid #30363d', flexDirection: 'column', gap: '4px' }}>
          <Button onClick={() => setShowNewFile(!showNewFile)} style={{ width: '100%' }}>
            <Plus size={14} /> New File
          </Button>
          {showNewFile && (
            <div style={{ display: 'flex', gap: '4px' }}>
              <TextInput
                placeholder="filename.py"
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createNewFile()}
                style={{ flex: 1 }}
              />
              <Button onClick={createNewFile} style={{ padding: '4px 8px' }}>
                ✓
              </Button>
            </div>
          )}
          <Button onClick={() => loadFileTree(projectId)} style={{ width: '100%' }}>
            <RefreshCw size={14} /> Refresh
          </Button>
        </ControlBar>

        <FileTree>
          {files.filter(f => f.type === 'file').map(file => (
            <FileItem
              key={file.fullPath}
              selected={selectedFile?.fullPath === file.fullPath}
              onClick={() => openFile(file)}
            >
              <FileIcon>
                <File size={14} />
              </FileIcon>
              <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {file.name}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteFile(file);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#c9d1d9',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                <X size={12} />
              </button>
            </FileItem>
          ))}
        </FileTree>
      </Sidebar>

      {/* Editor */}
      <EditorContainer>
        {/* Tabs */}
        {openFiles.length > 0 && (
          <EditorTabs>
            {openFiles.map(file => (
              <EditorTab
                key={file.fullPath}
                active={selectedFile?.fullPath === file.fullPath}
                onClick={() => openFile(file)}
              >
                <Code size={12} />
                {file.name}
                <CloseButton onClick={(e) => {
                  e.stopPropagation();
                  closeFile(file);
                }}>
                  <X size={12} />
                </CloseButton>
              </EditorTab>
            ))}
          </EditorTabs>
        )}

        {/* Control Bar */}
        <ControlBar>
          <Button onClick={saveFile}>
            <Save size={14} /> Save
          </Button>
          <Button onClick={executeCode} disabled={executing || !selectedFile}>
            {executing ? <Loader size={14} /> : <Play size={14} />}
            {executing ? 'Running...' : 'Run'}
          </Button>
          <SelectInput
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="bash">Bash</option>
          </SelectInput>
          {error && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f85149' }}>
              <AlertCircle size={14} />
              {error}
            </div>
          )}
        </ControlBar>

        {/* Monaco Editor */}
        {selectedFile ? (
          <EditorContent>
            <Editor
              height="100%"
              defaultLanguage={getLanguageFromFile(selectedFile.fullPath)}
              value={fileContent}
              onChange={(value) => setFileContent(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                fontFamily: 'Fira Code',
                wordWrap: 'on',
                scrollBeyondLastLine: false
              }}
            />
          </EditorContent>
        ) : (
          <EditorContent style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#666'
          }}>
            <div>Select a file to edit</div>
          </EditorContent>
        )}

        {/* Terminal */}
        <BottomPanel>
          <TerminalHeader>
            <Terminal size={12} />
            Terminal Output
          </TerminalHeader>
          <TerminalOutput>
            {terminalOutput}
          </TerminalOutput>
        </BottomPanel>
      </EditorContainer>
    </Container>
  );
};

export default AIBuilderIDE;
