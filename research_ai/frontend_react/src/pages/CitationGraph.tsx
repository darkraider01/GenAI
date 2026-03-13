import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState, BackgroundVariant } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Network, Search, Loader2 } from 'lucide-react';

export default function CitationGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchGraph = async () => {
    try {
      setLoading(true);
      const res = await axios.get('http://localhost:8000/api/citation-graph');
      
      // Inject random positions since we are not running a full d3 force layout algorithm locally
      // In a production app you'd run d3-force or elk.js
      const rawNodes = res.data.nodes || [];
      const placedNodes = rawNodes.map((n: any, i: number) => ({
        ...n,
        position: {
          x: Math.random() * 800 - 400,
          y: Math.random() * 800 - 400
        },
        style: {
          background: 'rgba(30, 41, 59, 0.9)',
          color: 'white',
          border: '1px solid rgba(59, 130, 246, 0.5)',
          borderRadius: '8px',
          padding: '10px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          width: 180,
          fontSize: '12px'
        }
      }));
      
      const rawEdges = res.data.edges || [];
      const placedEdges = rawEdges.map((e: any) => ({
        ...e,
        style: { stroke: 'rgba(148, 163, 184, 0.4)', strokeWidth: 2 }
      }));
      
      setNodes(placedNodes);
      setEdges(placedEdges);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const onNodeClick = useCallback((_: any, node: any) => {
    setSelectedNode(node);
  }, []);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: 0 }}>
          <Network color="#a855f7" size={32} />
          Interactive Citation Graph
        </h1>
        <button className="btn" onClick={fetchGraph} style={{ background: 'rgba(255,255,255,0.1)' }}>
          Refresh Network
        </button>
      </div>
      
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
        Explore the spatial topological relationships between the ingested scientific corpus based on reference links.
      </p>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '600px', background: 'var(--bg-card)', borderRadius: '16px' }}>
          <Loader2 className="animate-spin" size={48} color="var(--accent)" />
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: selectedNode ? '3fr 1fr' : '1fr', gap: '2rem', transition: 'all 0.3s ease' }}>
          <div className="react-flow__container">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
              attributionPosition="bottom-right"
              minZoom={0.1}
            >
              <Background color="#334155" variant={BackgroundVariant.Dots} />
              <Controls style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }} />
              <MiniMap 
                nodeColor={(n) => '#3b82f6'} 
                maskColor="rgba(15, 23, 42, 0.8)" 
                style={{ background: 'rgba(30, 41, 59, 0.9)', border: '1px solid rgba(255,255,255,0.1)' }} 
              />
            </ReactFlow>
          </div>
          
          {selectedNode && (
            <div className="details-panel slide-in">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                 <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', lineHeight: 1.4 }}>{selectedNode.data?.full_title || "Unknown Paper"}</h3>
                 <button 
                   onClick={() => setSelectedNode(null)} 
                   style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.5rem', lineHeight: 1 }}
                 >
                   &times;
                 </button>
              </div>
              
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Node ID</div>
                <div style={{ fontFamily: 'monospace', color: '#c0caf5' }}>{selectedNode.id}</div>
              </div>
              
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Cluster Horizon</div>
                <div style={{ color: '#34d399', fontWeight: 500 }}>{selectedNode.data?.topic_cluster || "Unclustered"}</div>
              </div>
              
              <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <button className="btn" style={{ width: '100%', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' }}>
                  <Search size={16} /> Open Full Context
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
