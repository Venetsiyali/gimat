import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
    Node,
    Edge,
    ConnectionLineType,
    useNodesState,
    useEdgesState,
    MarkerType,
    Controls,
    Background,
    Position
} from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';
import { ontologyAPI } from '../services/api';

// --- Types ---
interface NetworkNode {
    id: string;
    label: string;
    type: string;
    data: any;
}

interface NetworkEdge {
    source: string;
    target: string;
    label?: string;
}

// --- Dagre Layout Helper ---
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'LR') => {
    const isHorizontal = direction === 'LR';
    dagreGraph.setGraph({ rankdir: direction });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: 180, height: 60 });
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    nodes.forEach((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = isHorizontal ? Position.Left : Position.Top;
        node.sourcePosition = isHorizontal ? Position.Right : Position.Bottom;
        node.position = {
            x: nodeWithPosition.x - 90,
            y: nodeWithPosition.y - 30,
        };
    });

    return { nodes, edges };
};

// --- Main Component ---
const NetworkView: React.FC = () => {
    const [selectedRiver, setSelectedRiver] = useState<string>('Chirchiq');
    const [loading, setLoading] = useState(true);

    // React Flow State
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    // Sidebar State
    const [selectedNode, setSelectedNode] = useState<any>(null);

    useEffect(() => {
        loadNetwork();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedRiver]);

    const loadNetwork = async () => {
        try {
            setLoading(true);
            const response = await ontologyAPI.getNetwork(selectedRiver);
            const apiData = response.data;

            // Transform API data to React Flow
            // Styling for "Neon-Cyan" scientific look
            const initialNodes: Node[] = apiData.nodes.map((n: NetworkNode) => ({
                id: n.id,
                type: 'default',
                data: { label: n.label, ...n.data },
                position: { x: 0, y: 0 },
                style: {
                    background: '#0F172A', // Slate 900
                    color: '#22D3EE',      // Cyan 400
                    border: '1px solid #06B6D4', // Cyan 500
                    borderRadius: '8px',
                    padding: '12px',
                    width: 180,
                    fontSize: '13px',
                    fontWeight: 600,
                    boxShadow: '0 0 10px rgba(34, 211, 238, 0.2)',
                    textAlign: 'center'
                },
            }));

            const initialEdges: Edge[] = apiData.edges.map((e: NetworkEdge, i: number) => ({
                id: `e${i}`,
                source: e.source,
                target: e.target,
                type: 'smoothstep',
                animated: true,
                label: e.label || 'Oqim',
                style: { stroke: '#22D3EE', strokeWidth: 2 },
                labelStyle: { fill: '#94A3B8', fontSize: 11 },
                markerEnd: { type: MarkerType.ArrowClosed, color: '#22D3EE' },
            }));

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                initialNodes,
                initialEdges,
                'TB' // Top-to-Bottom hierarchy
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
            setLoading(false);

            // Generate overview stats for default selection
            setSelectedNode(null);

        } catch (error) {
            console.error('Error loading network:', error);
            setLoading(false);
        }
    };

    const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
        setSelectedNode(node);
    }, []);

    // Layout scientific dark theme
    const pageStyle: React.CSSProperties = {
        background: '#020617', // Very dark slate
        height: 'calc(100vh - 64px)',
        color: '#E2E8F0',
        display: 'flex',
        flexDirection: 'row', // Left Sidebar, Right Map
        overflow: 'hidden'
    };

    return (
        <div style={pageStyle}>
            {/* --- LEFT SIDEBAR (25%) --- */}
            <div className="w-1/4 h-full border-r border-slate-800 bg-slate-900/95 flex flex-col z-20 shadow-xl">
                {/* Sidebar Header */}
                <div className="p-5 border-b border-slate-800">
                    <h2 className="text-lg font-bold text-cyan-400 flex items-center gap-2 mb-1">
                        <span>🧠</span> Intellektual Explorer
                    </h2>
                    <p className="text-xs text-slate-500">Gidrologik obyektlar tahlili</p>
                </div>

                {/* River Selector */}
                <div className="p-5 border-b border-slate-800">
                    <label className="text-xs font-semibold text-slate-400 uppercase mb-2 block">Daryo Havzasi</label>
                    <select
                        className="w-full bg-slate-800 border border-slate-700 text-cyan-300 text-sm rounded-md p-2.5 focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                        value={selectedRiver}
                        onChange={(e) => setSelectedRiver(e.target.value)}
                    >
                        <option value="">Daryo tanlang...</option>
                        <option value="Chirchiq">Chirchiq Daryosi</option>
                        <option value="Zarafshon">Zarafshon Daryosi</option>
                    </select>
                </div>

                {/* Sidebar Content */}
                <div className="flex-1 overflow-y-auto p-5">
                    {!selectedNode ? (
                        <div className="text-center py-10 opacity-60">
                            <div className="text-4xl mb-3">📍</div>
                            <p className="text-sm text-slate-400">Sxemadan biror stansiyani tanlang</p>
                            <p className="text-xs text-slate-600 mt-2">Daryo oqimi bo'ylab joylashgan tugunlar ustiga bosing.</p>
                        </div>
                    ) : (
                        <div className="animate-fade-in space-y-6">
                            {/* Card: Station Info */}
                            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 shadow-lg backdrop-blur-sm relative overflow-hidden group">
                                <div className="absolute top-0 left-0 w-1 h-full bg-cyan-500"></div>
                                <h3 className="text-xl font-bold text-white mb-1">{selectedNode.data.label}</h3>
                                <div className="flex items-center gap-2 text-xs text-cyan-300 font-mono mb-3">
                                    <span>ID: {selectedNode.id}</span>
                                    <span>•</span>
                                    <span>{selectedRiver}</span>
                                </div>
                                <div className="grid grid-cols-2 gap-3 mt-4">
                                    <div className="bg-slate-900/80 p-2 rounded border border-slate-700/50">
                                        <span className="text-[10px] text-slate-500 uppercase block">Lat</span>
                                        <span className="text-sm font-mono text-slate-200">41.6523</span>
                                    </div>
                                    <div className="bg-slate-900/80 p-2 rounded border border-slate-700/50">
                                        <span className="text-[10px] text-slate-500 uppercase block">Long</span>
                                        <span className="text-sm font-mono text-slate-200">69.8401</span>
                                    </div>
                                </div>
                            </div>

                            {/* Card: Live Stats */}
                            <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-4">
                                <h4 className="text-xs font-bold text-slate-400 uppercase mb-3 flex items-center gap-2">
                                    <span>📊</span> Statistika
                                </h4>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center pb-2 border-b border-slate-800/50">
                                        <span className="text-sm text-slate-400">Suv Sathi (H)</span>
                                        <span className="text-base font-bold text-cyan-400">2.45 m</span>
                                    </div>
                                    <div className="flex justify-between items-center pb-2 border-b border-slate-800/50">
                                        <span className="text-sm text-slate-400">Suv Sarfi (Q)</span>
                                        <span className="text-base font-bold text-blue-400">145 m³/s</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-slate-400">Harorat (T)</span>
                                        <span className="text-base font-bold text-yellow-500">14.2 °C</span>
                                    </div>
                                </div>
                            </div>

                            {/* Card: Semantic Info */}
                            <div className="p-3 bg-cyan-900/10 border border-cyan-800/30 rounded-lg">
                                <p className="text-xs text-cyan-200/80 italic leading-relaxed">
                                    "Ushbu gidropost <strong>{selectedRiver}</strong> havzasining yuqori qismida joylashgan bo'lib, quyi oqimdagi suv omborlariga bevosita ta'sir ko'rsatadi."
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer Info */}
                <div className="p-4 border-t border-slate-800 text-[10px] text-slate-600 text-center">
                    Gidrologik Monitoring Tizimi v2.0
                </div>
            </div>

            {/* --- RIGHT MAIN AREA (75%) --- */}
            <div className="w-3/4 h-full relative bg-slate-950 flex flex-col">
                {/* Map overlay header */}
                <div className="absolute top-4 left-4 z-10">
                    <h1 className="text-2xl font-bold text-white tracking-tight">
                        Gidrologik Oqim Sxemasi
                    </h1>
                    <p className="text-sm text-slate-400 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                        Real vaqt rejimida
                    </p>
                </div>

                {/* Legend */}
                <div className="absolute bottom-6 right-6 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-lg">
                    <div className="flex items-center gap-3 text-xs text-slate-300">
                        <div className="flex items-center gap-1.5">
                            <div className="w-3 h-3 rounded bg-slate-900 border border-cyan-500"></div>
                            <span>Gidropost</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <div className="w-6 h-0.5 bg-cyan-500"></div>
                            <span>Oqim</span>
                        </div>
                    </div>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                            <span className="text-sm text-cyan-500 font-mono">Ma'lumotlar yuklanmoqda...</span>
                        </div>
                    </div>
                ) : !selectedRiver ? (
                    <div className="flex-1 flex items-center justify-center text-slate-500">
                        <div className="text-center">
                            <h3 className="text-xl font-medium text-slate-400 mb-2">Daryo tanlanmagan</h3>
                            <p className="text-sm">Iltimos, chap paneldan daryo havzasini tanlang.</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 w-full h-full min-h-[600px]">
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            onNodeClick={onNodeClick}
                            connectionLineType={ConnectionLineType.SmoothStep}
                            fitView
                            attributionPosition="bottom-right"
                            nodesDraggable={false}
                        >
                            <Controls
                                style={{ background: '#1E293B', border: '1px solid #334155', fill: '#CBD5E1' }}
                                showInteractive={false}
                            />
                            <Background color="#1E293B" gap={20} size={1} />
                        </ReactFlow>
                    </div>
                )}
            </div>
        </div>
    );
};

export default NetworkView;
