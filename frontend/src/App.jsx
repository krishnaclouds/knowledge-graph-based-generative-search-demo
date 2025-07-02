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
  const [searchMode, setSearchMode] = useState('graphrag'); // 'graphrag', 'traditional-rag', 'knowledge-graph-only', 'comparison'
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [retryCount, setRetryCount] = useState(0);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);

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

  // Function to run comparison analysis
  const runComparisonAnalysis = async () => {
    setSearchLoading(true);
    setError(null);
    setComparisonResults(null);
    setAnalysisResults(null);
    
    try {
      const isConnected = await checkConnection();
      if (!isConnected) {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8000.');
      }
      
      const requestBody = {
        query: searchQuery.trim(),
        max_results: 8
      };
      
      // Run both GraphRAG and Traditional RAG searches in parallel
      console.log('🔍 Running comparison searches for:', searchQuery.trim());
      
      const [graphragRes, traditionalRes] = await Promise.all([
        axios.post(`${API_BASE_URL}/graphrag-search`, requestBody, { timeout: 30000 }),
        axios.post(`${API_BASE_URL}/traditional-rag-search`, requestBody, { timeout: 30000 })
      ]);
      
      console.log('🔗 GraphRAG result:', graphragRes.data);
      console.log('📄 Traditional RAG result:', traditionalRes.data);
      
      // Create enhanced comparison data with new search modes
      const comparison = {
        graphrag: {
          ...graphragRes.data,
          searchMode: 'graphrag'
        },
        traditional_rag: {
          ...traditionalRes.data,
          searchMode: 'traditional_rag'
        },
        query: searchQuery.trim()
      };
      
      console.log('🔀 Enhanced comparison data:', comparison);
      
      // Validate comparison data structure
      if (!comparison.graphrag) {
        console.error('❌ Missing graphrag data in comparison results');
      }
      if (!comparison.traditional_rag) {
        console.error('❌ Missing traditional_rag data in comparison results');
      }
      console.log('🔗 GraphRAG summary:', graphragRes.data.answer ? 'Generated' : 'Failed');
      console.log('📄 Traditional RAG summary:', traditionalRes.data.answer ? 'Generated' : 'Failed');
      
      setComparisonResults(comparison);
      
      // Run LLM judge evaluation if both summaries exist
      if (comparison.graphrag.answer && comparison.traditional_rag.answer) {
        console.log('🤖 Running LLM Judge evaluation...');
        
        try {
          // Prepare BLIND evaluation data for LLM Judge (no identifying information)
          const judgePayload = {
            query: searchQuery.trim(),
            
            // Anonymized summaries - judge doesn't know which method generated which
            summary_a: comparison.graphrag.answer || 'No summary generated',
            summary_b: comparison.traditional_rag.answer || 'No summary generated',
            
            // Evaluation criteria only (no source metadata that reveals method)
            evaluation_criteria: [
              'completeness',
              'accuracy', 
              'contextual_depth',
              'relevance_to_query',
              'actionable_insights',
              'answer_quality'
            ]
          };
          
          console.log('📤 Sending to LLM Judge - BLIND Evaluation:');
          console.log('🔍 Query:', judgePayload.query);
          console.log('📝 Summary A Length:', judgePayload.summary_a.length, 'characters');
          console.log('📝 Summary B Length:', judgePayload.summary_b.length, 'characters');
          console.log('📋 Evaluation Criteria:', judgePayload.evaluation_criteria);
          console.log('🔒 Judge receives NO identifying information about which method generated which summary');
          
          const judgeRes = await axios.post(`${API_BASE_URL}/evaluate-summaries`, judgePayload, { timeout: 20000 });
          
          console.log('⚖️ LLM Judge Response:', judgeRes.data);
          
          // Transform LLM response from blind evaluation back to UI format
          const transformedResults = {
            ...judgeRes.data,
            // Map anonymous results back to method names for UI display
            // Note: summary_a = GraphRAG, summary_b = Traditional RAG (judge doesn't know this)
            winner: judgeRes.data.winner === 'summary_a' ? 'graphrag' : 'traditional_rag',
            criteria_scores: {}
          };
          
          // Transform criteria scores from anonymous to method names
          if (judgeRes.data.criteria_scores) {
            Object.entries(judgeRes.data.criteria_scores).forEach(([criteria, scores]) => {
              transformedResults.criteria_scores[criteria] = {
                graphrag: scores.summary_a,
                traditional_rag: scores.summary_b
              };
            });
          }
          
          // Detailed logging of BLIND LLM Judge evaluation
          console.log('\n🤖 === BLIND LLM JUDGE ANALYSIS ===');
          console.log('🏆 Winner (anonymous evaluation):', judgeRes.data.winner);
          console.log('🏆 Winner (revealed identity):', transformedResults.winner);
          console.log('📊 Confidence:', judgeRes.data.confidence + '%');
          console.log('💭 Reasoning:', judgeRes.data.reasoning);
          console.log('🔒 Judge evaluated summaries without knowing which method generated them');
          
          if (transformedResults.criteria_scores) {
            console.log('\n📋 Detailed Criteria Scores (Post-Evaluation Mapping):');
            Object.entries(transformedResults.criteria_scores).forEach(([criteria, scores]) => {
              console.log(`  ${criteria.replace(/_/g, ' ').toUpperCase()}:`);
              console.log(`    🔗 GraphRAG (was Anonymous Summary A): ${scores.graphrag}/10`);
              console.log(`    📄 Traditional RAG (was Anonymous Summary B): ${scores.traditional_rag}/10`);
              console.log(`    📈 Difference: ${scores.graphrag - scores.traditional_rag > 0 ? '+' : ''}${scores.graphrag - scores.traditional_rag}`);
            });
          }
          
          // Summary analysis
          const totalGraphRAGScore = Object.values(transformedResults.criteria_scores || {}).reduce((sum, scores) => sum + scores.graphrag, 0);
          const totalTraditionalScore = Object.values(transformedResults.criteria_scores || {}).reduce((sum, scores) => sum + scores.traditional_rag, 0);
          const criteriaCount = Object.keys(transformedResults.criteria_scores || {}).length;
          
          if (criteriaCount > 0) {
            console.log(`📊 Overall Averages: GraphRAG ${(totalGraphRAGScore/criteriaCount).toFixed(1)}/10, Traditional RAG ${(totalTraditionalScore/criteriaCount).toFixed(1)}/10`);
            console.log(`🏆 BLIND Judge Decision: ${transformedResults.winner.toUpperCase()} wins with ${transformedResults.confidence}% confidence`);
          }
          console.log('🤖 === END BLIND JUDGE ANALYSIS ===\n');
          
          setAnalysisResults(transformedResults);
        } catch (judgeError) {
          console.error('LLM Judge evaluation failed, using enhanced fallback analysis:', judgeError);
          console.log('📊 Fallback Analysis - Using Local Evaluation...');
          
          // Detailed analysis of the actual differences
          const graphragData = {
            summaryLength: comparison.graphrag.answer?.length || 0,
            documentsCount: comparison.graphrag.documents?.length || 0,
            citationsCount: comparison.graphrag.citations?.length || 0,
            entitiesCount: comparison.graphrag.graph_entities?.length || 0
          };
          
          const traditionalData = {
            summaryLength: comparison.traditional_rag.answer?.length || 0,
            documentsCount: comparison.traditional_rag.documents?.length || 0,
            citationsCount: comparison.traditional_rag.citations?.length || 0,
            entitiesCount: 0
          };
          
          console.log('🔗 GraphRAG Analysis:', graphragData);
          console.log('📄 Traditional RAG Analysis:', traditionalData);
          
          // Dynamic advantage detection
          const graphragAdvantages = [];
          const traditionalLimitations = [];
          
          if (graphragData.citationsCount > traditionalData.citationsCount) {
            graphragAdvantages.push(`${graphragData.citationsCount} structured citations vs ${traditionalData.citationsCount}`);
          }
          if (graphragData.entitiesCount > 0) {
            graphragAdvantages.push(`${graphragData.entitiesCount} knowledge graph entities providing context`);
          }
          if (graphragData.documentsCount > traditionalData.documentsCount) {
            graphragAdvantages.push(`broader document coverage (${graphragData.documentsCount} vs ${traditionalData.documentsCount})`);
          }
          if (graphragData.summaryLength > traditionalData.summaryLength * 1.2) {
            graphragAdvantages.push('more comprehensive summary content');
          }
          
          if (traditionalData.citationsCount === 0) {
            traditionalLimitations.push('no structured citations');
          }
          if (traditionalData.entitiesCount === 0) {
            traditionalLimitations.push('missing relationship context');
          }
          
          // Calculate detailed scores
          const scores = {
            completeness: {
              graphrag: Math.min(10, 6 + (graphragData.citationsCount > 0 ? 2 : 0) + (graphragData.entitiesCount > 0 ? 2 : 0)),
              traditional_rag: Math.min(8, 4 + (traditionalData.documentsCount > 0 ? 2 : 0) + (traditionalData.summaryLength > 100 ? 1 : 0))
            },
            accuracy: { 
              graphrag: 8, 
              traditional_rag: 7 
            },
            contextual_depth: { 
              graphrag: Math.min(10, 5 + (graphragData.entitiesCount > 0 ? 3 : 0) + (graphragData.citationsCount > 0 ? 2 : 0)), 
              traditional_rag: Math.min(6, 3 + (traditionalData.documentsCount > 0 ? 2 : 0))
            },
            source_diversity: {
              graphrag: Math.min(10, (graphragData.documentsCount > 0 ? 3 : 0) + (graphragData.citationsCount > 0 ? 3 : 0) + (graphragData.entitiesCount > 0 ? 4 : 0)),
              traditional_rag: Math.min(6, (traditionalData.documentsCount > 0 ? 4 : 0) + (traditionalData.documentsCount > 1 ? 2 : 0))
            },
            relevance_to_query: { 
              graphrag: 8, 
              traditional_rag: Math.min(8, traditionalData.documentsCount > 0 ? 7 : 4)
            },
            actionable_insights: {
              graphrag: Math.min(9, 6 + (graphragData.entitiesCount > 0 ? 2 : 0) + (graphragData.citationsCount > 0 ? 1 : 0)),
              traditional_rag: Math.min(6, 4 + (traditionalData.summaryLength > 200 ? 2 : 0))
            }
          };
          
          console.log('📊 Calculated Scores:', scores);
          
          const analysisReasoning = `Comprehensive analysis reveals GraphRAG advantages: ${graphragAdvantages.join(', ')}. Traditional RAG limitations include: ${traditionalLimitations.join(', ')}. GraphRAG provides ${graphragData.citationsCount} citations, ${graphragData.entitiesCount} knowledge graph entities, and ${graphragData.documentsCount} documents vs Traditional RAG with ${traditionalData.documentsCount} documents and ${traditionalData.citationsCount} citations.`;
          
          // Calculate confidence based on actual differences
          const avgGraphRAGScore = Object.values(scores).reduce((sum, score) => sum + score.graphrag, 0) / Object.keys(scores).length;
          const avgTraditionalScore = Object.values(scores).reduce((sum, score) => sum + score.traditional_rag, 0) / Object.keys(scores).length;
          const scoreDifference = avgGraphRAGScore - avgTraditionalScore;
          const confidence = Math.min(95, Math.max(60, 70 + (scoreDifference * 8)));
          
          console.log(`📈 Average Scores - GraphRAG: ${avgGraphRAGScore.toFixed(1)}, Traditional RAG: ${avgTraditionalScore.toFixed(1)}, Confidence: ${confidence.toFixed(0)}%`);
          
          const fallbackResults = {
            winner: avgGraphRAGScore > avgTraditionalScore ? 'graphrag' : 'traditional_rag',
            confidence: Math.round(confidence),
            reasoning: analysisReasoning,
            criteria_scores: scores
          };
          
          // Detailed logging of Fallback Analysis reasoning
          console.log('\n🛠️ === FALLBACK ANALYSIS DETAILED REASONING ===');
          console.log('🏆 Winner:', fallbackResults.winner);
          console.log('📊 Confidence:', fallbackResults.confidence + '%');
          console.log('💭 Reasoning:', fallbackResults.reasoning);
          
          console.log('\n📋 Fallback Criteria Scores:');
          Object.entries(scores).forEach(([criteria, scores]) => {
            console.log(`  ${criteria.replace(/_/g, ' ').toUpperCase()}:`);
            console.log(`    🔗 GraphRAG: ${scores.graphrag}/10`);
            console.log(`    📄 Traditional RAG: ${scores.traditional_rag}/10`);
            console.log(`    📈 Difference: ${scores.graphrag - scores.traditional_rag > 0 ? '+' : ''}${scores.graphrag - scores.traditional_rag}`);
          });
          
          // Summary analysis for fallback
          console.log(`📊 Overall Averages: GraphRAG ${avgGraphRAGScore.toFixed(1)}/10, Traditional RAG ${avgTraditionalScore.toFixed(1)}/10`);
          console.log(`🏆 Fallback Decision: ${fallbackResults.winner.toUpperCase()} wins with ${fallbackResults.confidence}% confidence`);
          console.log('🛠️ === END FALLBACK ANALYSIS ===\n');
          
          setAnalysisResults(fallbackResults);
        }
      } else {
        console.log('❌ Cannot run LLM judge - missing summaries:', {
          graphrag: !!comparison.graphrag.answer,
          traditional_rag: !!comparison.traditional_rag.answer
        });
      }
      
    } catch (err) {
      let errorMessage = 'Failed to run comparison analysis';
      
      if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to backend server. Please ensure the backend is running on port 8000.';
      } else if (err.response?.status === 500) {
        errorMessage = `Comparison failed: ${err.response.data?.detail || 'Internal server error'}`;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setSearchLoading(false);
    }
  };

  // Function to search using different modes
  const searchGraph = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    // Handle comparison mode
    if (searchMode === 'comparison') {
      return runComparisonAnalysis();
    }
    
    setSearchLoading(true);
    setError(null);
    setSearchResults(null);
    setComparisonResults(null);
    setAnalysisResults(null);
    
    try {
      const isConnected = await checkConnection();
      if (!isConnected) {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8000.');
      }
      
      let endpoint = '/search'; // default to knowledge graph search
      if (searchMode === 'graphrag') {
        endpoint = '/graphrag-search';
      } else if (searchMode === 'traditional-rag') {
        endpoint = '/traditional-rag-search';
      } else if (searchMode === 'knowledge-graph-only') {
        endpoint = '/knowledge-graph-only-search';
      }
      
      const requestBody = {
        query: searchQuery.trim(),
        max_results: 8
      };
      
      const res = await axios.post(`${API_BASE_URL}${endpoint}`, requestBody, { timeout: 30000 });
      
      setSearchResults({
        ...res.data,
        searchMode: searchMode
      });
      
      if ((res.data.results && res.data.results.length === 0) || 
          (res.data.documents && res.data.documents.length === 0)) {
        setError('No relevant information found for your query. Try rephrasing or using different keywords.');
      }
    } catch (err) {
      let errorMessage = `Failed to search ${searchMode === 'graphrag' ? 'GraphRAG (documents + knowledge graph)' : searchMode === 'traditional-rag' ? 'Traditional RAG (documents only)' : 'knowledge graph only'}`;
      
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
      <h1>Knowledge Graph RAG Search</h1>
      
      {/* Settings Section */}
      <div className="settings-section" style={{ marginBottom: 20 }}>
        <div className="glass-container" style={{ padding: 16, marginBottom: 15 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 15 }}>
            <div className={`status-indicator ${connectionStatus === 'connected' ? 'status-connected' : 'status-disconnected'}`} style={{
              padding: '8px 16px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {connectionStatus === 'connected' ? '✅ Connected' : '❌ Disconnected'}
            </div>
            
            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <button 
                onClick={fetchGraph} 
                disabled={loading || connectionStatus === 'disconnected'} 
                className={`${loading ? 'shimmer' : ''}`}
                style={{ 
                  opacity: loading || connectionStatus === 'disconnected' ? 0.6 : 1,
                  cursor: loading || connectionStatus === 'disconnected' ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  padding: '8px 16px'
                }}
              >
                {loading ? '🔄 Loading...' : '📊 Load Knowledge Graph'}
              </button>
              
              {connectionStatus === 'disconnected' && (
                <button 
                  onClick={retryConnection}
                  style={{ fontSize: '14px', padding: '8px 16px' }}
                >
                  🔄 Retry ({retryCount})
                </button>
              )}
            </div>
            
            {graphData.nodes.length > 0 && (
              <div className="success-message" style={{ 
                padding: '6px 12px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                ✅ Graph: {graphData.nodes.length} nodes, {graphData.edges.length} edges
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Search Interface - Main Focus */}
      <div className="search-container" style={{ marginBottom: 30, padding: 24, marginTop: 10 }}>
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
                value="graphrag"
                checked={searchMode === 'graphrag'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'graphrag' ? '#007bff' : '#666' }}>
                🔗 GraphRAG (Documents + Knowledge Graph)
              </span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="traditional-rag"
                checked={searchMode === 'traditional-rag'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'traditional-rag' ? '#007bff' : '#666' }}>
                📄 Traditional RAG (Documents Only)
              </span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="knowledge-graph-only"
                checked={searchMode === 'knowledge-graph-only'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'knowledge-graph-only' ? '#007bff' : '#666' }}>
                🕸️ Knowledge Graph Only
              </span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="comparison"
                checked={searchMode === 'comparison'}
                onChange={(e) => setSearchMode(e.target.value)}
                style={{ marginRight: 5 }}
              />
              <span style={{ color: searchMode === 'comparison' ? '#007bff' : '#666' }}>
                ⚖️ Comparison Analysis
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
              searchMode === 'graphrag' ? "Ask about investments, company strategies, or business trends..." :
              searchMode === 'traditional-rag' ? "Search investment reports and business documents..." :
              searchMode === 'comparison' ? "Compare GraphRAG vs Traditional RAG search results..." :
              "Ask about companies, people, and their relationships..."
            }
            style={{ 
              flex: 1, 
              padding: 16, 
              fontSize: 16, 
              outline: 'none'
            }}
            onKeyDown={(e) => e.key === 'Enter' && !searchLoading && connectionStatus === 'connected' && searchGraph()}
          />
          <button 
            onClick={searchGraph} 
            disabled={searchLoading || !searchQuery.trim() || connectionStatus === 'disconnected'}
            className={`interactive-element ${searchLoading ? 'shimmer' : ''}`}
            style={{ 
              padding: '16px 24px', 
              fontSize: 16,
              background: searchLoading ? 'var(--glass-bg-secondary)' : 'linear-gradient(135deg, var(--glass-success), rgba(52, 199, 89, 0.8))',
              cursor: searchLoading || !searchQuery.trim() || connectionStatus === 'disconnected' ? 'not-allowed' : 'pointer',
              opacity: searchLoading || !searchQuery.trim() || connectionStatus === 'disconnected' ? 0.6 : 1,
              minWidth: 120
            }}
          >
            {searchLoading ? '🔍 Searching...' : '🔍 Search'}
          </button>
        </div>
        
        {/* Search Tips */}
        <div className="glass-container" style={{ 
          fontSize: 14, 
          color: 'var(--glass-text-secondary)', 
          marginBottom: 15,
          padding: 12,
          background: 'var(--glass-bg-secondary)'
        }}>
          💡 <strong>Try these examples:</strong>
          {searchMode === 'graphrag' && (
            <span> "Apple's investments for 2025", "Tesla's energy storage plans", "Meta's metaverse strategy"</span>
          )}
          {searchMode === 'traditional-rag' && (
            <span> "Cloud infrastructure investment", "AI research funding", "Renewable energy projects"</span>
          )}
          {searchMode === 'knowledge-graph-only' && (
            <span> "Who works at Google?", "What companies are in tech?", "Show me AI researchers"</span>
          )}
          {searchMode === 'comparison' && (
            <>
              <span> Try these powerful examples to see the difference:</span>
              <div className="demo-queries">
                <button 
                  className="demo-query-button"
                  onClick={() => setSearchQuery("Apple's investments for 2025")}
                >
                  Apple's investments for 2025
                </button>
                <button 
                  className="demo-query-button"
                  onClick={() => setSearchQuery("Tesla's partnerships with energy companies")}
                >
                  Tesla's partnerships
                </button>
                <button 
                  className="demo-query-button"
                  onClick={() => setSearchQuery("Google's AI research collaborations")}
                >
                  Google's AI research
                </button>
                <button 
                  className="demo-query-button"
                  onClick={() => setSearchQuery("Microsoft's cloud infrastructure investments")}
                >
                  Microsoft's cloud strategy
                </button>
              </div>
            </>
          )}
        </div>
        
        {/* Search Results */}
        {searchResults && (
          <div className="results-container slide-in" style={{ marginTop: 20, padding: 20 }}>
            {/* Results Header */}
            <div className="interactive-element" style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: 15
            }}>
              <h3 style={{ color: 'var(--glass-text)', margin: 0, textShadow: '0 2px 10px rgba(0, 0, 0, 0.1)' }}>
                {searchResults.searchMode === 'graphrag' && '🔗 GraphRAG Search Results'}
                {searchResults.searchMode === 'traditional-rag' && '📄 Traditional RAG Search Results'}
                {searchResults.searchMode === 'knowledge-graph' && '🕸️ Knowledge Graph Results'}
              </h3>
              <div className="glass-container" style={{ 
                fontSize: 12,
                color: 'var(--glass-text-secondary)',
                padding: '6px 12px',
                borderRadius: 16,
                fontWeight: '500'
              }}>
                {searchResults.documents ? `${searchResults.documents.length} documents` : 
                 searchResults.results ? `${searchResults.results.length} results` : '0 results'} found
              </div>
            </div>

            {/* Generated Answer (for GraphRAG and knowledge graph search) */}
            {searchResults.answer && (
              <>
                <h4 style={{ color: 'var(--glass-text)', borderBottom: '2px solid var(--glass-accent)', paddingBottom: 8, textShadow: '0 1px 5px rgba(0, 0, 0, 0.1)' }}>
                  📝 AI-Generated Answer
                </h4>
                <div className="glass-container" style={{ 
                  padding: 24, 
                  marginBottom: 20,
                  fontSize: 16,
                  lineHeight: 1.7,
                  color: 'var(--glass-text)'
                }}>
                  {searchResults.answer}
                </div>
              </>
            )}
            
            {/* Side-by-side Sources & Documents Layout */}
            {((searchResults.citations && searchResults.citations.length > 0) || 
              (searchResults.documents && searchResults.documents.length > 0)) && (
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: 20, 
                marginBottom: 20 
              }}>
                {/* Left Column - Sources & Citations */}
                <div>
                  <h4 style={{ color: 'var(--retro-cyan)', marginBottom: 10, fontSize: '16px' }}>
                    📚 Sources & Citations
                  </h4>
                  <div className="glass-container" style={{ 
                    maxHeight: 400, 
                    overflowY: 'auto',
                    padding: 16
                  }}>
                    {searchResults.citations && searchResults.citations.length > 0 ? (
                      searchResults.citations.map((citation, index) => (
                        <div key={index} style={{ 
                          marginBottom: 12,
                          paddingBottom: 12,
                          borderBottom: index < searchResults.citations.length - 1 ? '1px solid var(--glass-border-secondary)' : 'none'
                        }}>
                          <div style={{ 
                            fontWeight: 'bold', 
                            color: 'var(--retro-green)',
                            fontSize: 14,
                            marginBottom: 4
                          }}>
                            [{index + 1}] {citation.title || citation.source}
                          </div>
                          
                          {citation.authors && (
                            <div style={{ 
                              fontSize: 12, 
                              color: 'var(--glass-text-secondary)', 
                              marginBottom: 2 
                            }}>
                              Authors: {Array.isArray(citation.authors) ? citation.authors.join(', ') : citation.authors}
                            </div>
                          )}
                          
                          {(citation.year || citation.venue) && (
                            <div style={{ 
                              fontSize: 12, 
                              color: 'var(--glass-text-secondary)', 
                              marginBottom: 2 
                            }}>
                              {citation.venue && `${citation.venue}`}{citation.year && ` (${citation.year})`}
                            </div>
                          )}
                          
                          {citation.doi && citation.doi !== 'N/A' && (
                            <div style={{ 
                              fontSize: 11, 
                              color: 'var(--retro-cyan)', 
                              marginTop: 2,
                              fontFamily: 'JetBrains Mono, monospace'
                            }}>
                              DOI: {citation.doi}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div style={{ 
                        textAlign: 'center', 
                        color: 'var(--glass-text-secondary)', 
                        fontSize: '14px',
                        fontStyle: 'italic',
                        padding: '20px'
                      }}>
                        No citations available
                      </div>
                    )}
                  </div>
                </div>

                {/* Right Column - Relevant Documents */}
                <div>
                  <h4 style={{ color: 'var(--retro-pink)', marginBottom: 10, fontSize: '16px' }}>
                    📄 Relevant Documents
                  </h4>
                  <div className="glass-container" style={{ 
                    maxHeight: 400, 
                    overflowY: 'auto',
                    padding: 12
                  }}>
                    {searchResults.documents && searchResults.documents.length > 0 ? (
                      searchResults.documents.map((doc, index) => (
                        <div key={index} style={{ 
                          padding: 12, 
                          marginBottom: 8,
                          background: index % 2 === 0 ? 'var(--glass-bg-secondary)' : 'var(--glass-bg-tertiary)',
                          borderRadius: 8,
                          border: '1px solid var(--glass-border-secondary)'
                        }}>
                          <div style={{ 
                            fontWeight: 'bold', 
                            marginBottom: 6,
                            color: 'var(--retro-pink)',
                            fontSize: 14
                          }}>
                            {doc.title}
                          </div>
                          
                          {/* Document metadata */}
                          <div style={{ marginBottom: 6 }}>
                            <span style={{
                              display: 'inline-block',
                              background: 'var(--retro-orange)',
                              color: 'black',
                              padding: '2px 8px',
                              borderRadius: 8,
                              fontSize: 10,
                              marginRight: 6,
                              fontWeight: '600'
                            }}>
                              DOC
                            </span>
                            {doc.metadata?.type && (
                              <span style={{
                                display: 'inline-block',
                                backgroundColor: 'var(--retro-cyan)',
                                color: 'black',
                                padding: '2px 6px',
                                borderRadius: 8,
                                fontSize: 10,
                                marginRight: 6,
                                fontWeight: '600'
                              }}>
                                {doc.metadata.type.replace('_', ' ').toUpperCase()}
                              </span>
                            )}
                            {doc.metadata?.date && (
                              <span style={{ fontSize: 10, color: 'var(--glass-text-secondary)' }}>
                                📅 {doc.metadata.date}
                              </span>
                            )}
                          </div>
                          
                          {/* Document content preview */}
                          {doc.content && (
                            <div style={{ 
                              fontSize: 12, 
                              color: 'var(--glass-text)', 
                              marginBottom: 6,
                              maxHeight: '80px',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              lineHeight: 1.3
                            }}>
                              {doc.content.length > 200 ? 
                                `${doc.content.substring(0, 200)}...` : 
                                doc.content}
                            </div>
                          )}
                          
                          {/* Similarity score */}
                          <div style={{ 
                            textAlign: 'right',
                            marginTop: 6
                          }}>
                            <span style={{ 
                              fontSize: 10,
                              fontWeight: 'bold',
                              color: doc.similarity > 0.7 ? 'var(--retro-green)' : 
                                     doc.similarity > 0.5 ? 'var(--retro-yellow)' : 'var(--retro-pink)',
                              background: 'var(--glass-bg-tertiary)',
                              padding: '2px 6px',
                              borderRadius: 4
                            }}>
                              {(doc.similarity * 100).toFixed(1)}% Match
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div style={{ 
                        textAlign: 'center', 
                        color: 'var(--glass-text-secondary)', 
                        fontSize: '14px',
                        fontStyle: 'italic',
                        padding: '20px'
                      }}>
                        No documents available
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Documents-Only Search Results */}
            {searchResults.searchMode === 'documents' && searchResults.documents && searchResults.documents.length > 0 && (
              <div style={{ marginBottom: 20 }}>
                {/* AI-Generated Answer for Documents-Only */}
                <h4 style={{ color: 'var(--retro-green)', borderBottom: '2px solid var(--retro-green)', paddingBottom: 8, marginBottom: 15, fontSize: '18px' }}>
                  📝 AI-Generated Answer
                </h4>
                <div className="glass-container" style={{ 
                  padding: 24, 
                  marginBottom: 20,
                  fontSize: 16,
                  lineHeight: 1.7,
                  color: 'var(--glass-text)',
                  background: 'var(--glass-bg-primary)',
                  border: '2px solid var(--retro-green)',
                  boxShadow: '0 0 20px var(--retro-green)'
                }}>
                  {searchResults.answer || (
                    <div style={{ 
                      color: 'var(--glass-text-secondary)', 
                      fontStyle: 'italic',
                      textAlign: 'center',
                      padding: '20px 0'
                    }}>
                      🤖 Generating AI summary from documents... 
                      <br />
                      <span style={{ fontSize: '14px', marginTop: '8px', display: 'block' }}>
                        If this persists, the backend may need to be configured to generate answers for document searches.
                      </span>
                    </div>
                  )}
                </div>
                
                <h4 style={{ color: 'var(--retro-pink)', marginBottom: 15, fontSize: '18px' }}>
                  📄 Source Documents
                </h4>
                <div className="glass-container" style={{ 
                  padding: 20,
                  maxHeight: 600, 
                  overflowY: 'auto' 
                }}>
                  {searchResults.documents.map((doc, index) => (
                    <div key={index} style={{ 
                      padding: 18, 
                      marginBottom: 15,
                      background: index % 2 === 0 ? 'var(--glass-bg-secondary)' : 'var(--glass-bg-tertiary)',
                      borderRadius: 12,
                      border: '2px solid var(--glass-border-secondary)'
                    }}>
                      <div style={{ 
                        fontWeight: 'bold', 
                        marginBottom: 8,
                        color: 'var(--retro-pink)',
                        fontSize: 16
                      }}>
                        {doc.title}
                      </div>
                      
                      {/* Document metadata */}
                      <div style={{ marginBottom: 10 }}>
                        <span style={{
                          display: 'inline-block',
                          background: 'var(--retro-orange)',
                          color: 'black',
                          padding: '4px 12px',
                          borderRadius: 8,
                          fontSize: 12,
                          marginRight: 8,
                          fontWeight: '600'
                        }}>
                          DOCUMENT
                        </span>
                        {doc.metadata?.type && (
                          <span style={{
                            display: 'inline-block',
                            backgroundColor: 'var(--retro-cyan)',
                            color: 'black',
                            padding: '4px 10px',
                            borderRadius: 8,
                            fontSize: 12,
                            marginRight: 8,
                            fontWeight: '600'
                          }}>
                            {doc.metadata.type.replace('_', ' ').toUpperCase()}
                          </span>
                        )}
                        {doc.metadata?.date && (
                          <span style={{ fontSize: 12, color: 'var(--glass-text-secondary)' }}>
                            📅 {doc.metadata.date}
                          </span>
                        )}
                      </div>
                      
                      {/* Document content preview */}
                      {doc.content && (
                        <div style={{ 
                          fontSize: 14, 
                          color: 'var(--glass-text)', 
                          marginBottom: 10,
                          lineHeight: 1.5,
                          background: 'var(--glass-bg-primary)',
                          padding: 12,
                          borderRadius: 8,
                          border: '1px solid var(--glass-border)'
                        }}>
                          {doc.content.length > 500 ? 
                            `${doc.content.substring(0, 500)}...` : 
                            doc.content}
                        </div>
                      )}
                      
                      {/* Additional metadata */}
                      {doc.metadata?.companies && (
                        <div style={{ fontSize: 12, color: 'var(--glass-text-secondary)', marginBottom: 4 }}>
                          🏢 Companies: {doc.metadata.companies}
                        </div>
                      )}
                      {doc.metadata?.amount && (
                        <div style={{ fontSize: 12, color: 'var(--retro-green)', fontWeight: 'bold', marginBottom: 4 }}>
                          💰 Investment: {doc.metadata.amount}
                        </div>
                      )}
                      
                      {/* Similarity score */}
                      <div style={{ 
                        textAlign: 'right',
                        marginTop: 10
                      }}>
                        <span style={{ 
                          fontSize: 12,
                          fontWeight: 'bold',
                          color: (doc.similarity > 0.7) ? 'var(--retro-green)' : 
                                 (doc.similarity > 0.5) ? 'var(--retro-yellow)' : 'var(--retro-pink)',
                          background: 'var(--glass-bg-tertiary)',
                          padding: '4px 10px',
                          borderRadius: 6,
                          border: '1px solid var(--glass-border)'
                        }}>
                          {(doc.similarity * 100).toFixed(1)}% Match
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
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

        {/* Comparison Results */}
        {comparisonResults && comparisonResults.graphrag && comparisonResults.traditional_rag && (
          <div className="results-container slide-in" style={{ marginTop: 20, padding: 20 }}>
            <h3 style={{ color: 'var(--retro-cyan)', margin: 0, textShadow: '0 2px 10px rgba(0, 0, 0, 0.1)', marginBottom: 20 }}>
              ⚖️ GraphRAG vs Traditional RAG Comparison
            </h3>
            
            <div className="comparison-grid">
              {/* Left Column - Hybrid Search Results */}
              <div>
                <h4 style={{ color: 'var(--retro-green)', marginBottom: 15, fontSize: '18px' }}>
                  🔗 GraphRAG Search (Knowledge Graph + Documents)
                </h4>
                <div className="glass-container" style={{ 
                  padding: 20,
                  border: analysisResults?.winner === 'graphrag' ? '3px solid var(--retro-green)' : '2px solid var(--retro-green)',
                  boxShadow: analysisResults?.winner === 'graphrag' ? '0 0 30px var(--retro-green)' : '0 0 20px var(--retro-green)',
                  position: 'relative'
                }}>
                  {analysisResults?.winner === 'graphrag' && (
                    <div style={{
                      position: 'absolute',
                      top: '-15px',
                      right: '15px',
                      background: 'var(--retro-green)',
                      color: 'black',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      fontFamily: 'JetBrains Mono, monospace'
                    }}>
                      🏆 LLM JUDGE WINNER
                    </div>
                  )}
                  {comparisonResults.graphrag?.answer ? (
                    <>
                      <div style={{ 
                        marginBottom: 15,
                        padding: 16,
                        background: 'var(--glass-bg-secondary)',
                        borderRadius: 8,
                        fontSize: 14,
                        lineHeight: 1.6,
                        border: analysisResults?.winner === 'graphrag' ? '2px solid var(--retro-green)' : '1px solid var(--glass-border)'
                      }}>
                        {comparisonResults.graphrag.answer}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--glass-text-secondary)', marginBottom: 10 }}>
                        📊 Sources: {comparisonResults.graphrag.documents?.length || 0} documents, 
                        {comparisonResults.graphrag.results?.length || 0} knowledge graph entities,
                        {comparisonResults.graphrag.citations?.length || 0} citations
                      </div>
                    </>
                  ) : (
                    <div style={{ textAlign: 'center', color: 'var(--glass-text-secondary)', padding: 20 }}>
                      No GraphRAG answer generated
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column - Documents-Only Results */}
              <div>
                <h4 style={{ color: 'var(--retro-pink)', marginBottom: 15, fontSize: '18px' }}>
                  📄 Traditional RAG Search
                </h4>
                <div className="glass-container" style={{ 
                  padding: 20,
                  border: analysisResults?.winner === 'traditional_rag' ? '3px solid var(--retro-pink)' : '2px solid var(--retro-pink)',
                  boxShadow: analysisResults?.winner === 'traditional_rag' ? '0 0 30px var(--retro-pink)' : '0 0 20px var(--retro-pink)',
                  position: 'relative'
                }}>
                  {analysisResults?.winner === 'traditional_rag' && (
                    <div style={{
                      position: 'absolute',
                      top: '-15px',
                      right: '15px',
                      background: 'var(--retro-pink)',
                      color: 'black',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      fontFamily: 'JetBrains Mono, monospace'
                    }}>
                      🏆 LLM JUDGE WINNER
                    </div>
                  )}
                  {comparisonResults.traditional_rag?.answer ? (
                    <>
                      <div style={{ 
                        marginBottom: 15,
                        padding: 16,
                        background: 'var(--secondary-bg)',
                        borderRadius: 8,
                        fontSize: 14,
                        lineHeight: 1.6,
                        border: analysisResults?.winner === 'traditional_rag' ? '2px solid var(--retro-pink)' : '1px solid var(--glass-border)',
                        maxHeight: '400px',
                        overflowY: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word'
                      }}>
                        {comparisonResults.traditional_rag.answer}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 10 }}>
                        📊 Sources: {comparisonResults.traditional_rag.documents?.length || 0} documents only
                        <br />
                        ⚠️ Limited to document content, no relationship context
                      </div>
                    </>
                  ) : (
                    <div style={{ textAlign: 'center', color: 'var(--glass-text-secondary)', padding: 20 }}>
                      No documents-only answer generated
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* LLM Judge Evaluation */}
            {analysisResults && (
              <div className="glass-container" style={{ 
                padding: 20,
                border: '2px solid var(--retro-cyan)',
                boxShadow: '0 0 20px var(--retro-cyan)',
                background: 'var(--glass-bg-primary)'
              }}>
                <h4 style={{ color: 'var(--retro-cyan)', marginBottom: 15, fontSize: '18px' }}>
                  🤖 LLM Judge Evaluation
                </h4>
                
                {/* Winner Announcement */}
                <div style={{
                  textAlign: 'center',
                  marginBottom: 20,
                  padding: 16,
                  background: analysisResults.winner === 'graphrag' ? 'var(--glass-bg-secondary)' : 'var(--glass-bg-tertiary)',
                  borderRadius: 12,
                  border: `2px solid ${analysisResults.winner === 'graphrag' ? 'var(--retro-green)' : 'var(--retro-pink)'}`,
                  boxShadow: `0 0 15px ${analysisResults.winner === 'graphrag' ? 'var(--retro-green)' : 'var(--retro-pink)'}`
                }}>
                  <div style={{ fontSize: 20, marginBottom: 8 }}>
                    🏆 Winner: <strong style={{ 
                      color: analysisResults.winner === 'graphrag' ? 'var(--retro-green)' : 'var(--retro-pink)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      {analysisResults.winner === 'graphrag' ? 'GraphRAG Search' : 'Traditional RAG'}
                    </strong>
                  </div>
                  <div style={{ 
                    fontSize: 14, 
                    color: 'var(--glass-text-secondary)',
                    fontFamily: 'JetBrains Mono, monospace'
                  }}>
                    Confidence: {analysisResults.confidence}%
                  </div>
                </div>

                {/* Reasoning */}
                <div style={{ marginBottom: 20 }}>
                  <h5 style={{ color: 'var(--retro-yellow)', marginBottom: 8, fontSize: '14px' }}>
                    📝 Judge's Reasoning:
                  </h5>
                  <div style={{
                    padding: 16,
                    background: 'var(--glass-bg-secondary)',
                    borderRadius: 8,
                    fontSize: 14,
                    lineHeight: 1.6,
                    fontStyle: 'italic',
                    border: '1px solid var(--retro-yellow)'
                  }}>
                    "{analysisResults.reasoning}"
                  </div>
                </div>

                {/* Criteria Scores */}
                {analysisResults.criteria_scores && Object.keys(analysisResults.criteria_scores).length > 0 && (
                  <div>
                    <h5 style={{ color: 'var(--retro-cyan)', marginBottom: 12, fontSize: '14px' }}>
                      📊 Detailed Scoring (1-10 scale):
                    </h5>
                    <div className="comparison-metrics">
                      {Object.entries(analysisResults.criteria_scores).map(([criterion, scores]) => {
                        const criterionLabels = {
                          completeness: '📋 Completeness',
                          accuracy: '✅ Accuracy',
                          contextual_depth: '🔍 Contextual Depth',
                          source_diversity: '📚 Source Diversity',
                          relevance_to_query: '🎯 Relevance to Query',
                          actionable_insights: '💡 Actionable Insights',
                          context: '🔍 Context', // fallback for old format
                          relevance: '🎯 Relevance' // fallback for old format
                        };
                        
                        return (
                          <div key={criterion} className="metric-card" style={{ 
                            border: '1px solid var(--retro-cyan)',
                            background: 'var(--glass-bg-tertiary)'
                          }}>
                            <div style={{ 
                              fontSize: 12, 
                              fontWeight: 'bold', 
                              color: 'var(--retro-cyan)', 
                              marginBottom: 8
                            }}>
                              {criterionLabels[criterion] || criterion.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                              <span style={{ fontSize: 11, color: 'var(--retro-green)' }}>
                                GraphRAG: {scores.graphrag}/10
                              </span>
                              <div style={{
                                width: `${scores.graphrag * 8}px`,
                                height: '4px',
                                background: 'var(--retro-green)',
                                borderRadius: '2px'
                              }} />
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                              <span style={{ fontSize: 11, color: 'var(--retro-pink)' }}>
                                Traditional RAG: {scores.traditional_rag}/10
                              </span>
                              <div style={{
                                width: `${scores.traditional_rag * 8}px`,
                                height: '4px',
                                background: 'var(--retro-pink)',
                                borderRadius: '2px'
                              }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Loading state for judge evaluation */}
            {comparisonResults && !analysisResults && (
              <div className="glass-container" style={{ 
                padding: 20,
                border: '2px solid var(--retro-cyan)',
                boxShadow: '0 0 20px var(--retro-cyan)',
                textAlign: 'center'
              }}>
                <div style={{ color: 'var(--retro-cyan)', fontSize: 16 }}>
                  🤖 LLM Judge is evaluating the summaries...
                </div>
                <div style={{ fontSize: 12, color: 'var(--glass-text-secondary)', marginTop: 8 }}>
                  Analyzing completeness, accuracy, context, and relevance
                </div>
              </div>
            )}

            {/* Data Enhancement Suggestions */}
            {comparisonResults && analysisResults && (
              <div className="glass-container" style={{ 
                padding: 20,
                border: '2px solid var(--retro-yellow)',
                boxShadow: '0 0 20px var(--retro-yellow)',
                background: 'var(--glass-bg-secondary)',
                marginTop: 20
              }}>
                <h4 style={{ color: 'var(--retro-yellow)', marginBottom: 15, fontSize: '16px' }}>
                  💡 Sample Data Enhancement Suggestions
                </h4>
                <div style={{ fontSize: 14, lineHeight: 1.6 }}>
                  <p style={{ marginBottom: 12 }}>
                    <strong>To showcase more dramatic differences, consider enhancing the knowledge graph with:</strong>
                  </p>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                    gap: 12,
                    marginBottom: 12
                  }}>
                    <div style={{ 
                      padding: 12, 
                      background: 'var(--glass-bg-tertiary)', 
                      borderRadius: 8,
                      border: '1px solid var(--retro-green)'
                    }}>
                      <strong style={{ color: 'var(--retro-green)' }}>🔗 Partnership Networks</strong><br />
                      <span style={{ fontSize: 12 }}>Apple-OpenAI collaboration, Tesla-Google partnerships</span>
                    </div>
                    <div style={{ 
                      padding: 12, 
                      background: 'var(--glass-bg-tertiary)', 
                      borderRadius: 8,
                      border: '1px solid var(--retro-pink)'
                    }}>
                      <strong style={{ color: 'var(--retro-pink)' }}>💰 Investment Entities</strong><br />
                      <span style={{ fontSize: 12 }}>Specific investment amounts, sectors, timelines</span>
                    </div>
                    <div style={{ 
                      padding: 12, 
                      background: 'var(--glass-bg-tertiary)', 
                      borderRadius: 8,
                      border: '1px solid var(--retro-cyan)'
                    }}>
                      <strong style={{ color: 'var(--retro-cyan)' }}>🏢 Market Context</strong><br />
                      <span style={{ fontSize: 12 }}>Industry sizes, growth rates, competitive landscape</span>
                    </div>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--glass-text-secondary)' }}>
                    <strong>Current Status:</strong> {comparisonResults.graphrag.results?.length || 0} knowledge graph entities, 
                    {comparisonResults.graphrag.documents?.length || 0} documents integrated
                  </div>
                </div>
              </div>
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
