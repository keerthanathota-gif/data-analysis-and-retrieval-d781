import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CFRDashboard.css';

const CFRDashboard = () => {
  const [activeTab, setActiveTab] = useState('pipeline');
  const [stats, setStats] = useState({ chapters: 0, sections: 0, embeddings: 0 });

  // Pipeline state
  const [pipelineUrls, setPipelineUrls] = useState('https://www.govinfo.gov/bulkdata/CFR/2025/title-16/');
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineResults, setPipelineResults] = useState(null);


  // RAG state
  const [ragQuery, setRagQuery] = useState('');
  const [ragLevel, setRagLevel] = useState('all');
  const [ragTopK, setRagTopK] = useState(10);
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResults, setRagResults] = useState(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('chapter');
  const [searchTopK, setSearchTopK] = useState(10);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);

  // Advanced Analysis state (Redundancy/Parity/Overlap)
  const [advancedLevel, setAdvancedLevel] = useState('section');
  const [advancedMaxItems, setAdvancedMaxItems] = useState('100');
  const [advancedLoading, setAdvancedLoading] = useState(false);
  const [advancedResults, setAdvancedResults] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [comparisonModal, setComparisonModal] = useState(null);
  const [loadingComparison, setLoadingComparison] = useState(false);

  useEffect(() => {
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let interval;
    if (pipelineLoading) {
      interval = setInterval(checkPipelineStatus, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pipelineLoading]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const loadStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/search/stats');
      const data = response.data;
      setStats({
        chapters: data.total_chapters || 0,
        sections: data.total_sections || 0,
        embeddings: data.total_embeddings || 0
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const runPipeline = async () => {
    if (!pipelineUrls.trim()) {
      alert('Please enter at least one CFR URL');
      return;
    }

    setPipelineLoading(true);
    setPipelineResults(null);

    try {
      const urls = pipelineUrls.split('\n').map(url => url.trim()).filter(url => url.length > 0);

      console.log('Starting pipeline with URLs:', urls);
      console.log('Auth headers:', getAuthHeaders());

      const response = await axios.post(
        'http://localhost:8000/admin/pipeline/run',
        { urls },
        getAuthHeaders()
      );

      console.log('Pipeline response:', response.data);
      setPipelineResults({ message: response.data.message, status: 'started' });
    } catch (error) {
      console.error('Pipeline error:', error);
      console.error('Error response:', error.response);

      const errorMessage = error.response?.data?.detail || error.message || 'Failed to start pipeline';

      setPipelineResults({
        message: errorMessage,
        status: 'error',
        error_message: errorMessage
      });
      setPipelineLoading(false);

      alert(`Pipeline Error: ${errorMessage}`);
    }
  };

  const checkPipelineStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admin/pipeline/status', getAuthHeaders());
      const status = response.data;

      setPipelineResults(status);

      if (status.state === 'completed') {
        setPipelineLoading(false);
        await loadStats();
      } else if (status.state === 'error') {
        setPipelineLoading(false);
      }
    } catch (error) {
      console.error('Failed to check pipeline status:', error);
    }
  };

  const resetDatabase = async () => {
    if (!window.confirm('Are you sure you want to reset the database? This will delete all CFR data.')) {
      return;
    }

    try {
      await axios.post('http://localhost:8000/admin/pipeline/reset', {}, getAuthHeaders());
      await loadStats();
      alert('Database reset successfully');
    } catch (error) {
      alert('Failed to reset database: ' + (error.response?.data?.detail || error.message));
    }
  };


  const runRAGQuery = async () => {
    if (!ragQuery.trim()) {
      alert('Please enter a query');
      return;
    }

    setRagLoading(true);
    setRagResults(null);

    try {
      const response = await axios.post(
        'http://localhost:8000/search/query',
        {
          query: ragQuery,
          level: ragLevel,
          top_k: ragTopK
        },
        getAuthHeaders()
      );
      setRagResults(response.data);
    } catch (error) {
      setRagResults({
        message: error.response?.data?.detail || 'Query failed',
        status: 'error'
      });
    } finally {
      setRagLoading(false);
    }
  };

  const runSearch = async () => {
    if (!searchQuery.trim()) {
      alert('Please enter a search query');
      return;
    }

    setSearchLoading(true);
    setSearchResults(null);

    try {
      const response = await axios.get(
        `http://localhost:8000/search/similar/${encodeURIComponent(searchQuery)}`,
        {
          params: {
            search_type: searchType,
            top_k: searchTopK
          },
          ...getAuthHeaders()
        }
      );
      setSearchResults(response.data);
    } catch (error) {
      setSearchResults({
        message: error.response?.data?.detail || 'Search failed',
        status: 'error'
      });
    } finally {
      setSearchLoading(false);
    }
  };

  const runAdvancedAnalysis = async () => {
    setAdvancedLoading(true);
    setAdvancedResults(null);
    setSelectedCategory('all');

    try {
      const params = { level: advancedLevel };

      // Add max_items if specified
      if (advancedMaxItems && advancedMaxItems.trim() !== '') {
        const maxItems = parseInt(advancedMaxItems);
        if (!isNaN(maxItems) && maxItems > 0) {
          params.max_items = maxItems;
        }
      }

      const response = await axios.post(
        'http://localhost:8000/search/analysis/advanced',
        null,
        {
          params: params,
          ...getAuthHeaders()
        }
      );
      setAdvancedResults(response.data);
    } catch (error) {
      setAdvancedResults({
        error: true,
        message: error.response?.data?.detail || 'Advanced analysis failed'
      });
    } finally {
      setAdvancedLoading(false);
    }
  };

  const viewComparisonDetails = async (item1_id, item2_id, category, similarity_score) => {
    setLoadingComparison(true);
    setComparisonModal(null);

    try {
      console.log('Fetching section details for IDs:', item1_id, item2_id);

      // Fetch details for both items
      const [item1Response, item2Response] = await Promise.all([
        axios.get(`http://localhost:8000/search/section/${item1_id}`, getAuthHeaders()),
        axios.get(`http://localhost:8000/search/section/${item2_id}`, getAuthHeaders())
      ]);

      console.log('Item 1 Response:', item1Response.data);
      console.log('Item 1 Text Length:', item1Response.data.text?.length || 0);
      console.log('Item 2 Response:', item2Response.data);
      console.log('Item 2 Text Length:', item2Response.data.text?.length || 0);

      // Check if text exists
      if (!item1Response.data.text || !item2Response.data.text) {
        console.warn('WARNING: One or both sections have no text!');
        console.warn('Item 1 has text:', !!item1Response.data.text);
        console.warn('Item 2 has text:', !!item2Response.data.text);
      }

      setComparisonModal({
        item1: item1Response.data,
        item2: item2Response.data,
        category: category,
        similarity_score: similarity_score
      });
    } catch (error) {
      console.error('Error fetching comparison details:', error);
      alert('Failed to load comparison details: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoadingComparison(false);
    }
  };

  const closeComparisonModal = () => {
    setComparisonModal(null);
  };

  // Helper function to highlight similar words between two texts
  const highlightSimilarText = (text1, text2) => {
    if (!text1 || !text2) return { text1: text1 || '', text2: text2 || '' };

    // Simple word-based comparison
    const words1 = text1.toLowerCase().split(/\s+/);
    const words2 = text2.toLowerCase().split(/\s+/);
    const commonWords = new Set(words1.filter(word => words2.includes(word) && word.length > 3));

    // Helper to escape special regex characters
    const escapeRegex = (str) => {
      return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    };

    const highlightText = (text, words) => {
      let highlighted = text;
      words.forEach(word => {
        try {
          // Escape special regex characters in the word
          const escapedWord = escapeRegex(word);
          const regex = new RegExp(`\\b(${escapedWord})\\b`, 'gi');
          highlighted = highlighted.replace(regex, '<mark style="background-color: #fef08a; padding: 2px 4px; border-radius: 2px;">$1</mark>');
        } catch (e) {
          // If regex still fails, skip this word
          console.warn('Failed to highlight word:', word, e);
        }
      });
      return highlighted;
    };

    return {
      text1: highlightText(text1, commonWords),
      text2: highlightText(text2, commonWords)
    };
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <div className="app-container">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <div className="dashboard-header-left">
          <div className="dashboard-logo">
            <i className="fas fa-cube"></i>
          </div>
          <h1 className="dashboard-title">CFR Pipeline System</h1>
        </div>
        <button className="sign-out-btn" onClick={handleLogout}>
          <i className="fas fa-sign-out-alt"></i>
          Sign Out
        </button>
      </div>

      <div className="dashboard-layout">
        {/* Horizontal Navigation Tabs */}
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'pipeline' ? 'active' : ''}`} 
            onClick={() => setActiveTab('pipeline')}
          >
            Pipeline
          </button>
          <button 
            className={`nav-tab ${activeTab === 'advanced' ? 'active' : ''}`} 
            onClick={() => setActiveTab('advanced')}
          >
            Analysis
          </button>
          <button 
            className={`nav-tab ${activeTab === 'rag' ? 'active' : ''}`} 
            onClick={() => setActiveTab('rag')}
          >
            RAG Query
          </button>
        </div>

        {/* Content Area */}
        <div className="dashboard-content">
      {/* Pipeline Tab */}
      {activeTab === 'pipeline' && (
        <div className="tab-content active">
          {/* Statistics Card */}
          <div className="card">
            <div className="card-header">
              <i className="fas fa-chart-bar"></i>
              <h2>Database Statistics</h2>
            </div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '20px'
            }}>
              {/* Total Chapters */}
              <div style={{
                padding: '24px',
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                borderRadius: '12px',
                border: '2px solid #10b981',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-20px',
                  right: '-20px',
                  width: '80px',
                  height: '80px',
                  background: 'rgba(16, 185, 129, 0.1)',
                  borderRadius: '50%'
                }}></div>
                <div style={{ position: 'relative', zIndex: 1 }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '12px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      background: '#10b981',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '1.4em'
                    }}>
                      <i className="fas fa-book"></i>
                    </div>
                    <div>
                      <div style={{
                        fontSize: '2.5em',
                        fontWeight: 'bold',
                        color: '#047857',
                        lineHeight: '1'
                      }}>
                        {stats.chapters}
                      </div>
                    </div>
                  </div>
                  <div style={{
                    fontSize: '0.95rem',
                    color: '#065f46',
                    fontWeight: '600'
                  }}>
                    Total Chapters
                  </div>
                </div>
              </div>

              {/* Total Regulations */}
              <div style={{
                padding: '24px',
                background: 'linear-gradient(135deg, #ecfccb 0%, #d9f99d 100%)',
                borderRadius: '12px',
                border: '2px solid #84cc16',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-20px',
                  right: '-20px',
                  width: '80px',
                  height: '80px',
                  background: 'rgba(132, 204, 22, 0.1)',
                  borderRadius: '50%'
                }}></div>
                <div style={{ position: 'relative', zIndex: 1 }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '12px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      background: '#84cc16',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '1.4em'
                    }}>
                      <i className="fas fa-file-alt"></i>
                    </div>
                    <div>
                      <div style={{
                        fontSize: '2.5em',
                        fontWeight: 'bold',
                        color: '#4d7c0f',
                        lineHeight: '1'
                      }}>
                        {stats.sections}
                      </div>
                    </div>
                  </div>
                  <div style={{
                    fontSize: '0.95rem',
                    color: '#365314',
                    fontWeight: '600'
                  }}>
                    Total Regulations
                  </div>
                </div>
              </div>

              {/* Total Embeddings */}
              <div style={{
                padding: '24px',
                background: 'linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%)',
                borderRadius: '12px',
                border: '2px solid #14b8a6',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-20px',
                  right: '-20px',
                  width: '80px',
                  height: '80px',
                  background: 'rgba(20, 184, 166, 0.1)',
                  borderRadius: '50%'
                }}></div>
                <div style={{ position: 'relative', zIndex: 1 }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '12px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      background: '#14b8a6',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '1.4em'
                    }}>
                      <i className="fas fa-brain"></i>
                    </div>
                    <div>
                      <div style={{
                        fontSize: '2.5em',
                        fontWeight: 'bold',
                        color: '#0f766e',
                        lineHeight: '1'
                      }}>
                        {stats.embeddings}
                      </div>
                    </div>
                  </div>
                  <div style={{
                    fontSize: '0.95rem',
                    color: '#134e4a',
                    fontWeight: '600'
                  }}>
                    Total Embeddings
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Pipeline Control Card */}
          <div className="card" style={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '2px solid #e2e8f0'
          }}>
            <div className="card-header" style={{ borderBottom: '2px solid #e2e8f0' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white'
              }}>
                <i className="fas fa-rocket"></i>
              </div>
              <h2>Data Pipeline Control</h2>
            </div>

            <div style={{
              padding: '16px',
              background: '#f0fdf4',
              borderRadius: '8px',
              border: '1px solid #bbf7d0',
              marginBottom: '24px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <i className="fas fa-info-circle" style={{ color: '#10b981', fontSize: '1.1em' }}></i>
                <strong style={{ color: '#065f46' }}>Pipeline Process</strong>
              </div>
              <p style={{
                margin: 0,
                color: '#047857',
                fontSize: '0.9rem',
                lineHeight: '1.6'
              }}>
                Enter CFR URLs to crawl, parse XML files, store in database, and generate AI embeddings. You can add multiple URLs.
              </p>
            </div>

            <div className="form-group">
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.95rem',
                fontWeight: '600',
                color: '#0f172a',
                marginBottom: '10px'
              }}>
                <i className="fas fa-link" style={{ color: '#10b981' }}></i>
                CFR URLs (one per line)
              </label>
              <textarea
                value={pipelineUrls}
                onChange={(e) => setPipelineUrls(e.target.value)}
                rows="4"
                placeholder="https://www.govinfo.gov/bulkdata/CFR/2025/title-16/"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                  fontFamily: 'monospace',
                  transition: 'all 0.2s'
                }}
              />
              <small style={{
                color: '#64748b',
                display: 'block',
                marginTop: '8px',
                fontSize: '0.85rem'
              }}>
                Example: https://www.govinfo.gov/bulkdata/CFR/YEAR/title-NUMBER/
              </small>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '16px',
              marginTop: '24px'
            }}>
              <button
                className="btn btn-primary"
                onClick={runPipeline}
                disabled={pipelineLoading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  padding: '14px 24px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '1rem',
                  cursor: pipelineLoading ? 'not-allowed' : 'pointer',
                  opacity: pipelineLoading ? 0.6 : 1,
                  transition: 'all 0.2s',
                  boxShadow: '0 2px 4px rgba(16, 185, 129, 0.2)'
                }}
              >
                <i className="fas fa-play"></i> Run Pipeline
              </button>
              <button
                className="btn btn-danger"
                onClick={resetDatabase}
                disabled={pipelineLoading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  padding: '14px 24px',
                  background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '1rem',
                  cursor: pipelineLoading ? 'not-allowed' : 'pointer',
                  opacity: pipelineLoading ? 0.6 : 1,
                  transition: 'all 0.2s',
                  boxShadow: '0 2px 4px rgba(249, 115, 22, 0.2)'
                }}
              >
                <i className="fas fa-trash-alt"></i> Reset Database
              </button>
            </div>
          </div>

          {pipelineLoading && (
            <div className="loading">
              <div className="spinner"></div>
              <p className="loading-text">Processing pipeline...</p>
              {pipelineResults && (
                <p style={{ marginTop: '10px', color: '#6366f1' }}>
                  {pipelineResults.current_step || 'Starting...'}
                </p>
              )}
            </div>
          )}

          {pipelineResults && !pipelineLoading && (
            <div className={`result-box ${pipelineResults.state === 'completed' ? 'success' : pipelineResults.state === 'error' ? 'error' : ''}`}>
              <h3>Pipeline Results</h3>
              <p>{pipelineResults.message || pipelineResults.error_message || 'Pipeline completed'}</p>
              {pipelineResults.steps_completed && (
                <ul>
                  {pipelineResults.steps_completed.map((step, i) => (
                    <li key={i}>✓ {step}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}

      {/* Advanced Analysis Tab - Redundancy/Parity/Overlap */}
      {activeTab === 'advanced' && (
        <div className="tab-content active">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-network-wired"></i>
              <h2>Advanced Regulation Analysis</h2>
            </div>
            <p className="card-description">
              <i className="fas fa-info-circle"></i>
              Detect redundancy, parity, and overlap across regulations using semantic similarity.
              <br />
              <strong style={{color: '#dc2626'}}>Redundancy (≥95%)</strong>: Nearly identical - consolidate
              {' '} | {' '}
              <strong style={{color: '#f59e0b'}}>Parity (85-95%)</strong>: Very similar - review for conflicts
              {' '} | {' '}
              <strong style={{color: '#3b82f6'}}>Overlap (70-85%)</strong>: Related - add cross-references
            </p>

            <div className="form-group">
              <label><i className="fas fa-layer-group"></i> Analysis Level</label>
              <select value={advancedLevel} onChange={(e) => setAdvancedLevel(e.target.value)}>
                <option value="chapter">Chapter Level</option>
                <option value="subchapter">Subchapter Level</option>
                <option value="section">Section Level</option>
              </select>
            </div>

            <div className="form-group">
              <label>
                <i className="fas fa-hashtag"></i> Max Items to Analyze (for performance)
              </label>
              <input
                type="number"
                value={advancedMaxItems}
                onChange={(e) => setAdvancedMaxItems(e.target.value)}
                placeholder="e.g., 100, 200, 500"
                min="10"
                max="10000"
              />
              <small style={{ color: 'var(--text-light)', display: 'block', marginTop: '5px' }}>
                Limit analysis to first N items for faster results. Leave empty to analyze all items.
                {stats.sections > 0 && ` (You have ${stats.sections} sections total)`}
              </small>
            </div>

            <button className="btn btn-primary" onClick={runAdvancedAnalysis} disabled={advancedLoading}>
              <i className="fas fa-play"></i> Run Advanced Analysis
            </button>
          </div>

          {advancedLoading && (
            <div className="loading">
              <div className="spinner"></div>
              <p className="loading-text">Analyzing regulation relationships...</p>
            </div>
          )}

          {advancedResults && !advancedResults.error && (
            <div>
              {/* Health Score Card */}
              <div className="card" style={{marginTop: '20px'}}>
                <div className="card-header">
                  <i className="fas fa-heartbeat"></i>
                  <h2>Corpus Health Score</h2>
                </div>
                <div style={{padding: '20px'}}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '20px'}}>
                    <div style={{textAlign: 'center'}}>
                      <div style={{
                        fontSize: '72px',
                        fontWeight: 'bold',
                        lineHeight: '1',
                        color: advancedResults.health_score?.health_color || '#10b981'
                      }}>
                        {advancedResults.health_score?.grade || 'N/A'}
                      </div>
                      <div style={{
                        fontSize: '14px',
                        color: '#6b7280',
                        marginTop: '5px'
                      }}>
                        {advancedResults.health_score?.rating || 'N/A'}
                      </div>
                    </div>
                    <div style={{flex: 1}}>
                      <div style={{fontSize: '24px', fontWeight: 'bold', marginBottom: '5px'}}>
                        {advancedResults.health_score?.score || 0}/100
                      </div>
                      <div style={{color: '#6b7280', marginBottom: '10px'}}>
                        {advancedResults.health_score?.description || 'No data'}
                      </div>
                      <div style={{fontSize: '13px', color: '#6b7280'}}>
                        <div><strong>Redundancy:</strong> {advancedResults.health_score?.redundancy_rate || 0}%</div>
                        <div><strong>Parity:</strong> {advancedResults.health_score?.parity_rate || 0}%</div>
                        <div><strong>Overlap:</strong> {advancedResults.health_score?.overlap_rate || 0}%</div>
                      </div>
                    </div>
                  </div>
                  <div style={{
                    marginTop: '20px',
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '15px'
                  }}>
                    <div style={{
                      padding: '15px',
                      background: 'rgba(220, 38, 38, 0.1)',
                      borderRadius: '8px',
                      textAlign: 'center'
                    }}>
                      <div style={{fontSize: '24px', color: '#dc2626', fontWeight: 'bold'}}>
                        {advancedResults.health_score?.breakdown?.redundancy || 0}
                      </div>
                      <div style={{fontSize: '14px', color: '#6b7280'}}>Redundancy</div>
                    </div>
                    <div style={{
                      padding: '15px',
                      background: 'rgba(245, 158, 11, 0.1)',
                      borderRadius: '8px',
                      textAlign: 'center'
                    }}>
                      <div style={{fontSize: '24px', color: '#f59e0b', fontWeight: 'bold'}}>
                        {advancedResults.health_score?.breakdown?.parity || 0}
                      </div>
                      <div style={{fontSize: '14px', color: '#6b7280'}}>Parity</div>
                    </div>
                    <div style={{
                      padding: '15px',
                      background: 'rgba(59, 130, 246, 0.1)',
                      borderRadius: '8px',
                      textAlign: 'center'
                    }}>
                      <div style={{fontSize: '24px', color: '#3b82f6', fontWeight: 'bold'}}>
                        {advancedResults.health_score?.breakdown?.overlap || 0}
                      </div>
                      <div style={{fontSize: '14px', color: '#6b7280'}}>Overlap</div>
                    </div>
                  </div>
                </div>
              </div>


              {/* Category Filter */}
              <div className="card" style={{marginTop: '20px'}}>
                <div className="card-header">
                  <i className="fas fa-filter"></i>
                  <h2>Relationship Details</h2>
                </div>
                <div style={{padding: '20px'}}>
                  <div style={{marginBottom: '15px'}}>
                    <label style={{marginRight: '10px'}}><strong>Filter by Category:</strong></label>
                    <select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      style={{
                        padding: '8px 15px',
                        borderRadius: '6px',
                        border: '1px solid #d1d5db',
                        fontSize: '14px'
                      }}
                    >
                      <option value="all">All Categories</option>
                      <option value="redundancy">Redundancy Only</option>
                      <option value="parity">Parity Only</option>
                      <option value="overlap">Overlap Only</option>
                    </select>
                  </div>

                  {/* Relationships Display */}
                  {advancedResults.categorized_relationships && (
                    <div>
                      {/* Redundancy */}
                      {(selectedCategory === 'all' || selectedCategory === 'redundancy') &&
                       advancedResults.categorized_relationships.redundancy?.length > 0 && (
                        <div style={{marginBottom: '20px'}}>
                          <h3 style={{
                            fontSize: '18px',
                            color: '#dc2626',
                            marginBottom: '10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px'
                          }}>
                            <i className="fas fa-exclamation-circle"></i>
                            Redundancy ({advancedResults.categorized_relationships.redundancy.length})
                          </h3>
                          {advancedResults.categorized_relationships.redundancy.map((rel, i) => (
                            <div key={i} style={{
                              padding: '15px',
                              background: 'rgba(220, 38, 38, 0.05)',
                              border: '2px solid #dc2626',
                              borderRadius: '8px',
                              marginBottom: '10px'
                            }}>
                              <div style={{fontWeight: 'bold', marginBottom: '5px'}}>
                                {rel.item1_name} ↔ {rel.item2_name}
                              </div>
                              <div style={{fontSize: '14px', color: '#6b7280', marginBottom: '5px'}}>
                                Similarity: <strong style={{color: '#dc2626'}}>{(rel.similarity_score * 100).toFixed(1)}%</strong>
                              </div>
                              <div style={{fontSize: '13px', color: '#6b7280', marginBottom: '5px'}}>
                                {rel.explanation}
                              </div>
                              <div style={{
                                fontSize: '13px',
                                padding: '8px',
                                background: 'white',
                                borderRadius: '4px',
                                marginTop: '8px'
                              }}>
                                <i className="fas fa-lightbulb"></i> <strong>Recommendation:</strong> {rel.recommendation}
                              </div>
                              {advancedLevel === 'section' && (
                                <button
                                  onClick={() => viewComparisonDetails(rel.item1_id, rel.item2_id, 'redundancy', rel.similarity_score)}
                                  style={{
                                    marginTop: '10px',
                                    padding: '8px 16px',
                                    background: '#dc2626',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontSize: '13px',
                                    fontWeight: '500'
                                  }}
                                  onMouseOver={(e) => e.target.style.background = '#b91c1c'}
                                  onMouseOut={(e) => e.target.style.background = '#dc2626'}
                                >
                                  <i className="fas fa-eye"></i> View Full Text Comparison
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Parity */}
                      {(selectedCategory === 'all' || selectedCategory === 'parity') &&
                       advancedResults.categorized_relationships.parity?.length > 0 && (
                        <div style={{marginBottom: '20px'}}>
                          <h3 style={{
                            fontSize: '18px',
                            color: '#f59e0b',
                            marginBottom: '10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px'
                          }}>
                            <i className="fas fa-balance-scale"></i>
                            Parity ({advancedResults.categorized_relationships.parity.length})
                          </h3>
                          {advancedResults.categorized_relationships.parity.map((rel, i) => (
                            <div key={i} style={{
                              padding: '15px',
                              background: 'rgba(245, 158, 11, 0.05)',
                              border: '2px solid #f59e0b',
                              borderRadius: '8px',
                              marginBottom: '10px'
                            }}>
                              <div style={{fontWeight: 'bold', marginBottom: '5px'}}>
                                {rel.item1_name} ↔ {rel.item2_name}
                              </div>
                              <div style={{fontSize: '14px', color: '#6b7280', marginBottom: '5px'}}>
                                Similarity: <strong style={{color: '#f59e0b'}}>{(rel.similarity_score * 100).toFixed(1)}%</strong>
                              </div>
                              <div style={{fontSize: '13px', color: '#6b7280', marginBottom: '5px'}}>
                                {rel.explanation}
                              </div>
                              <div style={{
                                fontSize: '13px',
                                padding: '8px',
                                background: 'white',
                                borderRadius: '4px',
                                marginTop: '8px'
                              }}>
                                <i className="fas fa-lightbulb"></i> <strong>Recommendation:</strong> {rel.recommendation}
                              </div>
                              {advancedLevel === 'section' && (
                                <button
                                  onClick={() => viewComparisonDetails(rel.item1_id, rel.item2_id, 'parity', rel.similarity_score)}
                                  style={{
                                    marginTop: '10px',
                                    padding: '8px 16px',
                                    background: '#f59e0b',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontSize: '13px',
                                    fontWeight: '500'
                                  }}
                                  onMouseOver={(e) => e.target.style.background = '#d97706'}
                                  onMouseOut={(e) => e.target.style.background = '#f59e0b'}
                                >
                                  <i className="fas fa-eye"></i> View Full Text Comparison
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Overlap */}
                      {(selectedCategory === 'all' || selectedCategory === 'overlap') &&
                       advancedResults.categorized_relationships.overlap?.length > 0 && (
                        <div style={{marginBottom: '20px'}}>
                          <h3 style={{
                            fontSize: '18px',
                            color: '#3b82f6',
                            marginBottom: '10px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px'
                          }}>
                            <i className="fas fa-link"></i>
                            Overlap ({advancedResults.categorized_relationships.overlap.length})
                          </h3>
                          {advancedResults.categorized_relationships.overlap.map((rel, i) => (
                            <div key={i} style={{
                              padding: '15px',
                              background: 'rgba(59, 130, 246, 0.05)',
                              border: '2px solid #3b82f6',
                              borderRadius: '8px',
                              marginBottom: '10px'
                            }}>
                              <div style={{fontWeight: 'bold', marginBottom: '5px'}}>
                                {rel.item1_name} ↔ {rel.item2_name}
                              </div>
                              <div style={{fontSize: '14px', color: '#6b7280', marginBottom: '5px'}}>
                                Similarity: <strong style={{color: '#3b82f6'}}>{(rel.similarity_score * 100).toFixed(1)}%</strong>
                              </div>
                              <div style={{fontSize: '13px', color: '#6b7280', marginBottom: '5px'}}>
                                {rel.explanation}
                              </div>
                              <div style={{
                                fontSize: '13px',
                                padding: '8px',
                                background: 'white',
                                borderRadius: '4px',
                                marginTop: '8px'
                              }}>
                                <i className="fas fa-lightbulb"></i> <strong>Recommendation:</strong> {rel.recommendation}
                              </div>
                              {advancedLevel === 'section' && (
                                <button
                                  onClick={() => viewComparisonDetails(rel.item1_id, rel.item2_id, 'overlap', rel.similarity_score)}
                                  style={{
                                    marginTop: '10px',
                                    padding: '8px 16px',
                                    background: '#3b82f6',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontSize: '13px',
                                    fontWeight: '500'
                                  }}
                                  onMouseOver={(e) => e.target.style.background = '#2563eb'}
                                  onMouseOut={(e) => e.target.style.background = '#3b82f6'}
                                >
                                  <i className="fas fa-eye"></i> View Full Text Comparison
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {advancedResults && advancedResults.error && (
            <div className="result-box error">
              <h3>Analysis Error</h3>
              <p>{advancedResults.message}</p>
            </div>
          )}
        </div>
      )}


      {/* RAG Query Tab */}
      {activeTab === 'rag' && (
        <div className="tab-content active">
          <div className="card">
            <div className="card-header">
              <i className="fas fa-robot"></i>
              <h2>RAG Query Interface</h2>
            </div>
            <p className="card-description">
              Use natural language to search and retrieve relevant regulatory content. Powered by semantic embeddings and AI.
            </p>

            <div className="form-group">
              <label><i className="fas fa-keyboard"></i> Enter Your Query</label>
              <textarea
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                placeholder="Example: What are the regulations about consumer protection and privacy?"
              />
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label><i className="fas fa-filter"></i> Search Level</label>
                <select value={ragLevel} onChange={(e) => setRagLevel(e.target.value)}>
                  <option value="all">All Levels</option>
                  <option value="chapter">Chapter Only</option>
                  <option value="subchapter">Subchapter Only</option>
                  <option value="section">Section Only</option>
                </select>
              </div>
              <div className="form-group">
                <label><i className="fas fa-list-ol"></i> Top K Results</label>
                <input
                  type="number"
                  value={ragTopK}
                  onChange={(e) => setRagTopK(e.target.value)}
                  min="1"
                  max="50"
                />
              </div>
            </div>

            <button className="btn btn-primary" onClick={runRAGQuery} disabled={ragLoading}>
              <i className="fas fa-search"></i> Search
            </button>
          </div>

          {ragLoading && (
            <div className="loading">
              <div className="spinner"></div>
              <p className="loading-text">Searching...</p>
            </div>
          )}

          {ragResults && (
            <div className="result-box">
              <h3>Search Results</h3>
              {ragResults.results && ragResults.results.length > 0 ? (
                <div className="results-list">
                  {ragResults.results.map((result, i) => (
                    <div key={i} className="result-item">
                      <h4>{result.name || result.section_number}</h4>
                      <p><strong>Similarity:</strong> {(result.similarity_score * 100).toFixed(1)}%</p>
                      <p>{result.subject || result.text?.substring(0, 200)}...</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No results found</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Comparison Modal */}
      {comparisonModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px',
          overflow: 'auto'
        }}
        onClick={closeComparisonModal}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            maxWidth: '1400px',
            width: '100%',
            maxHeight: '90vh',
            overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
          }}
          onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div style={{
              padding: '20px 30px',
              borderBottom: '2px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              position: 'sticky',
              top: 0,
              background: 'white',
              zIndex: 1
            }}>
              <div>
                <h2 style={{ margin: 0, fontSize: '24px', color: '#1f2937' }}>
                  <i className="fas fa-balance-scale"></i> Regulation Text Comparison
                </h2>
                <div style={{ marginTop: '8px', fontSize: '14px', color: '#6b7280' }}>
                  <span style={{
                    padding: '4px 12px',
                    background: comparisonModal.category === 'redundancy' ? '#fef2f2' :
                               comparisonModal.category === 'parity' ? '#fef3c7' : '#eff6ff',
                    color: comparisonModal.category === 'redundancy' ? '#dc2626' :
                           comparisonModal.category === 'parity' ? '#f59e0b' : '#3b82f6',
                    borderRadius: '6px',
                    fontWeight: 'bold',
                    textTransform: 'uppercase',
                    fontSize: '12px'
                  }}>
                    {comparisonModal.category}
                  </span>
                  <span style={{ marginLeft: '10px' }}>
                    Similarity: <strong>{(comparisonModal.similarity_score * 100).toFixed(1)}%</strong>
                  </span>
                </div>
              </div>
              <button onClick={closeComparisonModal} style={{
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                <i className="fas fa-times"></i> Close
              </button>
            </div>

            {/* Modal Body - Side by Side Comparison */}
            <div style={{
              padding: '30px',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '30px'
            }}>
              {/* Regulation A */}
              <div style={{
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                padding: '20px',
                background: '#f9fafb'
              }}>
                <h3 style={{
                  margin: '0 0 15px 0',
                  fontSize: '18px',
                  color: '#dc2626',
                  fontWeight: 'bold',
                  borderBottom: '2px solid #dc2626',
                  paddingBottom: '10px'
                }}>
                  <i className="fas fa-file-alt"></i> Regulation A
                </h3>
                <div style={{ marginBottom: '15px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    <strong>Section:</strong> {comparisonModal.item1.section_number}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    <strong>Subject:</strong> {comparisonModal.item1.subject}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    <strong>Citation:</strong> {comparisonModal.item1.citation}
                  </div>
                </div>
                <div style={{
                  background: 'white',
                  padding: '15px',
                  borderRadius: '6px',
                  fontSize: '14px',
                  lineHeight: '1.8',
                  color: '#1f2937',
                  maxHeight: '600px',
                  overflow: 'auto'
                }}>
                  {comparisonModal.item1.text ? (
                    <div dangerouslySetInnerHTML={{
                      __html: highlightSimilarText(comparisonModal.item1.text, comparisonModal.item2.text).text1
                    }} />
                  ) : (
                    <div style={{ color: '#ef4444', padding: '20px', textAlign: 'center', background: '#fef2f2', borderRadius: '6px' }}>
                      <i className="fas fa-exclamation-triangle"></i>
                      <p><strong>No text available for this section</strong></p>
                      <p style={{ fontSize: '12px', marginTop: '10px' }}>
                        <strong>Section:</strong> {comparisonModal.item1.section_number}<br />
                        <strong>Subject:</strong> {comparisonModal.item1.subject || 'N/A'}<br />
                        <strong>Citation:</strong> {comparisonModal.item1.citation || 'N/A'}<br /><br />
                        <em>This section's text was not extracted during the pipeline parsing.
                        The XML file may not contain text for this section, or it may be a header/placeholder section.</em>
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Regulation B */}
              <div style={{
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                padding: '20px',
                background: '#f9fafb'
              }}>
                <h3 style={{
                  margin: '0 0 15px 0',
                  fontSize: '18px',
                  color: '#3b82f6',
                  fontWeight: 'bold',
                  borderBottom: '2px solid #3b82f6',
                  paddingBottom: '10px'
                }}>
                  <i className="fas fa-file-alt"></i> Regulation B
                </h3>
                <div style={{ marginBottom: '15px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    <strong>Section:</strong> {comparisonModal.item2.section_number}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    <strong>Subject:</strong> {comparisonModal.item2.subject}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>
                    <strong>Citation:</strong> {comparisonModal.item2.citation}
                  </div>
                </div>
                <div style={{
                  background: 'white',
                  padding: '15px',
                  borderRadius: '6px',
                  fontSize: '14px',
                  lineHeight: '1.8',
                  color: '#1f2937',
                  maxHeight: '600px',
                  overflow: 'auto'
                }}>
                  {comparisonModal.item2.text ? (
                    <div dangerouslySetInnerHTML={{
                      __html: highlightSimilarText(comparisonModal.item1.text, comparisonModal.item2.text).text2
                    }} />
                  ) : (
                    <div style={{ color: '#ef4444', padding: '20px', textAlign: 'center', background: '#fef2f2', borderRadius: '6px' }}>
                      <i className="fas fa-exclamation-triangle"></i>
                      <p><strong>No text available for this section</strong></p>
                      <p style={{ fontSize: '12px', marginTop: '10px' }}>
                        <strong>Section:</strong> {comparisonModal.item2.section_number}<br />
                        <strong>Subject:</strong> {comparisonModal.item2.subject || 'N/A'}<br />
                        <strong>Citation:</strong> {comparisonModal.item2.citation || 'N/A'}<br /><br />
                        <em>This section's text was not extracted during the pipeline parsing.
                        The XML file may not contain text for this section, or it may be a header/placeholder section.</em>
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Legend */}
            <div style={{
              padding: '20px 30px',
              borderTop: '2px solid #e5e7eb',
              background: '#f9fafb'
            }}>
              <div style={{ fontSize: '13px', color: '#6b7280' }}>
                <strong><i className="fas fa-info-circle"></i> Legend:</strong>
                {' '}
                <mark style={{ background: '#fef08a', padding: '2px 6px', borderRadius: '3px', marginLeft: '10px' }}>
                  Highlighted text
                </mark>
                {' '}= Common words/phrases between both regulations (words longer than 3 characters)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading Comparison Modal */}
      {loadingComparison && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '12px',
            textAlign: 'center'
          }}>
            <div className="spinner" style={{ margin: '0 auto 15px' }}></div>
            <p style={{ margin: 0, color: '#6b7280' }}>Loading full text comparison...</p>
          </div>
        </div>
      )}
        </div>
      </div>
    </div>
  );
};

export default CFRDashboard;
