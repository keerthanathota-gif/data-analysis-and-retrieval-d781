import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const NetworkGraph = ({ nodes, edges, onNodeClick, width, height }) => {
  const graphRef = useRef();
  const [hoveredNode, setHoveredNode] = useState(null);

  // Transform data for react-force-graph
  const graphData = {
    nodes: nodes.map(node => ({
      id: node.id,
      label: node.label,
      subject: node.subject,
      citations_in: node.citations_in,
      citations_out: node.citations_out,
      pagerank: node.pagerank,
      importance: node.importance,
      text_preview: node.text_preview,
      val: Math.max(5, node.importance * 2) // Node size based on importance
    })),
    links: edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      type: edge.type,
      strength: edge.strength,
      color: edge.color
    }))
  };

  useEffect(() => {
    // Fit graph to viewport after data loads
    if (graphRef.current && graphData.nodes.length > 0) {
      graphRef.current.zoomToFit(400, 50);
    }
  }, [graphData.nodes.length]);

  // Node color based on importance
  const getNodeColor = (node) => {
    const importance = node.importance || 0;
    if (importance > 50) return '#dc2626'; // Red - very important
    if (importance > 30) return '#f59e0b'; // Orange - important
    if (importance > 15) return '#3b82f6'; // Blue - moderate
    return '#6b7280'; // Gray - low
  };

  // Custom node canvas rendering
  const paintNode = (node, ctx, globalScale) => {
    const label = node.label;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    
    // Draw node circle
    const radius = Math.sqrt(node.val) * 2;
    ctx.fillStyle = getNodeColor(node);
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
    ctx.fill();
    
    // Draw border
    ctx.strokeStyle = node === hoveredNode ? '#ffffff' : '#ffffff';
    ctx.lineWidth = node === hoveredNode ? 2.5 : 1.5;
    ctx.stroke();
    
    // Draw label if zoomed in enough
    if (globalScale > 1.5) {
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#1f2937';
      ctx.fillText(label, node.x, node.y + radius + 8);
    }
  };

  // Link rendering
  const paintLink = (link, ctx, globalScale) => {
    const start = link.source;
    const end = link.target;
    
    if (typeof start !== 'object' || typeof end !== 'object') return;
    
    // Draw link
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = link.color || '#6b7280';
    ctx.lineWidth = link.type === 'citation' ? 2 : 1;
    ctx.globalAlpha = 0.6;
    ctx.stroke();
    ctx.globalAlpha = 1;
  };

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      background: '#f9fafb',
      borderRadius: '8px',
      overflow: 'hidden',
      position: 'relative'
    }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={width || 1200}
        height={height || 800}
        nodeLabel={node => `
          <div style="
            background: white;
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 300px;
            font-family: Arial, sans-serif;
          ">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #1f2937;">
              ${node.label}
            </div>
            <div style="font-size: 12px; margin-bottom: 6px; color: #4b5563;">
              ${node.subject}
            </div>
            <div style="font-size: 11px; color: #6b7280; border-top: 1px solid #e5e7eb; padding-top: 6px; margin-top: 6px;">
              <div><strong>Citations In:</strong> ${node.citations_in}</div>
              <div><strong>Citations Out:</strong> ${node.citations_out}</div>
              <div><strong>PageRank:</strong> ${node.pagerank?.toFixed(6) || '0'}</div>
              <div><strong>Importance:</strong> ${node.importance?.toFixed(2) || '0'}</div>
            </div>
          </div>
        `}
        nodeCanvasObject={paintNode}
        nodeCanvasObjectMode={() => 'replace'}
        linkCanvasObject={paintLink}
        linkCanvasObjectMode={() => 'replace'}
        onNodeClick={onNodeClick}
        onNodeHover={node => setHoveredNode(node)}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.1}
        cooldownTicks={100}
        onEngineStop={() => graphRef.current?.zoomToFit(400, 50)}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
      />
      
      {/* Legend */}
      <div style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        background: 'white',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        fontSize: '12px',
        maxWidth: '200px'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '10px', fontSize: '14px' }}>
          Legend
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontWeight: '600', marginBottom: '5px' }}>Node Colors:</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#dc2626' }}></div>
            <span>Very Important</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b' }}></div>
            <span>Important</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#3b82f6' }}></div>
            <span>Moderate</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#6b7280' }}></div>
            <span>Low</span>
          </div>
        </div>
        
        <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '10px', marginTop: '10px' }}>
          <div style={{ fontWeight: '600', marginBottom: '5px' }}>Edge Types:</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <div style={{ width: '20px', height: '2px', background: '#ef4444' }}></div>
            <span>Citation</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <div style={{ width: '20px', height: '2px', background: '#dc2626' }}></div>
            <span>Very Similar</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <div style={{ width: '20px', height: '2px', background: '#f59e0b' }}></div>
            <span>Similar</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '20px', height: '2px', background: '#3b82f6' }}></div>
            <span>Related</span>
          </div>
        </div>
      </div>
      
      {/* Controls Info */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '20px',
        background: 'white',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        fontSize: '11px',
        color: '#6b7280'
      }}>
        <div><strong>Controls:</strong></div>
        <div>• Drag to pan</div>
        <div>• Scroll to zoom</div>
        <div>• Click node for details</div>
        <div>• Hover for info</div>
      </div>
    </div>
  );
};

export default NetworkGraph;
