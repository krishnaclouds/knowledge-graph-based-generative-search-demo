import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { Network } from 'vis-network/standalone';
import './App.css';

function App() {
  const networkRef = useRef(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // Function to fetch graph data from backend
  const fetchGraph = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get('http://localhost:8000/graph');
      setGraphData(res.data);
    } catch (err) {
      setError('Failed to fetch graph data');
    } finally {
      setLoading(false);
    }
  };

  // Function to search the knowledge graph using RAG
  const searchGraph = async () => {
    if (!searchQuery.trim()) return;
    
    setSearchLoading(true);
    setError(null);
    try {
      const res = await axios.post('http://localhost:8000/search', {
        query: searchQuery,
        max_results: 5
      });
      setSearchResults(res.data);
    } catch (err) {
      setError('Failed to search knowledge graph');
    } finally {
      setSearchLoading(false);
    }
  };

  // Render the graph when data changes
  useEffect(() => {
    if (networkRef.current && graphData.nodes.length > 0) {
      const data = {
        nodes: graphData.nodes,
        edges: graphData.edges,
      };
      const options = {
        nodes: { shape: 'dot', size: 20, font: { size: 16 } },
        edges: { arrows: 'to', font: { align: 'middle' } },
        physics: { stabilization: true },
      };
      new Network(networkRef.current, data, options);
    }
  }, [graphData]);

  return (
    <div className="App">
      <h1>Knowledge Graph RAG Search Demo</h1>
      
      {/* Graph Controls */}
      <div style={{ marginBottom: 20 }}>
        <button onClick={fetchGraph} disabled={loading} style={{ marginRight: 10 }}>
          {loading ? 'Loading...' : 'Load Knowledge Graph'}
        </button>
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
            style={{ flex: 1, padding: 10, fontSize: 16 }}
            onKeyPress={(e) => e.key === 'Enter' && searchGraph()}
          />
          <button 
            onClick={searchGraph} 
            disabled={searchLoading || !searchQuery.trim()}
            style={{ padding: '10px 20px', fontSize: 16 }}
          >
            {searchLoading ? 'Searching...' : 'Search'}
          </button>
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
      
      {error && <div style={{ color: 'red', marginBottom: 20 }}>{error}</div>}
      
      {/* Graph Visualization */}
      <div>
        <h2>Graph Visualization</h2>
        <div ref={networkRef} style={{ height: '500px', border: '1px solid #ccc' }} />
      </div>
    </div>
  );
}

export default App;
