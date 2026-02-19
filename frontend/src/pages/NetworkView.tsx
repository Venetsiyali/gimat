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
    type: string; // 'hydropost' | 'river'
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

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
    const isHorizontal = direction === 'LR';
    dagreGraph.setGraph({ rankdir: direction });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: 180, height: 80 }); // Assumed node size
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    nodes.forEach((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = isHorizontal ? Position.Left : Position.Top;
        node.sourcePosition = isHorizontal ? Position.Right : Position.Bottom;
        // Adjust position to center it slightly better
        node.position = {
            x: nodeWithPosition.x - 90,
            y: nodeWithPosition.y - 40,
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

    // RAG Explorer State
    const [selectedNode, setSelectedNode] = useState<any>(null);
    const [ragLoading, setRagLoading] = useState(false);
    const [relatedNodes, setRelatedNodes] = useState<any[]>([]);

    useEffect(() => {
        loadNetwork();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedRiver]);

    const loadNetwork = async () => {
        try {
            setLoading(true);
            const response = await ontologyAPI.getNetwork(selectedRiver);
            const apiData = response.data;

            // Transform API data to React Flow format
            const initialNodes: Node[] = apiData.nodes.map((n: NetworkNode) => ({
                id: n.id,
                type: 'default', // Using default for now, can be custom
                data: { label: n.label, ...n.data },
                position: { x: 0, y: 0 }, // Layout will set this
                style: {
                    background: '#1E293B',
                    color: '#FFF',
                    border: '1px solid #3B82F6',
                    borderRadius: '8px',
                    padding: '10px',
                    width: 180,
                    fontSize: '12px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                },
            }));

            const initialEdges: Edge[] = apiData.edges.map((e: NetworkEdge, i: number) => ({
                id: `e${i}`,
                source: e.source,
                target: e.target,
                type: 'smoothstep',
                animated: true,
                label: e.label || 'FLOWS_TO',
                style: { stroke: '#3B82F6', strokeWidth: 2 },
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3B82F6' },
                labelStyle: { fill: '#94A3B8', fontSize: 10 }
            }));

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                initialNodes,
                initialEdges,
                'TB' // Top-to-Bottom flow
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
            setLoading(false);
        } catch (error) {
            console.error('Error loading network:', error);
            setLoading(false);
        }
    };

    const onNodeClick = useCallback(async (_event: React.MouseEvent, node: Node) => {
        setSelectedNode(node);
        setRagLoading(true);
        try {
            // Mocking semantic relationship fetch for now (would use ontologyAPI in real scenario)
            // In a real implementation, you might call: await ontologyAPI.getRelated(node.id)

            // Simulating fetch delay
            setTimeout(() => {
                // Here we would filter the original graph data or fetch from backend
                // For this demo, let's just show some static "intelligent" insights
                setRelatedNodes([
                    { relation: 'UPSTREAM', target: 'Chorvoq suv ombori', distance: '12 km' },
                    { relation: 'DOWNSTREAM', target: 'G\'azalkent GES', distance: '8 km' },
                    { relation: 'INFLUENCES', target: 'Sug\'orish tizimi', impact: 'High' }
                ]);
                setRagLoading(false);
            }, 500);

        } catch (error) {
            console.error(error);
            setRagLoading(false);
        }
    }, []);

    // Layout style for the scientific look
    const pageStyle: React.CSSProperties = {
        background: '#0F172A',
        minHeight: 'calc(100vh - 64px)',
        color: '#E2E8F0',
        display: 'flex',
        flexDirection: 'column'
    };

    return (
        <div style={pageStyle}>
            {/* Header */}
            <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-900">
                <div>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">
                        Gidrologik Topologiya va Semantik Bog‘liqliklar
                    </h1>
                    <p className="text-xs text-slate-400">Iyerarxik Oqim Sxemasi (Flow Schema)</p>
                </div>
                <div className="flex items-center gap-4">
                    <select
                        className="bg-slate-800 border border-slate-600 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                        value={selectedRiver}
                        onChange={(e) => setSelectedRiver(e.target.value)}
                    >
                        <option value="Chirchiq">Chirchiq Daryosi</option>
                        <option value="Zarafshon">Zarafshon Daryosi</option>
                    </select>
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden relative">
                {/* Main: Flow Schema */}
                <div className="flex-1 relative border-r border-slate-700">
                    {loading ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                        </div>
                    ) : (
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            onNodeClick={onNodeClick}
                            connectionLineType={ConnectionLineType.SmoothStep}
                            fitView
                            attributionPosition="bottom-left"
                            nodesDraggable={false} // Lock structure for scientific view
                        >
                            <Controls style={{ fill: '#fff' }} />
                            <Background color="#334155" gap={16} />
                        </ReactFlow>
                    )}
                    <div className="absolute top-4 left-4 bg-slate-800/80 backdrop-blur-sm p-3 rounded border border-slate-600 z-10">
                        <div className="flex items-center gap-2 mb-1">
                            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                            <span className="text-xs text-slate-300">Gidropost</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-0.5 bg-blue-500"></div>
                            <span className="text-xs text-slate-300">Suv Oqimi</span>
                        </div>
                    </div>
                </div>

                {/* Right: RAG Explorer */}
                <div className="w-96 bg-slate-900 border-l border-slate-800 flex flex-col shadow-2xl z-20">
                    <div className="p-4 border-b border-slate-800 bg-slate-800/50">
                        <h2 className="font-bold text-blue-400 flex items-center gap-2">
                            <span>🧠</span> Intellektual Explorer
                        </h2>
                        <p className="text-xs text-slate-500 mt-1">Semantik qidiruv va kontekst</p>
                    </div>

                    <div className="p-4 flex-1 overflow-y-auto">
                        {!selectedNode ? (
                            <div className="text-center py-10 text-slate-500">
                                <p className="mb-2">Biror tugunni (stansiya) tanlang</p>
                                <p className="text-xs">Ontologik bog‘liqliklarni ko‘rish uchun sxemadagi obyekt ustiga bosing.</p>
                            </div>
                        ) : (
                            <div className="animate-fade-in">
                                <div className="mb-6">
                                    <h3 className="text-lg font-bold text-white mb-1">{selectedNode.data.label}</h3>
                                    <span className="px-2 py-0.5 rounded text-xs bg-blue-900 text-blue-200 border border-blue-700">
                                        ID: {selectedNode.id}
                                    </span>
                                </div>

                                {/* Live Data Placeholder */}
                                <div className="bg-slate-800 rounded-lg p-3 mb-6 border border-slate-700">
                                    <h4 className="text-xs font-semibold text-slate-400 uppercase mb-3">Joriy Ko'rsatkichlar</h4>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-xs text-slate-500">Suv Sathi (H)</p>
                                            <p className="text-lg font-mono text-cyan-400">2.45 <span className="text-xs">m</span></p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-slate-500">Suv Sarfi (Q)</p>
                                            <p className="text-lg font-mono text-cyan-400">145.2 <span className="text-xs">m³/s</span></p>
                                        </div>
                                    </div>
                                </div>

                                {/* RAG Insights (Semantic Graph) */}
                                <div>
                                    <h4 className="text-xs font-semibold text-slate-400 uppercase mb-3 flex justify-between">
                                        <span>Qo'shni Tugunlar (Graph)</span>
                                        {ragLoading && <span className="animate-pulse">Yuklanmoqda...</span>}
                                    </h4>

                                    <div className="space-y-2">
                                        {relatedNodes.map((rel, idx) => (
                                            <div key={idx} className="bg-slate-800/40 p-3 rounded border border-slate-700 hover:border-slate-500 transition-colors cursor-pointer group">
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded 
                                                        ${rel.relation === 'UPSTREAM' ? 'bg-indigo-900/50 text-indigo-300' :
                                                            rel.relation === 'DOWNSTREAM' ? 'bg-emerald-900/50 text-emerald-300' : 'bg-slate-700 text-slate-300'}`}>
                                                        {rel.relation}
                                                    </span>
                                                    <span className="text-xs text-slate-500 font-mono">{rel.distance || rel.impact}</span>
                                                </div>
                                                <div className="text-sm font-medium text-slate-200 group-hover:text-blue-400 transition-colors">
                                                    {rel.target}
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="mt-6 p-3 bg-blue-900/20 border border-blue-800/50 rounded">
                                        <p className="text-xs text-blue-200 italic">
                                            "Bu stansiya Chirchiq daryosining o'rta oqimida joylashgan bo'lib, G'azalkent suv omboriga to'g'ridan-to'g'ri bog'liq."
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NetworkView;
