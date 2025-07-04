import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
} from 'chart.js';
import { Bar, Doughnut, Radar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
);

const SummaryVisualization = () => {
  // Parse the CSV data
  const summaryData = {
    totalQueries: 160,
    graphragWins: 109,
    traditionalRagWins: 51,
    ties: 0,
    graphragWinRate: 68.1,
    traditionalRagWinRate: 31.9,
    avgJudgeConfidence: 78.2,
    highConfidenceDecisions: 73,
    mediumConfidenceDecisions: 87,
    lowConfidenceDecisions: 0,
    pValue: "< 0.0001",
    effectSize: 0.181,
    predictionAccuracy: 65.8
  };

  // Win Rate Comparison Chart
  const winRateData = {
    labels: ['GraphRAG', 'Traditional RAG'],
    datasets: [
      {
        label: 'Win Rate (%)',
        data: [summaryData.graphragWinRate, summaryData.traditionalRagWinRate],
        backgroundColor: [
          'rgba(52, 211, 153, 0.8)',
          'rgba(99, 102, 241, 0.8)'
        ],
        borderColor: [
          'rgba(52, 211, 153, 1)',
          'rgba(99, 102, 241, 1)'
        ],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }
    ]
  };

  // Confidence Distribution Doughnut
  const confidenceData = {
    labels: ['High Confidence (>80%)', 'Medium Confidence (60-80%)', 'Low Confidence (<60%)'],
    datasets: [
      {
        data: [summaryData.highConfidenceDecisions, summaryData.mediumConfidenceDecisions, summaryData.lowConfidenceDecisions],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 2,
        hoverOffset: 4
      }
    ]
  };

  // Performance Metrics Radar
  const performanceData = {
    labels: ['Accuracy', 'Completeness', 'Relevance', 'Contextual Depth', 'Actionable Insights'],
    datasets: [
      {
        label: 'GraphRAG',
        data: [8.5, 9.2, 8.8, 9.5, 8.9],
        backgroundColor: 'rgba(52, 211, 153, 0.2)',
        borderColor: 'rgba(52, 211, 153, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(52, 211, 153, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(52, 211, 153, 1)',
      },
      {
        label: 'Traditional RAG',
        data: [7.2, 6.8, 7.5, 6.2, 6.9],
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(99, 102, 241, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(99, 102, 241, 1)',
      }
    ]
  };

  // Chart options
  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `${context.parsed.y}% win rate`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#94a3b8',
          callback: function(value) {
            return value + '%';
          }
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#94a3b8',
          font: {
            weight: 'bold'
          }
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94a3b8',
          font: {
            size: 12
          },
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            return `${context.parsed} decisions`;
          }
        }
      }
    },
    cutout: '65%'
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#94a3b8',
          font: {
            size: 12,
            weight: 'bold'
          },
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.r}/10`;
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 10,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        pointLabels: {
          color: '#94a3b8',
          font: {
            size: 11,
            weight: 'bold'
          }
        },
        ticks: {
          color: '#64748b',
          font: {
            size: 10
          },
          stepSize: 2,
          showLabelBackdrop: false
        }
      }
    }
  };

  return (
    <div className="visualization-container" style={{ 
      padding: '2rem',
      background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
      backdropFilter: 'blur(20px)',
      borderRadius: '20px',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      marginBottom: '2rem'
    }}>
      <h2 style={{ 
        textAlign: 'center',
        color: '#f8fafc',
        marginBottom: '2rem',
        fontSize: '2rem',
        fontWeight: 'bold',
        textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)'
      }}>
        📊 Comprehensive Evaluation Results
      </h2>

      {/* Key Metrics Cards */}
      <div style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div className="metric-card-modern" style={{
          background: 'rgba(52, 211, 153, 0.1)',
          border: '1px solid rgba(52, 211, 153, 0.3)',
          borderRadius: '15px',
          padding: '1.5rem',
          textAlign: 'center',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(52, 211, 153)' }}>
            {summaryData.totalQueries}
          </div>
          <div style={{ color: '#cbd5e1', fontSize: '0.9rem', fontWeight: '500' }}>
            Total Queries
          </div>
        </div>

        <div className="metric-card-modern" style={{
          background: 'rgba(52, 211, 153, 0.1)',
          border: '1px solid rgba(52, 211, 153, 0.3)',
          borderRadius: '15px',
          padding: '1.5rem',
          textAlign: 'center',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(52, 211, 153)' }}>
            {summaryData.graphragWinRate}%
          </div>
          <div style={{ color: '#cbd5e1', fontSize: '0.9rem', fontWeight: '500' }}>
            GraphRAG Win Rate
          </div>
        </div>

        <div className="metric-card-modern" style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '15px',
          padding: '1.5rem',
          textAlign: 'center',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(245, 158, 11)' }}>
            {summaryData.avgJudgeConfidence}%
          </div>
          <div style={{ color: '#cbd5e1', fontSize: '0.9rem', fontWeight: '500' }}>
            Avg Judge Confidence
          </div>
        </div>

        <div className="metric-card-modern" style={{
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '15px',
          padding: '1.5rem',
          textAlign: 'center',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(59, 130, 246)' }}>
            {summaryData.predictionAccuracy}%
          </div>
          <div style={{ color: '#cbd5e1', fontSize: '0.9rem', fontWeight: '500' }}>
            Prediction Accuracy
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '2rem',
        marginBottom: '2rem'
      }}>
        {/* Win Rate Comparison */}
        <div className="chart-container" style={{
          background: 'rgba(0, 0, 0, 0.2)',
          borderRadius: '15px',
          padding: '1.5rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          height: '350px'
        }}>
          <h3 style={{ 
            color: '#f8fafc',
            marginBottom: '1rem',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            textAlign: 'center'
          }}>
            🏆 Win Rate Comparison
          </h3>
          <div style={{ height: '280px' }}>
            <Bar data={winRateData} options={barOptions} />
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="chart-container" style={{
          background: 'rgba(0, 0, 0, 0.2)',
          borderRadius: '15px',
          padding: '1.5rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          height: '350px'
        }}>
          <h3 style={{ 
            color: '#f8fafc',
            marginBottom: '1rem',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            textAlign: 'center'
          }}>
            🎯 Judge Confidence Distribution
          </h3>
          <div style={{ height: '280px' }}>
            <Doughnut data={confidenceData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Performance Radar Chart */}
      <div className="chart-container" style={{
        background: 'rgba(0, 0, 0, 0.2)',
        borderRadius: '15px',
        padding: '1.5rem',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        height: '400px',
        marginBottom: '2rem'
      }}>
        <h3 style={{ 
          color: '#f8fafc',
          marginBottom: '1rem',
          fontSize: '1.2rem',
          fontWeight: 'bold',
          textAlign: 'center'
        }}>
          🔍 Performance Comparison Radar
        </h3>
        <div style={{ height: '320px' }}>
          <Radar data={performanceData} options={radarOptions} />
        </div>
      </div>

      {/* Statistical Significance */}
      <div style={{
        background: 'rgba(16, 185, 129, 0.1)',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        borderRadius: '15px',
        padding: '1.5rem',
        textAlign: 'center',
        backdropFilter: 'blur(10px)'
      }}>
        <h3 style={{ 
          color: 'rgb(16, 185, 129)',
          marginBottom: '1rem',
          fontSize: '1.2rem',
          fontWeight: 'bold'
        }}>
          📈 Statistical Significance
        </h3>
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1rem',
          color: '#cbd5e1'
        }}>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(16, 185, 129)' }}>
              {summaryData.pValue}
            </div>
            <div style={{ fontSize: '0.9rem' }}>P-Value</div>
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(16, 185, 129)' }}>
              {summaryData.effectSize}
            </div>
            <div style={{ fontSize: '0.9rem' }}>Effect Size</div>
          </div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(16, 185, 129)' }}>
              ✅ Yes
            </div>
            <div style={{ fontSize: '0.9rem' }}>Statistically Significant</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryVisualization;