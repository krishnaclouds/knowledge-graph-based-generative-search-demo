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

  // Function to search the knowledge graph using RAG
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
      
      const res = await axios.post(`${API_BASE_URL}/search`, {
        query: searchQuery.trim(),
        max_results: 5
      }, { timeout: 30000 });
      
      setSearchResults(res.data);
      
      if (res.data.results.length === 0) {
        setError('No relevant information found for your query. Try rephrasing or using different keywords.');
      }
    } catch (err) {
      let errorMessage = 'Failed to search knowledge graph';
      
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
        <h2>Search Knowledge Graph</h2>
        <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Ask a question about the knowledge graph..."
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
          💡 <strong>Search Tips:</strong> Try queries like "What companies are in tech?", "Who works at Google?", or "What topics are discussed?"
        </div>
        
        {/* Search Results */}
        {searchResults && (
          <div style={{ marginTop: 20 }}>
            <h3>Answer:</h3>
            <div style={{ 
              padding: 15, 
              backgroundColor: '#f5f5f5', 
              borderRadius: 5, 
              marginBottom: 15,
              fontSize: 16,
              lineHeight: 1.5
            }}>
              {searchResults.answer}
            </div>
            
            <h4>Related Nodes (Relevance Score):</h4>
            <div style={{ maxHeight: 200, overflowY: 'auto' }}>
              {searchResults.results.map((result, index) => (
                <div key={index} style={{ 
                  padding: 10, 
                  margin: '5px 0', 
                  border: '1px solid #ccc',
                  borderRadius: 5,
                  backgroundColor: '#fafafa'
                }}>
                  <strong>{result.node.text}</strong>
                  <span style={{ color: '#666', fontSize: 14, marginLeft: 10 }}>
                    (Score: {result.similarity.toFixed(3)})
                  </span>
                </div>
              ))}
            </div>
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
