import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/CFRDashboard.css';

const CFRDashboard_85063ac = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('pipeline');
  const [loading, setLoading] = useState({});
  const [stats, setStats] = useState({
    chapters: 0,
    sections: 0,
    embeddings: 0
  });

  // Pipeline state
  const [pipelineUrls, setPipelineUrls] = useState('https://www.govinfo.gov/bulkdata/CFR/2025/title-16/');
  const [pipelineResults, setPipelineResults] = useState('');

  // Analysis state
  const [analysisLevel, setAnalysisLevel] = useState('chapter');
  const [analysisResults, setAnalysisResults] = useState(null);

  // Clustering state
  const [clusterLevel, setClusterLevel] = useState('section');
  const [clusterN, setClusterN] = useState('');
  const [clusteringResults, setClusteringResults] = useState(null);

  // RAG state
  const [ragQuery, setRagQuery] = useState('');
  const [ragLevel, setRagLevel] = useState('all');
  const [ragTopK, setRagTopK] = useState(10);
  const [ragResults, setRagResults] = useState(null);

  // Similarity state
  const [simName, setSimName] = useState('');
  const [simType, setSimType] = useState('chapter');
  const [simTopK, setSimTopK] = useState(10);
  const [similarityResults, setSimilarityResults] = useState(null);

  // Visualizations state
  const [visualizations, setVisualizations] = useState(null);

  useEffect(() => {
    getStats();
  }, []);

  const API_BASE = 'http://localhost:8000';

  const getStats = async () => {
    try {
      setLoading(prev => ({ ...prev, pipeline: true }));
      const response = await fetch(`${API_BASE}/api/pipeline/stats`);
      const data = await response.json();
      setStats({
        chapters: data.chapters || 0,
        sections: data.sections || 0,
        embeddings: data.section_embeddings || 0
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(prev => ({ ...prev, pipeline: false }));
    }
  };

  const runPipeline = async () => {
    if (!pipelineUrls.trim()) {
      setPipelineResults('<div class="cfr-alert cfr-alert-warning">Please enter at least one CFR URL</div>');
      return;
    }

    const urls = pipelineUrls.split('\n').map(url => url.trim()).filter(url => url.length > 0);
    
    setLoading(prev => ({ ...prev, pipeline: true }));
    setPipelineResults('');

    try {
      const response = await fetch(`${API_BASE}/api/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls })
      });
      const data = await response.json();
      
      setPipelineResults(`
        <div class="cfr-alert cfr-alert-success">
          <strong>Pipeline Started!</strong><br>
          Processing ${data.num_urls} URL(s) in the background.
        </div>
      `);

      setTimeout(() => getStats(), 3000);
    } catch (error) {
      setPipelineResults(`
        <div class="cfr-alert cfr-alert-danger">
          <strong>Error:</strong> ${error.message}
        </div>
      `);
    } finally {
      setLoading(prev => ({ ...prev, pipeline: false }));
    }
  };

  const runAnalysis = async () => {
    setLoading(prev => ({ ...prev, analysis: true }));
    setAnalysisResults(null);

    try {
      const response = await fetch(`${API_BASE}/api/analysis/similarity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level: analysisLevel })
      });
      const data = await response.json();
      setAnalysisResults(data);
    } catch (error) {
      setAnalysisResults({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, analysis: false }));
    }
  };

  const performClustering = async () => {
    setLoading(prev => ({ ...prev, clustering: true }));
    setClusteringResults(null);

    try {
      const requestBody = { level: clusterLevel };
      if (clusterN) {
        requestBody.n_clusters = parseInt(clusterN);
      }
      
      const response = await fetch(`${API_BASE}/api/clustering/cluster`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      const data = await response.json();
      setClusteringResults(data);
    } catch (error) {
      setClusteringResults({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, clustering: false }));
    }
  };

  const generateVisualizations = async () => {
    setLoading(prev => ({ ...prev, clustering: true }));

    try {
      const requestBody = { level: clusterLevel };
      if (clusterN) {
        requestBody.n_clusters = parseInt(clusterN);
      }
      
      const response = await fetch(`${API_BASE}/api/visualization/clusters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      const data = await response.json();
      setVisualizations(data.visualizations);
      setActiveTab('visualizations');
    } catch (error) {
      console.error('Error generating visualizations:', error);
    } finally {
      setLoading(prev => ({ ...prev, clustering: false }));
    }
  };

  const queryRAG = async () => {
    if (!ragQuery.trim()) {
      setRagResults({ error: 'Please enter a query to search.' });
      return;
    }
    
    setLoading(prev => ({ ...prev, rag: true }));
    setRagResults(null);

    try {
      const response = await fetch(`${API_BASE}/api/rag/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: ragQuery, level: ragLevel, top_k: ragTopK })
      });
      const data = await response.json();
      setRagResults(data);
    } catch (error) {
      setRagResults({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, rag: false }));
    }
  };

  const findSimilar = async () => {
    if (!simName.trim()) {
      setSimilarityResults({ error: 'Please enter an item name to search.' });
      return;
    }
    
    setLoading(prev => ({ ...prev, similarity: true }));
    setSimilarityResults(null);

    try {
      const response = await fetch(`${API_BASE}/api/rag/similar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: simName, search_type: simType, top_k: simTopK })
      });
      const data = await response.json();
      setSimilarityResults(data);
    } catch (error) {
      setSimilarityResults({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, similarity: false }));
    }
  };

  const resetDatabase = async () => {
    if (!window.confirm('⚠️ WARNING: This will delete ALL data. Are you sure?')) {
      return;
    }

    setLoading(prev => ({ ...prev, pipeline: true }));

    try {
      await fetch(`${API_BASE}/api/pipeline/reset`, { method: 'POST' });
      setPipelineResults('<div class="cfr-alert cfr-alert-success">Database reset complete!</div>');
      setStats({ chapters: 0, sections: 0, embeddings: 0 });
    } catch (error) {
      setPipelineResults(`<div class="cfr-alert cfr-alert-danger">Error: ${error.message}</div>`);
    } finally {
      setLoading(prev => ({ ...prev, pipeline: false }));
    }
  };

  const getSimilarityBadgeClass = (score) => {
    if (score >= 0.85) return 'high';
    if (score >= 0.75) return 'medium';
    return '';
  };

  return (
    <div className="cfr-app-container">
      {/* Header */}
      <div className="cfr-header">
        <div className="cfr-header-content">
          <h1>
            <i className="fas fa-brain"></i>
            CFR Agentic AI
          </h1>
          <p>Intelligent Analysis & Retrieval System for Code of Federal Regulations</p>
          <div className="cfr-header-stats">
            <div className="cfr-stat-item">
              <span className="cfr-stat-value">{stats.chapters}</span>
              <span className="cfr-stat-label">Chapters</span>
            </div>
            <div className="cfr-stat-item">
              <span className="cfr-stat-value">{stats.sections}</span>
              <span className="cfr-stat-label">Sections</span>
            </div>
            <div className="cfr-stat-item">
              <span className="cfr-stat-value">{stats.embeddings}</span>
              <span className="cfr-stat-label">Embeddings</span>
            </div>
          </div>
        </div>
      </div>

      {/* Layout */}
      <div className="cfr-layout">
        {/* Sidebar Navigation */}
        <div className="cfr-nav-tabs">
          <button className={`cfr-nav-tab ${activeTab === 'pipeline' ? 'active' : ''}`} onClick={() => setActiveTab('pipeline')}>
            <i className="fas fa-database"></i>
            <span>Pipeline</span>
          </button>
          <button className={`cfr-nav-tab ${activeTab === 'analysis' ? 'active' : ''}`} onClick={() => setActiveTab('analysis')}>
            <i className="fas fa-chart-line"></i>
            <span>Analysis</span>
          </button>
          <button className={`cfr-nav-tab ${activeTab === 'clustering' ? 'active' : ''}`} onClick={() => setActiveTab('clustering')}>
            <i className="fas fa-project-diagram"></i>
            <span>Clustering</span>
          </button>
          <button className={`cfr-nav-tab ${activeTab === 'rag' ? 'active' : ''}`} onClick={() => setActiveTab('rag')}>
            <i className="fas fa-comments"></i>
            <span>RAG Query</span>
          </button>
          <button className={`cfr-nav-tab ${activeTab === 'similarity' ? 'active' : ''}`} onClick={() => setActiveTab('similarity')}>
            <i className="fas fa-search"></i>
            <span>Search</span>
          </button>
          <button className={`cfr-nav-tab ${activeTab === 'visualizations' ? 'active' : ''}`} onClick={() => setActiveTab('visualizations')}>
            <i className="fas fa-chart-pie"></i>
            <span>Visuals</span>
          </button>
          <div style={{ flex: 1 }}></div>
          <button className="cfr-nav-tab" onClick={logout}>
            <i className="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </button>
        </div>

        {/* Main Content */}
        <div className="cfr-main-content">
          {/* Pipeline Tab */}
          {activeTab === 'pipeline' && (
            <div className="cfr-tab-content active">
              <div className="cfr-card">
                <div className="cfr-card-header">
                  <i className="fas fa-rocket"></i>
                  <h2>Data Pipeline Control</h2>
                </div>
                <p className="cfr-card-description">
                  Enter CFR URLs to crawl, parse XML files, store in database, and generate AI embeddings.
                </p>
                
                <div className="cfr-form-group">
                  <label><i className="fas fa-link"></i> CFR URLs (one per line)</label>
                  <textarea
                    value={pipelineUrls}
                    onChange={(e) => setPipelineUrls(e.target.value)}
                    rows="4"
                    placeholder="https://www.govinfo.gov/bulkdata/CFR/2025/title-16/"
                  />
                </div>
                
                <div className="cfr-btn-group">
                  <button className="cfr-btn cfr-btn-primary" onClick={runPipeline} disabled={loading.pipeline}>
                    <i className="fas fa-play"></i> Run Complete Pipeline
                  </button>
                  <button className="cfr-btn cfr-btn-secondary" onClick={getStats}>
                    <i className="fas fa-chart-bar"></i> Get Statistics
                  </button>
                  <button className="cfr-btn cfr-btn-danger" onClick={resetDatabase}>
                    <i className="fas fa-trash-alt"></i> Reset Database
                  </button>
                </div>
              </div>

              {pipelineResults && (
                <div dangerouslySetInnerHTML={{ __html: pipelineResults }} />
              )}
            </div>
          )}

          {/* Analysis Tab */}
          {activeTab === 'analysis' && (
            <div className="cfr-tab-content active">
              <div className="cfr-card">
                <div className="cfr-card-header">
                  <i className="fas fa-microscope"></i>
                  <h2>Redundancy Analysis</h2>
                </div>
                <p className="cfr-card-description">
                  Analyze semantic similarity, detect overlaps, and check redundancy across different levels.
                </p>

                <div className="cfr-form-group">
                  <label><i className="fas fa-layer-group"></i> Analysis Level</label>
                  <select value={analysisLevel} onChange={(e) => setAnalysisLevel(e.target.value)}>
                    <option value="chapter">Chapter Level</option>
                    <option value="subchapter">Subchapter Level</option>
                    <option value="section">Section Level</option>
                  </select>
                </div>

                <button className="cfr-btn cfr-btn-primary" onClick={runAnalysis} disabled={loading.analysis}>
                  <i className="fas fa-play"></i> Run Analysis
                </button>
              </div>

              {loading.analysis && <div className="cfr-loading"><div className="cfr-spinner"></div></div>}
              {analysisResults && !analysisResults.error && (
                <div className="cfr-results-container">
                  <div className="cfr-results-header">
                    <h3><i className="fas fa-chart-line"></i> Analysis Results</h3>
                    <span className="cfr-results-count">{analysisResults.total_pairs} pairs</span>
                  </div>
                  {analysisResults.results?.slice(0, 10).map((result, idx) => (
                    <div key={idx} className="cfr-result-item">
                      <div className="cfr-result-item-header">
                        <div className="cfr-result-item-title">#{idx + 1}</div>
                        <span className={`cfr-similarity-badge ${getSimilarityBadgeClass(result.similarity_score)}`}>
                          {(result.similarity_score * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="cfr-result-item-content">
                        <strong>Item 1:</strong> {result.item1_name}<br />
                        <strong>Item 2:</strong> {result.item2_name}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {analysisResults?.error && (
                <div className="cfr-alert cfr-alert-danger">Error: {analysisResults.error}</div>
              )}
            </div>
          )}

          {/* Clustering Tab */}
          {activeTab === 'clustering' && (
            <div className="cfr-tab-content active">
              <div className="cfr-card">
                <div className="cfr-card-header">
                  <i className="fas fa-sitemap"></i>
                  <h2>K-Means Clustering</h2>
                </div>
                <p className="cfr-card-description">
                  Automatically group similar content using K-Means clustering.
                </p>

                <div className="cfr-form-grid">
                  <div className="cfr-form-group">
                    <label><i className="fas fa-layer-group"></i> Clustering Level</label>
                    <select value={clusterLevel} onChange={(e) => setClusterLevel(e.target.value)}>
                      <option value="section">Section Level</option>
                      <option value="subchapter">Subchapter Level</option>
                      <option value="chapter">Chapter Level</option>
                    </select>
                  </div>
                  <div className="cfr-form-group">
                    <label><i className="fas fa-hashtag"></i> Number of Clusters</label>
                    <input
                      type="number"
                      value={clusterN}
                      onChange={(e) => setClusterN(e.target.value)}
                      placeholder="Auto"
                      min="2"
                      max="20"
                    />
                  </div>
                </div>

                <div className="cfr-btn-group">
                  <button className="cfr-btn cfr-btn-primary" onClick={performClustering} disabled={loading.clustering}>
                    <i className="fas fa-project-diagram"></i> Perform Clustering
                  </button>
                  <button className="cfr-btn cfr-btn-success" onClick={generateVisualizations} disabled={loading.clustering}>
                    <i className="fas fa-image"></i> Generate Visualizations
                  </button>
                </div>
              </div>

              {loading.clustering && <div className="cfr-loading"><div className="cfr-spinner"></div></div>}
              {clusteringResults && !clusteringResults.error && (
                <div className="cfr-results-container">
                  <div className="cfr-results-header">
                    <h3><i className="fas fa-project-diagram"></i> Clustering Results</h3>
                    <span className="cfr-results-count">{clusteringResults.num_clusters} clusters</span>
                  </div>
                  {clusteringResults.clusters?.map((cluster, idx) => (
                    <div key={idx} className="cfr-result-item">
                      <div className="cfr-result-item-header">
                        <div className="cfr-result-item-title">Cluster {cluster.label}</div>
                        <span className="cfr-similarity-badge">{cluster.size} items</span>
                      </div>
                      <div className="cfr-result-item-content">
                        {cluster.summary && <p><strong>Summary:</strong> {cluster.summary}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {clusteringResults?.error && (
                <div className="cfr-alert cfr-alert-danger">Error: {clusteringResults.error}</div>
              )}
            </div>
          )}

          {/* RAG Query Tab */}
          {activeTab === 'rag' && (
            <div className="cfr-tab-content active">
              <div className="cfr-card">
                <div className="cfr-card-header">
                  <i className="fas fa-robot"></i>
                  <h2>RAG Query Interface</h2>
                </div>
                <p className="cfr-card-description">
                  Use natural language to search and retrieve relevant regulatory content.
                </p>

                <div className="cfr-form-group">
                  <label><i className="fas fa-keyboard"></i> Enter Your Query</label>
                  <textarea
                    value={ragQuery}
                    onChange={(e) => setRagQuery(e.target.value)}
                    placeholder="Example: What are the regulations about consumer protection?"
                  />
                </div>

                <div className="cfr-form-grid">
                  <div className="cfr-form-group">
                    <label><i className="fas fa-filter"></i> Search Level</label>
                    <select value={ragLevel} onChange={(e) => setRagLevel(e.target.value)}>
                      <option value="all">All Levels</option>
                      <option value="chapter">Chapter Only</option>
                      <option value="subchapter">Subchapter Only</option>
                      <option value="section">Section Only</option>
                    </select>
                  </div>
                  <div className="cfr-form-group">
                    <label><i className="fas fa-list-ol"></i> Top K Results</label>
                    <input
                      type="number"
                      value={ragTopK}
                      onChange={(e) => setRagTopK(parseInt(e.target.value))}
                      min="1"
                      max="50"
                    />
                  </div>
                </div>

                <button className="cfr-btn cfr-btn-primary" onClick={queryRAG} disabled={loading.rag}>
                  <i className="fas fa-search"></i> Search Database
                </button>
              </div>

              {loading.rag && <div className="cfr-loading"><div className="cfr-spinner"></div></div>}
              {ragResults && !ragResults.error && (
                <div className="cfr-results-container">
                  <div className="cfr-results-header">
                    <h3><i className="fas fa-search"></i> Query Results</h3>
                    <span className="cfr-results-count">{ragResults.results?.length} results</span>
                  </div>
                  {ragResults.results?.map((result, idx) => (
                    <div key={idx} className="cfr-result-item">
                      <div className="cfr-result-item-header">
                        <div className="cfr-result-item-title">
                          {result.subject || result.section_number || result.name}
                        </div>
                        <span className={`cfr-similarity-badge ${getSimilarityBadgeClass(result.similarity_score)}`}>
                          {(result.similarity_score * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="cfr-result-item-content">
                        {result.section_number && <><strong>Section:</strong> {result.section_number}<br /></>}
                        {result.chapter_name && <><strong>Chapter:</strong> {result.chapter_name}<br /></>}
                        {result.text && <><strong>Preview:</strong> {result.text.substring(0, 200)}...</>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {ragResults?.error && (
                <div className="cfr-alert cfr-alert-danger">Error: {ragResults.error}</div>
              )}
            </div>
          )}

          {/* Similarity Search Tab */}
          {activeTab === 'similarity' && (
            <div className="cfr-tab-content active">
              <div className="cfr-card">
                <div className="cfr-card-header">
                  <i className="fas fa-clone"></i>
                  <h2>Find Similar Items</h2>
                </div>
                <p className="cfr-card-description">
                  Search for a specific item to find the most similar related items.
                </p>

                <div className="cfr-form-group">
                  <label><i className="fas fa-search"></i> Item Name or Keywords</label>
                  <input
                    type="text"
                    value={simName}
                    onChange={(e) => setSimName(e.target.value)}
                    placeholder="Example: Consumer Protection"
                  />
                </div>

                <div className="cfr-form-grid">
                  <div className="cfr-form-group">
                    <label><i className="fas fa-tag"></i> Search Type</label>
                    <select value={simType} onChange={(e) => setSimType(e.target.value)}>
                      <option value="chapter">Chapter</option>
                      <option value="subchapter">Subchapter</option>
                      <option value="section">Section</option>
                    </select>
                  </div>
                  <div className="cfr-form-group">
                    <label><i className="fas fa-list-ol"></i> Top K Results</label>
                    <input
                      type="number"
                      value={simTopK}
                      onChange={(e) => setSimTopK(parseInt(e.target.value))}
                      min="1"
                      max="50"
                    />
                  </div>
                </div>

                <button className="cfr-btn cfr-btn-primary" onClick={findSimilar} disabled={loading.similarity}>
                  <i className="fas fa-search-plus"></i> Find Similar Items
                </button>
              </div>

              {loading.similarity && <div className="cfr-loading"><div className="cfr-spinner"></div></div>}
              {similarityResults && !similarityResults.error && (
                <div className="cfr-results-container">
                  <div className="cfr-results-header">
                    <h3><i className="fas fa-clone"></i> Similar Items</h3>
                    <span className="cfr-results-count">{similarityResults.results?.length} found</span>
                  </div>
                  {similarityResults.results?.map((result, idx) => (
                    <div key={idx} className="cfr-result-item">
                      <div className="cfr-result-item-header">
                        <div className="cfr-result-item-title">
                          {result.name || result.subject || result.section_number}
                        </div>
                        <span className={`cfr-similarity-badge ${getSimilarityBadgeClass(result.similarity_score)}`}>
                          {(result.similarity_score * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="cfr-result-item-content">
                        {result.name && <><strong>Name:</strong> {result.name}<br /></>}
                        {result.chapter_name && <><strong>Chapter:</strong> {result.chapter_name}<br /></>}
                        {result.text && <><strong>Preview:</strong> {result.text.substring(0, 150)}...</>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {similarityResults?.error && (
                <div className="cfr-alert cfr-alert-danger">Error: {similarityResults.error}</div>
              )}
            </div>
          )}

          {/* Visualizations Tab */}
          {activeTab === 'visualizations' && (
            <div className="cfr-tab-content active">
              <div className="cfr-card">
                <div className="cfr-card-header">
                  <i className="fas fa-chart-area"></i>
                  <h2>Cluster Visualizations</h2>
                </div>
                <p className="cfr-card-description">
                  Explore beautiful visualizations of your clustering results.
                </p>
                
                {visualizations ? (
                  <div className="cfr-vis-grid">
                    {visualizations.tsne_2d && (
                      <div className="cfr-vis-card">
                        <img src={visualizations.tsne_2d} alt="t-SNE 2D" className="cfr-vis-card-image" />
                        <div className="cfr-vis-card-body">
                          <div className="cfr-vis-card-title">t-SNE 2D Visualization</div>
                          <a href={visualizations.tsne_2d} target="_blank" rel="noreferrer" className="cfr-vis-card-link">
                            View Full Size <i className="fas fa-external-link-alt"></i>
                          </a>
                        </div>
                      </div>
                    )}
                    {visualizations.pca_2d && (
                      <div className="cfr-vis-card">
                        <img src={visualizations.pca_2d} alt="PCA 2D" className="cfr-vis-card-image" />
                        <div className="cfr-vis-card-body">
                          <div className="cfr-vis-card-title">PCA 2D Visualization</div>
                          <a href={visualizations.pca_2d} target="_blank" rel="noreferrer" className="cfr-vis-card-link">
                            View Full Size <i className="fas fa-external-link-alt"></i>
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="cfr-empty-state">
                    <i className="fas fa-chart-pie"></i>
                    <h3>No Visualizations Yet</h3>
                    <p>Go to the Clustering tab and click "Generate Visualizations"</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CFRDashboard_85063ac;
