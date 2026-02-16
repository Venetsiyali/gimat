import React, { useState, useEffect } from 'react';
import { ontology API } from '../services/api';
import './NetworkView.css';

const NetworkView: React.FC = () => {
    const [networkData, setNetworkData] = useState<any>(null);
    const [selectedRiver, setSelectedRiver] = useState<string>('Chirchiq');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadNetwork();
    }, [selectedRiver]);

    const loadNetwork = async () => {
        try {
            setLoading(true);
            const response = await ontologyAPI.getNetwork(selectedRiver);
            setNetworkData(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error loading network:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4">
            <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">Daryo Tarmog'i</h2>
                <p className="text-gray-600">Graf ontologiyasi va topologiya</p>
            </div>

            {/* River Selector */}
            <div className="card mb-6">
                <label className="block text-sm font-medium mb-2">Daryo tanlang:</label>
                <select
                    className="w-full md:w-64 p-2 border rounded-lg"
                    value={selectedRiver}
                    onChange={(e) => setSelectedRiver(e.target.value)}
                >
                    <option value="Chirchiq">Chirchiq</option>
                    <option value="Zarafshon">Zarafshon</option>
                </select>
            </div>

            {/* Network Stats */}
            {networkData && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="card">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Tugunlar</h3>
                        <p className="text-3xl font-bold text-blue-600">{networkData.node_count}</p>
                    </div>

                    <div className="card">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Bog'lanishlar</h3>
                        <p className="text-3xl font-bold text-green-600">{networkData.edge_count}</p>
                    </div>

                    <div className="card">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Daryo nomi</h3>
                        <p className="text-xl font-bold text-purple-600">{networkData.river_name}</p>
                    </div>
                </div>
            )}

            {/* Network Visualization Placeholder */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">Graf Vizualizatsiya</h3>
                <div className="network-viz-container">
                    <div className="text-center py-16">
                        <p className="text-gray-500 mb-4">🌊 Daryo tarmog'i grafigi</p>
                        <p className="text-sm text-gray-400">
                            Graf vizualizatsiya uchun react-force-graph kutubxonasi ishlatiladi
                        </p>
                        {networkData && (
                            <div className="mt-4 text-xs">
                                <p>Nodes: {networkData.nodes?.length || 0}</p>
                                <p>Edges: {networkData.edges?.length || 0}</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Neo4j Info */}
            <div className="mt-8 card bg-gradient-to-r from-purple-50 to-blue-50">
                <h3 className="text-lg font-bold mb-2">📊 Graf Bazasi</h3>
                <p className="text-sm text-gray-600">
                    Neo4j graf bazasida daryo havzalarining to'liq topologik modeli saqlanadi.
                    Gidropostlar, suv omborlari va daryo uchastkalarining o'zaro bog'liqligini
                    FLOWS_TO, MONITORS va INFLUENCES munosabatlari orqali ifodalanadi.
                </p>
            </div>
        </div>
    );
};

export default NetworkView;
