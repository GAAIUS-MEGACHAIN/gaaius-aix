/**
 * BuildPage Enhancements - Replit-like IDE Features
 * Adds file explorer, code execution, and terminal to existing BuildPage
 */

import React, { useState, useCallback } from 'react';
import { ChevronRight, ChevronDown, FileCode, Folder, Plus, Trash2, Play, Package } from 'lucide-react';

export const FileExplorer = ({ files, activeFile, onSelectFile, onCreateFile, onDeleteFile }) => {
  const [expanded, setExpanded] = useState({});

  const toggleFolder = (folder) => {
    setExpanded(prev => ({ ...prev, [folder]: !prev[folder] }));
  };

  const getFileIcon = (filename) => {
    if (filename.endsWith('.html')) return '🌐';
    if (filename.endsWith('.css')) return '🎨';
    if (filename.endsWith('.js')) return '⚙️';
    if (filename.endsWith('.py')) return '🐍';
    if (filename.endsWith('.json')) return '📋';
    if (filename.endsWith('.md')) return '📝';
    return '📄';
  };

  const getParentFolder = (path) => {
    const parts = path.split('/');
    return parts.slice(0, -1).join('/');
  };

  const groupedFiles = {};
  Object.keys(files).forEach(filename => {
    const folder = getParentFolder(filename);
    if (!groupedFiles[folder]) groupedFiles[folder] = [];
    groupedFiles[folder].push(filename);
  });

  return (
    <div className="h-full bg-[#0d0d0d] border-r border-white/10 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-white/10 flex items-center justify-between">
        <h3 className="text-xs font-bold text-gray-400 uppercase">Files</h3>
        <button
          onClick={() => onCreateFile('new-file.js')}
          className="text-gray-400 hover:text-white transition p-1"
          title="New file"
        >
          <Plus className="w-3 h-3" />
        </button>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-auto">
        {Object.entries(groupedFiles).map(([folder, items]) => (
          <div key={folder || 'root'}>
            {folder && (
              <button
                onClick={() => toggleFolder(folder)}
                className="w-full flex items-center gap-1 px-3 py-2 text-xs hover:bg-white/5 text-gray-300"
              >
                {expanded[folder] ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                <Folder className="w-3 h-3" />
                {folder}
              </button>
            )}

            {(!folder || expanded[folder]) && items.map(file => (
              <button
                key={file}
                onClick={() => onSelectFile(file)}
                className={`w-full flex items-center gap-2 px-3 py-2 text-xs transition ${
                  activeFile === file
                    ? 'bg-orange-500/20 text-orange-400 border-l-2 border-orange-400'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <span className="text-sm">{getFileIcon(file)}</span>
                <span className="flex-1 text-left truncate">{file.split('/').pop()}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteFile(file);
                  }}
                  className="opacity-0 hover:opacity-100 text-red-400 transition"
                  title="Delete file"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export const CodeExecutionPanel = ({ onExecute, language = 'python', isLoading = false }) => {
  const [code, setCode] = useState('console.log("Hello, World!");');

  const languages = [
    { id: 'python', label: 'Python', icon: '🐍' },
    { id: 'javascript', label: 'JavaScript', icon: '⚙️' },
    { id: 'shell', label: 'Shell', icon: '💻' },
  ];

  return (
    <div className="h-full bg-[#0d0d0d] border-l border-white/10 flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-white/10">
        <div className="flex items-center gap-2 mb-3">
          <Play className="w-4 h-4 text-green-400" />
          <h3 className="text-xs font-bold text-gray-400 uppercase">Execute Code</h3>
        </div>
        
        <div className="flex gap-2">
          {languages.map(lang => (
            <button
              key={lang.id}
              onClick={() => {
                setCode(
                  lang.id === 'python' ? 'print("Hello, World!")' :
                  lang.id === 'javascript' ? 'console.log("Hello, World!");' :
                  'echo "Hello, World!"'
                );
              }}
              className="text-xs px-2 py-1 bg-white/10 hover:bg-white/20 rounded transition"
            >
              {lang.icon} {lang.label}
            </button>
          ))}
        </div>
      </div>

      {/* Editor */}
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        className="flex-1 bg-[#0a0a0a] text-sm font-mono p-3 resize-none border-b border-white/10 text-gray-300 focus:outline-none"
        placeholder="Enter code to execute..."
      />

      {/* Execute Button */}
      <div className="p-3">
        <button
          onClick={() => onExecute(code, language)}
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-900 text-white font-medium text-sm py-2 rounded transition flex items-center justify-center gap-2"
        >
          <Play className="w-4 h-4" />
          {isLoading ? 'Running...' : 'Execute'}
        </button>
      </div>
    </div>
  );
};

export const TerminalPanel = ({ output = [], isLoading = false }) => {
  return (
    <div className="h-full bg-[#0a0a0a] border-t border-white/10 flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-white/10 flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`} />
        <h3 className="text-xs font-bold text-gray-400 uppercase">Terminal Output</h3>
      </div>

      {/* Output */}
      <div className="flex-1 overflow-auto bg-[#0d0d0d] font-mono text-xs p-3">
        {output.length === 0 ? (
          <div className="text-gray-600">
            <div>$ Ready to execute code</div>
          </div>
        ) : (
          output.map((line, i) => (
            <div key={i} className={`py-0.5 ${
              line.type === 'error' ? 'text-red-400' :
              line.type === 'success' ? 'text-green-400' :
              line.type === 'warning' ? 'text-yellow-400' :
              line.type === 'info' ? 'text-blue-400' :
              'text-gray-400'
            }`}>
              {line.text}
            </div>
          ))
        )}
        {isLoading && <div className="text-green-400 animate-pulse">$ Running...</div>}
      </div>
    </div>
  );
};

export const PackageManagerPanel = ({ language = 'javascript', onInstall, isLoading = false }) => {
  const [packageName, setPackageName] = useState('');

  return (
    <div className="p-3 border-t border-white/10">
      <div className="flex items-center gap-2 mb-3">
        <Package className="w-4 h-4 text-blue-400" />
        <h4 className="text-xs font-bold text-gray-400">Install Package</h4>
      </div>

      <div className="flex gap-2">
        <select
          defaultValue={language}
          className="text-xs px-2 py-1 bg-white/10 rounded border border-white/20 text-gray-300"
        >
          <option value="javascript">npm</option>
          <option value="python">pip</option>
        </select>
        <input
          type="text"
          value={packageName}
          onChange={(e) => setPackageName(e.target.value)}
          placeholder="Package name..."
          className="flex-1 text-xs px-2 py-1 bg-white/5 rounded border border-white/20 text-gray-300 placeholder-gray-600 focus:outline-none"
        />
        <button
          onClick={() => {
            if (packageName.trim()) {
              onInstall(packageName, language);
              setPackageName('');
            }
          }}
          disabled={isLoading || !packageName.trim()}
          className="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 text-white rounded transition"
        >
          {isLoading ? 'Installing...' : 'Install'}
        </button>
      </div>
    </div>
  );
};
