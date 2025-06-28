import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { Network } from 'vis-network/standalone';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const networkRef = useRef(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchMode, setSearchMode] = useState('hybrid'); // 'hybrid', 'knowledge-graph', 'documents'
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [retryCount, setRetryCount] = useState(0);

  // Function to check backend connection
  const checkConnection = async () => {
    try {
      await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
      setConnectionStatus('connected');
      setRetryCount(0);
      return true;
    } catch (err) {
      setConnectionStatus('disconnected');
      console.error('Backend connection failed:', err);
      return false;
    }
  };

  // Function to fetch graph data from backend
  const fetchGraph = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const isConnected = await checkConnection();
      if (!isConnected) {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8000.');
      }
      
      const res = await axios.get(`${API_BASE_URL}/graph`, { timeout: 10000 });
      setGraphData(res.data);
      
      if (res.data.nodes.length === 0) {
        setError('No data found in the knowledge graph. Please ensure sample data is loaded.');
      }
    } catch (err) {
      let errorMessage = 'Failed to fetch graph data';
      
      if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to backend server. Please ensure the backend is running on port 8000.';
      } else if (err.response?.status === 500) {
        errorMessage = `Server error: ${err.response.data?.detail || 'Internal server error'}`;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Function to search using different modes
  const searchGraph = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    setSearchLoading(true);
    setError(null);
    setSearchResults(null);
    
    try {
      const isConnected = await checkConnection();
      if (!isConnected) {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8000.');
      }
      
      let endpoint = '/search'; // default to knowledge graph search
      if (searchMode === 'hybrid') {
        endpoint = '/hybrid-search';
      } else if (searchMode === 'documents') {
        endpoint = '/documents/search';
      }
      
      const res = await axios.post(`${API_BASE_URL}${endpoint}`, {
        query: searchQuery.trim(),
        max_results: 8
      }, { timeout: 30000 });
      
      setSearchResults({
        ...res.data,
        searchMode: searchMode
      });
      
      if ((res.data.results && res.data.results.length === 0) || 
          (res.data.documents && res.data.documents.length === 0)) {
        setError('No relevant information found for your query. Try rephrasing or using different keywords.');
      }
    } catch (err) {
      let errorMessage = `Failed to search ${searchMode === 'hybrid' ? 'documents and knowledge graph' : searchMode === 'documents' ? 'documents' : 'knowledge graph'}`;
      
      if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to backend server. Please ensure the backend is running on port 8000.';
      } else if (err.response?.status === 422) {
        errorMessage = 'Invalid search query. Please check your input.';
      } else if (err.response?.status === 500) {
        errorMessage = `Search failed: ${err.response.data?.detail || 'Internal server error'}`;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setSearchLoading(false);
    }
  };
  
  // Retry connection
  const retryConnection = async () => {
    setRetryCount(prev => prev + 1);
    await checkConnection();
  };

  // Check connection on component mount
  useEffect(() => {
    checkConnection();
  }, []);
  
  // Render the graph when data changes
  useEffect(() => {
    if (networkRef.current && graphData.nodes.length > 0) {
      const data = {
        nodes: graphData.nodes,
        edges: graphData.edges,
      };
      const options = {
        nodes: { 
          shape: 'dot', 
          size: 20, 
          font: { size: 16 },
          borderWidth: 2,
          shadow: true
        },
        edges: { 
          arrows: 'to', 
          font: { align: 'middle' },
          shadow: true,
          smooth: { type: 'dynamic' }
        },
        physics: { 
          stabilization: true,
          barnesHut: { gravitationalConstant: -2000 }
        },
        interaction: {
          hover: true,
          selectConnectedEdges: false
        }
      };
      new Network(networkRef.current, data, options);
    }
  }, [graphData]);

  return (
    <div className="App">
      <h1>Knowledge Graph RAG Search Demo</h1>
      
      {/* Connection Status */}
      <div style={{ 
        marginBottom: 20, 
        padding: 10, 
        backgroundColor: connectionStatus === 'connected' ? '#d4edda' : '#f8d7da',
        border: `1px solid ${connectionStatus === 'connected' ? '#c3e6cb' : '#f5c6cb'}`,
        borderRadius: 5,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <span style={{ 
          color: connectionStatus === 'connected' ? '#155724' : '#721c24',
          fontWeight: 'bold'
        }}>
          Backend Status: {connectionStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}
        </span>
        {connectionStatus === 'disconnected' && (
          <button 
            onClick={retryConnection} 
            style={{ 
              padding: '5px 10px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: 3,
              cursor: 'pointer'
            }}
          >
            Retry ({retryCount})
          </button>
        )}
      </div>
      
      {/* Graph Controls */}
      <div style={{ marginBottom: 20 }}>
        <button 
          onClick={fetchGraph} 
          disabled={loading || connectionStatus === 'disconnected'} 
          style={{ 
            marginRight: 10,
            padding: '10px 20px',
            fontSize: 16,
            backgroundColor: loading ? '#6c757d' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: 5,
            cursor: loading || connectionStatus === 'disconnected' ? 'not-allowed' : 'pointer',
            opacity: loading || connectionStatus === 'disconnected' ? 0.6 : 1
          }}
        >
          {loading ? '🔄 Loading...' : '📊 Load Knowledge Graph'}
        </button>
        {graphData.nodes.length > 0 && (
          <span style={{ color: '#28a745', fontWeight: 'bold' }}>
            ✅ Graph loaded: {graphData.nodes.length} nodes, {graphData.edges.length} edges
          </span>
        )}
      </div>
      
      {/* Search Interface */}
      <div style={{ marginBottom: 20, padding: 20, border: '1px solid #ddd', borderRadius: 8 }}>
        <h2>🔍 AI-Powered Search</h2>
        
        {/* Search Mode Selector */}
        <div style={{ marginBottom: 15 }}>
          <label style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 8, display: 'block' }}>
            Search Mode:
          </label>
          <div style={{ display: 'flex', gap: 15 }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="hybrid"
                checked={searchMode === 'hybrid'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'hybrid' ? '#007bff' : '#666' }}>
                🔗 Hybrid Search (Documents + Knowledge Graph)
              </span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="documents"
                checked={searchMode === 'documents'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'documents' ? '#007bff' : '#666' }}>
                📄 Documents Only
              </span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="knowledge-graph"
                checked={searchMode === 'knowledge-graph'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'knowledge-graph' ? '#007bff' : '#666' }}>
                🕸️ Knowledge Graph Only
              </span>
            </label>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={
              searchMode === 'hybrid' ? "Ask about investments, company strategies, or business trends..." :
              searchMode === 'documents' ? "Search investment reports and business documents..." :
              "Ask about companies, people, and their relationships..."
            }
            style={{ 
              flex: 1, 
              padding: 12, 
              fontSize: 16, 
              border: '2px solid #ddd',
              borderRadius: 5,
              outline: 'none'
            }}
            onKeyDown={(e) => e.key === 'Enter' && !searchLoading && connectionStatus === 'connected' && searchGraph()}
            onFocus={(e) => e.target.style.borderColor = '#007bff'}
            onBlur={(e) => e.target.style.borderColor = '#ddd'}
          />
          <button 
            onClick={searchGraph} 
            disabled={searchLoading || !searchQuery.trim() || connectionStatus === 'disconnected'}
            style={{ 
              padding: '12px 24px', 
              fontSize: 16,
              backgroundColor: searchLoading ? '#6c757d' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: 5,
              cursor: searchLoading || !searchQuery.trim() || connectionStatus === 'disconnected' ? 'not-allowed' : 'pointer',
              opacity: searchLoading || !searchQuery.trim() || connectionStatus === 'disconnected' ? 0.6 : 1,
              minWidth: 120
            }}
          >
            {searchLoading ? '🔍 Searching...' : '🔍 Search'}
          </button>
        </div>
        
        {/* Search Tips */}
        <div style={{ 
          fontSize: 14, 
          color: '#666', 
          marginBottom: 15,
          padding: 10,
          backgroundColor: '#f8f9fa',
          borderRadius: 5,
          border: '1px solid #e9ecef'
        }}>
          💡 <strong>Try these examples:</strong>
          {searchMode === 'hybrid' && (
            <span> "Apple's investments for 2025", "Tesla's energy storage plans", "Meta's metaverse strategy"</span>
          )}
          {searchMode === 'documents' && (
            <span> "Cloud infrastructure investment", "AI research funding", "Renewable energy projects"</span>
          )}
          {searchMode === 'knowledge-graph' && (
            <span> "Who works at Google?", "What companies are in tech?", "Show me AI researchers"</span>
          )}
        </div>
        
        {/* Search Results */}
        {searchResults && (
          <div style={{ marginTop: 20 }}>
            {/* Results Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: 15
            }}>
              <h3 style={{ color: '#2c3e50', margin: 0 }}>
                {searchResults.searchMode === 'hybrid' && '🔗 Hybrid Search Results'}
                {searchResults.searchMode === 'documents' && '📄 Document Search Results'}
                {searchResults.searchMode === 'knowledge-graph' && '🕸️ Knowledge Graph Results'}
              </h3>
              <div style={{ 
                fontSize: 12,
                color: '#6c757d',
                backgroundColor: '#f8f9fa',
                padding: '4px 8px',
                borderRadius: 4,
                border: '1px solid #e9ecef'
              }}>
                {searchResults.documents ? `${searchResults.documents.length} documents` : 
                 searchResults.results ? `${searchResults.results.length} results` : '0 results'} found
              </div>
            </div>

            {/* Generated Answer (for hybrid and knowledge graph search) */}
            {searchResults.answer && (
              <>
                <h4 style={{ color: '#2c3e50', borderBottom: '2px solid #3498db', paddingBottom: 8 }}>
                  📝 AI-Generated Answer
                </h4>
                <div style={{ 
                  padding: 20, 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: 8, 
                  marginBottom: 20,
                  fontSize: 16,
                  lineHeight: 1.6,
                  border: '1px solid #e9ecef',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  {searchResults.answer}
                </div>
              </>
            )}
            
            {/* Citations */}
            {searchResults.citations && searchResults.citations.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                <h4 style={{ color: '#2c3e50', marginBottom: 10 }}>📚 Sources & Citations</h4>
                <div style={{ 
                  backgroundColor: '#fff3cd', 
                  border: '1px solid #ffeaa7',
                  borderRadius: 6,
                  padding: 15
                }}>
                  {searchResults.citations.map((citation, index) => (
                    <div key={index} style={{ 
                      marginBottom: 8,
                      paddingBottom: 8,
                      borderBottom: index < searchResults.citations.length - 1 ? '1px solid #ffeaa7' : 'none'
                    }}>
                      <strong>[{index + 1}]</strong> {citation.title || citation.source}
                      {citation.authors && (
                        <div style={{ fontSize: 14, color: '#6c757d', marginTop: 2 }}>
                          Authors: {Array.isArray(citation.authors) ? citation.authors.join(', ') : citation.authors}
                        </div>
                      )}
                      {(citation.year || citation.venue) && (
                        <div style={{ fontSize: 14, color: '#6c757d', marginTop: 2 }}>
                          {citation.venue && `${citation.venue}`}{citation.year && ` (${citation.year})`}
                        </div>
                      )}
                      {citation.doi && citation.doi !== 'N/A' && (
                        <div style={{ fontSize: 12, color: '#007bff', marginTop: 2 }}>
                          DOI: {citation.doi}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Document Results (for hybrid and document-only search) */}
            {searchResults.documents && searchResults.documents.length > 0 && (
              <>
                <h4 style={{ color: '#2c3e50', marginBottom: 10 }}>📄 Relevant Documents</h4>
                <div style={{ maxHeight: 400, overflowY: 'auto', border: '1px solid #dee2e6', borderRadius: 6, marginBottom: 20 }}>
                  {searchResults.documents.map((doc, index) => (
                    <div key={index} style={{ 
                      padding: 15, 
                      margin: 0,
                      borderBottom: index < searchResults.documents.length - 1 ? '1px solid #e9ecef' : 'none',
                      backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa'
                    }}>
                      <div style={{ 
                        fontWeight: 'bold', 
                        marginBottom: 8,
                        color: '#2c3e50',
                        fontSize: 16
                      }}>
                        {doc.title}
                      </div>
                      
                      {/* Document metadata */}
                      <div style={{ marginBottom: 8 }}>
                        <span style={{
                          display: 'inline-block',
                          backgroundColor: '#6f42c1',
                          color: 'white',
                          padding: '2px 8px',
                          borderRadius: 12,
                          fontSize: 12,
                          marginRight: 8,
                          fontWeight: 'bold'
                        }}>
                          Document
                        </span>
                        {doc.metadata?.type && (
                          <span style={{
                            display: 'inline-block',
                            backgroundColor: '#17a2b8',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: 12,
                            fontSize: 12,
                            marginRight: 8
                          }}>
                            {doc.metadata.type.replace('_', ' ').toUpperCase()}
                          </span>
                        )}
                        {doc.metadata?.date && (
                          <span style={{ fontSize: 12, color: '#6c757d' }}>
                            📅 {doc.metadata.date}
                          </span>
                        )}
                      </div>
                      
                      {/* Document content preview */}
                      {doc.content && (
                        <div style={{ 
                          fontSize: 14, 
                          color: '#495057', 
                          marginBottom: 8,
                          maxHeight: '100px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>
                          {doc.content.length > 300 ? 
                            `${doc.content.substring(0, 300)}...` : 
                            doc.content}
                        </div>
                      )}
                      
                      {/* Additional metadata */}
                      {doc.metadata?.companies && (
                        <div style={{ fontSize: 12, color: '#6c757d', marginBottom: 3 }}>
                          🏢 Companies: {doc.metadata.companies}
                        </div>
                      )}
                      {doc.metadata?.amount && (
                        <div style={{ fontSize: 12, color: '#28a745', fontWeight: 'bold' }}>
                          💰 Investment: {doc.metadata.amount}
                        </div>
                      )}
                      
                      {/* Similarity score */}
                      <div style={{ 
                        textAlign: 'right',
                        marginTop: 8
                      }}>
                        <span style={{ 
                          fontSize: 12,
                          fontWeight: 'bold',
                          color: doc.similarity > 0.7 ? '#28a745' : 
                                 doc.similarity > 0.5 ? '#ffc107' : '#dc3545',
                          backgroundColor: '#f8f9fa',
                          padding: '2px 6px',
                          borderRadius: 4,
                          border: '1px solid #e9ecef'
                        }}>
                          {(doc.similarity * 100).toFixed(1)}% Match
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
            
            {/* Document-only search results */}
            {searchResults.searchMode === 'documents' && searchResults.results && (
              <>
                <h4 style={{ color: '#2c3e50', marginBottom: 10 }}>📄 Document Search Results</h4>
                <div style={{ maxHeight: 400, overflowY: 'auto', border: '1px solid #dee2e6', borderRadius: 6, marginBottom: 20 }}>
                  {searchResults.results.map((result, index) => (
                    <div key={index} style={{ 
                      padding: 15, 
                      margin: 0,
                      borderBottom: index < searchResults.results.length - 1 ? '1px solid #e9ecef' : 'none',
                      backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa'
                    }}>
                      <div style={{ 
                        fontWeight: 'bold', 
                        marginBottom: 8,
                        color: '#2c3e50',
                        fontSize: 16
                      }}>
                        {result.metadata?.title || 'Document'}
                      </div>
                      
                      <div style={{ 
                        fontSize: 14, 
                        color: '#495057', 
                        marginBottom: 8,
                        maxHeight: '100px',
                        overflow: 'hidden'
                      }}>
                        {result.content?.length > 300 ? 
                          `${result.content.substring(0, 300)}...` : 
                          result.content}
                      </div>
                      
                      <div style={{ 
                        textAlign: 'right'
                      }}>
                        <span style={{ 
                          fontSize: 12,
                          fontWeight: 'bold',
                          color: result.similarity > 0.7 ? '#28a745' : 
                                 result.similarity > 0.5 ? '#ffc107' : '#dc3545'
                        }}>
                          {((1 - result.distance) * 100).toFixed(1)}% Match
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
            
            {/* Knowledge Graph Results */}
            {searchResults.results && searchResults.searchMode !== 'documents' && (
              <>
                <h4 style={{ color: '#2c3e50', marginBottom: 10 }}>🔍 Related Knowledge Graph Nodes</h4>
                <div style={{ maxHeight: 300, overflowY: 'auto', border: '1px solid #dee2e6', borderRadius: 6 }}>
                  {searchResults.results.map((result, index) => (
                <div key={index} style={{ 
                  padding: 15, 
                  margin: 0,
                  borderBottom: index < searchResults.results.length - 1 ? '1px solid #e9ecef' : 'none',
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start'
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontWeight: 'bold', 
                      marginBottom: 5,
                      color: '#2c3e50'
                    }}>
                      {result.node.name || result.node.title || result.node.text}
                    </div>
                    
                    {/* Node type badges */}
                    <div style={{ marginBottom: 8 }}>
                      {result.node.labels.map((label, labelIndex) => (
                        <span key={labelIndex} style={{
                          display: 'inline-block',
                          backgroundColor: 
                            label === 'Company' ? '#007bff' :
                            label === 'Person' ? '#28a745' :
                            label === 'Topic' ? '#ffc107' :
                            label === 'Document' ? '#6f42c1' : '#6c757d',
                          color: 'white',
                          padding: '2px 8px',
                          borderRadius: 12,
                          fontSize: 12,
                          marginRight: 5,
                          fontWeight: 'bold'
                        }}>
                          {label}
                        </span>
                      ))}
                    </div>
                    
                    {/* Additional node information */}
                    {result.node.industry && (
                      <div style={{ fontSize: 14, color: '#6c757d', marginBottom: 3 }}>
                        Industry: {result.node.industry}
                      </div>
                    )}
                    {result.node.role && (
                      <div style={{ fontSize: 14, color: '#6c757d', marginBottom: 3 }}>
                        Role: {result.node.role}
                      </div>
                    )}
                    {result.node.authors && (
                      <div style={{ fontSize: 14, color: '#6c757d', marginBottom: 3 }}>
                        Authors: {Array.isArray(result.node.authors) ? 
                          result.node.authors.slice(0, 3).join(', ') + (result.node.authors.length > 3 ? '...' : '') : 
                          result.node.authors}
                      </div>
                    )}
                    {result.node.year && (
                      <div style={{ fontSize: 14, color: '#6c757d', marginBottom: 3 }}>
                        Year: {result.node.year}
                      </div>
                    )}
                    {result.node.description && (
                      <div style={{ 
                        fontSize: 14, 
                        color: '#495057', 
                        marginTop: 8,
                        fontStyle: 'italic',
                        maxHeight: '60px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }}>
                        {result.node.description.length > 150 ? 
                          `${result.node.description.substring(0, 150)}...` : 
                          result.node.description}
                      </div>
                    )}
                  </div>
                  
                  <div style={{ 
                    marginLeft: 15,
                    textAlign: 'center',
                    minWidth: '80px'
                  }}>
                    <div style={{ 
                      fontSize: 18,
                      fontWeight: 'bold',
                      color: result.similarity > 0.7 ? '#28a745' : 
                             result.similarity > 0.5 ? '#ffc107' : '#dc3545'
                    }}>
                      {(result.similarity * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: 12, color: '#6c757d' }}>
                      Relevance
                    </div>
                  </div>
                </div>
              ))}
            </div>
              </>
            )}
          </div>
        )}
      </div>
      
      {error && (
        <div style={{ 
          color: '#721c24',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          padding: 15,
          borderRadius: 5,
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 10
        }}>
          <span style={{ fontSize: 18 }}>⚠️</span>
          <div>
            <strong>Error:</strong> {error}
            {connectionStatus === 'disconnected' && (
              <div style={{ marginTop: 8, fontSize: 14 }}>
                <strong>Troubleshooting:</strong>
                <ul style={{ margin: '5px 0', paddingLeft: 20 }}>
                  <li>Ensure the backend server is running: <code>cd backend && python main.py</code></li>
                  <li>Check that Neo4j is running and accessible</li>
                  <li>Verify your .env file has the correct configuration</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Graph Visualization */}
      <div>
        <h2>📈 Graph Visualization</h2>
        {graphData.nodes.length === 0 ? (
          <div style={{
            height: '500px',
            border: '2px dashed #ccc',
            borderRadius: 10,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f8f9fa',
            color: '#666',
            fontSize: 18
          }}>
            📊 Load the knowledge graph to see the visualization
          </div>
        ) : (
          <div 
            ref={networkRef} 
            style={{ 
              height: '500px', 
              border: '2px solid #007bff',
              borderRadius: 10,
              backgroundColor: '#f8f9fa'
            }} 
          />
        )}
      </div>
    </div>
  );
}

export default App;
