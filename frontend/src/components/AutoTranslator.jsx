import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AutoTranslator = ({ apiUrl = 'http://127.0.0.1:8000' }) => {
  const [activeTab, setActiveTab] = useState('translate');
  const [text, setText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [supportedLanguages, setSupportedLanguages] = useState({});
  const [userLanguage, setUserLanguage] = useState('en');
  const [autoTranslate, setAutoTranslate] = useState(true);
  const [cacheStats, setCacheStats] = useState(null);
  const [translationHistory, setTranslationHistory] = useState([]);
  const [secondaryLanguages, setSecondaryLanguages] = useState([]);

  // Fetch supported languages on mount
  useEffect(() => {
    fetchSupportedLanguages();
  }, []);

  const fetchSupportedLanguages = useCallback(async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/languages/supported`);
      setSupportedLanguages(response.data.languages);
    } catch (err) {
      console.error('Error fetching languages:', err);
    }
  }, [apiUrl]);

  const translateText = useCallback(async (textToTranslate) => {
    if (!textToTranslate.trim()) {
      setError('Please enter text to translate');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${apiUrl}/api/translate/`, {
        text: textToTranslate,
        source_language: sourceLanguage,
        target_language: targetLanguage,
        use_cache: true,
      });

      const result = response.data;
      setTranslatedText(result.translated_text);
      setDetectedLanguage(result.detected_language);
      setConfidence(result.confidence);

      // Add to history
      setTranslationHistory((prev) => [
        {
          id: result.id,
          original: result.original_text,
          translated: result.translated_text,
          source: result.source_language,
          target: result.target_language,
          timestamp: new Date().toLocaleTimeString(),
          isCached: result.is_cached,
        },
        ...prev.slice(0, 9),
      ]);

      setSuccess('Translation completed successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Translation failed');
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, sourceLanguage, targetLanguage]);

  const detectLanguage = useCallback(async () => {
    if (!text.trim()) {
      setError('Please enter text to detect');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${apiUrl}/api/translate/detect`, {
        text,
      });

      const result = response.data;
      setDetectedLanguage(result.detected_language);
      setConfidence(result.confidence);
      setSourceLanguage(result.detected_language || 'auto');

      setSuccess(
        `Detected: ${result.language_name || result.detected_language} (${(result.confidence * 100).toFixed(1)}%)`
      );
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Language detection failed');
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, text]);

  const setLanguagePreference = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const userId = localStorage.getItem('userId') || 'default_user';
      const response = await axios.post(`${apiUrl}/api/language-preferences/`, {
        user_id: userId,
        primary_language: userLanguage,
        secondary_languages: secondaryLanguages,
        auto_translate: autoTranslate,
      });

      setSuccess('Language preference saved successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save preference');
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, userLanguage, autoTranslate, secondaryLanguages]);

  const getCacheStats = useCallback(async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/languages/stats`);
      setCacheStats(response.data);
    } catch (err) {
      console.error('Error fetching cache stats:', err);
    }
  }, [apiUrl]);

  const clearCache = useCallback(async () => {
    if (!window.confirm('Are you sure you want to clear the translation cache?')) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await axios.post(`${apiUrl}/api/languages/cache/clear`);
      setSuccess('Cache cleared successfully!');
      setCacheStats(null);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to clear cache');
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl]);

  const handleTranslate = () => {
    translateText(text);
  };

  const handleLanguageToggle = (lang) => {
    if (secondaryLanguages.includes(lang)) {
      setSecondaryLanguages(secondaryLanguages.filter((l) => l !== lang));
    } else {
      setSecondaryLanguages([...secondaryLanguages, lang]);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
    setTimeout(() => setSuccess(null), 2000);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
          <span className="text-4xl">🌍</span>
          Auto-Translator
        </h1>
        <p className="text-gray-600 mt-2">Translate to 50+ languages • Auto-detect language • Multi-platform support</p>
      </div>

      {/* Alert Messages */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">✕</button>
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 flex justify-between items-center">
          <span>{success}</span>
          <button onClick={() => setSuccess(null)} className="text-green-500 hover:text-green-700">✕</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {[
          { id: 'translate', label: '✉️ Translate', icon: '🔤' },
          { id: 'detect', label: '🔍 Detect Language', icon: '🎯' },
          { id: 'preferences', label: '⚙️ Preferences', icon: '👤' },
          { id: 'stats', label: '📊 Statistics', icon: '📈' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              if (tab.id === 'stats') getCacheStats();
            }}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === tab.id
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg p-6">
        {/* Translate Tab */}
        {activeTab === 'translate' && (
          <div className="space-y-4">
            {/* Language Selection */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Source Language</label>
                <select
                  value={sourceLanguage}
                  onChange={(e) => setSourceLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="auto">🔍 Auto-detect</option>
                  {Object.entries(supportedLanguages).map(([code, name]) => (
                    <option key={code} value={code}>
                      {name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Target Language</label>
                <select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  {Object.entries(supportedLanguages).map(([code, name]) => (
                    <option key={code} value={code}>
                      {name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Text Areas */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Text to Translate</label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Enter text to translate..."
                  className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                />
                <div className="mt-2 text-sm text-gray-500">
                  {text.length} characters
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Translated Text</label>
                <textarea
                  value={translatedText}
                  readOnly
                  placeholder="Translated text will appear here..."
                  className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 resize-none"
                />
                {translatedText && (
                  <button
                    onClick={() => copyToClipboard(translatedText)}
                    className="mt-2 text-sm px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200"
                  >
                    📋 Copy
                  </button>
                )}
              </div>
            </div>

            {/* Translation Info */}
            {detectedLanguage && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm">
                  <span className="font-semibold">Detected Language:</span> {detectedLanguage}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Confidence:</span> {(confidence * 100).toFixed(1)}%
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleTranslate}
                disabled={isLoading || !text.trim()}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Translating...' : '🚀 Translate'}
              </button>
              <button
                onClick={detectLanguage}
                disabled={isLoading || !text.trim()}
                className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Detecting...' : '🔍 Detect'}
              </button>
            </div>

            {/* Translation History */}
            {translationHistory.length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">📜 Recent Translations</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {translationHistory.map((item) => (
                    <div key={item.id} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="text-sm text-gray-600">
                            <span className="font-semibold">{item.source.toUpperCase()}</span> → <span className="font-semibold">{item.target.toUpperCase()}</span>
                          </p>
                          <p className="text-sm text-gray-800 mt-1">{item.original}</p>
                          <p className="text-sm text-gray-700 italic">{item.translated}</p>
                        </div>
                        <div className="text-right ml-2">
                          <p className="text-xs text-gray-500">{item.timestamp}</p>
                          {item.isCached && <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">💾 Cached</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Primary Language</label>
              <select
                value={userLanguage}
                onChange={(e) => setUserLanguage(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                {Object.entries(supportedLanguages).map(([code, name]) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </select>
              <p className="text-sm text-gray-500 mt-2">
                Messages will be automatically translated to this language
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">Secondary Languages</label>
              <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto p-3 bg-gray-50 rounded-lg border border-gray-200">
                {Object.entries(supportedLanguages).map(([code, name]) => (
                  <label key={code} className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded">
                    <input
                      type="checkbox"
                      checked={secondaryLanguages.includes(code)}
                      onChange={() => handleLanguageToggle(code)}
                      className="w-4 h-4 text-indigo-600 rounded"
                    />
                    <span className="text-sm">{name}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoTranslate}
                  onChange={(e) => setAutoTranslate(e.target.checked)}
                  className="w-5 h-5 text-indigo-600 rounded"
                />
                <span className="text-sm font-semibold text-gray-700">
                  Enable Auto-Translation for Chat Messages
                </span>
              </label>
              <p className="text-sm text-gray-500 mt-2">
                Messages will be automatically translated to your preferred language
              </p>
            </div>

            <button
              onClick={setLanguagePreference}
              disabled={isLoading}
              className="w-full px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? 'Saving...' : '💾 Save Preferences'}
            </button>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                ✅ Your language preferences will be applied across all chat modes and messaging features
              </p>
            </div>
          </div>
        )}

        {/* Statistics Tab */}
        {activeTab === 'stats' && (
          <div className="space-y-6">
            {cacheStats ? (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
                    <p className="text-sm text-gray-600">Cache Size</p>
                    <p className="text-2xl font-bold text-indigo-600">
                      {cacheStats.cache.cache_size}/{cacheStats.cache.max_cache_size}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {cacheStats.cache.cache_usage_percent.toFixed(1)}% used
                    </p>
                  </div>
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-gray-600">User Preferences</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {cacheStats.cache.preferences_count}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Active users
                    </p>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Translation Paths</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {Object.entries(cacheStats.translation_paths).map(([path, count]) => (
                      <div key={path} className="p-3 bg-gray-50 rounded-lg flex justify-between items-center">
                        <span className="text-sm text-gray-700">{path}</span>
                        <span className="font-semibold text-indigo-600">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  onClick={clearCache}
                  disabled={isLoading}
                  className="w-full px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isLoading ? 'Clearing...' : '🗑️ Clear Cache'}
                </button>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Click on the Statistics tab to load cache stats</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Supported Features */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { icon: '🌐', title: '50+ Languages', desc: 'Support for 50+ languages worldwide' },
          { icon: '🎯', title: 'Auto-Detect', desc: 'Automatic language detection' },
          { icon: '💾', title: 'Caching', desc: '10,000 translations cached' },
          { icon: '⚡', title: 'Real-time', desc: 'Instant translation & sync' },
        ].map((feature, i) => (
          <div key={i} className="p-4 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg border border-indigo-100 text-center">
            <p className="text-3xl mb-2">{feature.icon}</p>
            <p className="font-semibold text-gray-800">{feature.title}</p>
            <p className="text-sm text-gray-600 mt-1">{feature.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AutoTranslator;
