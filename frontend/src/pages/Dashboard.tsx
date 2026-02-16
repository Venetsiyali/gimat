import React, { useState, useEffect } from 'react';
import { dataAPI, ontologyAPI } from '../services/api';
import './Dashboard.css';

interface Station {
    station_id: string;
    station_name: string;
    river_name: string;
    latitude: number;
    longitude: number;
}

interface LatestData {
    timestamp: string;
    discharge: number;
    water_level: number;
    temperature: number;
}

const Dashboard: React.FC = () => {
    const [stations, setStations] = useState<Station[]>([]);
    const [selectedStation, setSelectedStation] = useState<string>('');
    const [latestData, setLatestData] = useState<LatestData | null>(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        loadStations();
    }, []);

    useEffect(() => {
        if (selectedStation) {
            loadLatestData();
            loadStatistics();
        }
    }, [selectedStation]);

    const loadStations = async () => {
        try {
            const response = await dataAPI.getStations();
            setStations(response.data);
            if (response.data.length > 0) {
                setSelectedStation(response.data[0].station_id);
            }
            setLoading(false);
        } catch (error) {
            console.error('Error loading stations:', error);
            setLoading(false);
        }
    };

    const loadLatestData = async () => {
        try {
            const response = await dataAPI.getLatestObservation(selectedStation);
            setLatestData(response.data);
        } catch (error) {
            console.error('Error loading latest data:', error);
        }
    };

    const loadStatistics = async () => {
        try {
            const response = await dataAPI.getStatistics(selectedStation);
            setStats(response.data);
        } catch (error) {
            console.error('Error loading statistics:', error);
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
                <h2 className="text-3xl font-bold mb-2">Dashboard</h2>
                <p className="text-gray-600">Real-time gidrologik monitoring</p>
            </div>

            {/* Station Selector */}
            <div className="card mb-6">
                <label className="block text-sm font-medium mb-2">Gidropost tanlang:</label>
                <select
                    className="w-full md:w-64 p-2 border rounded-lg"
                    value={selectedStation}
                    onChange={(e) => setSelectedStation(e.target.value)}
                >
                    {stations.map((station) => (
                        <option key={station.station_id} value={station.station_id}>
                            {station.station_name} ({station.river_name})
                        </option>
                    ))}
                </select>
            </div>

            {/* Latest Data Cards */}
            {latestData && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="card">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Suv sathi</h3>
                        <p className="text-3xl font-bold text-blue-600">
                            {latestData.water_level?.toFixed(2) || 'N/A'} m
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                            {new Date(latestData.timestamp).toLocaleString('uz-UZ')}
                        </p>
                    </div>

                    <div className="card">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Suv sarfi</h3>
                        <p className="text-3xl font-bold text-green-600">
                            {latestData.discharge?.toFixed(1) || 'N/A'} m³/s
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                            {new Date(latestData.timestamp).toLocaleString('uz-UZ')}
                        </p>
                    </div>

                    <div className="card">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Harorat</h3>
                        <p className="text-3xl font-bold text-orange-600">
                            {latestData.temperature?.toFixed(1) || 'N/A'} °C
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                            {new Date(latestData.timestamp).toLocaleString('uz-UZ')}
                        </p>
                    </div>
                </div>
            )}

            {/* Statistics */}
            {stats && stats.discharge && (
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">Statistika (Yillik)</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-gray-500">O'rtacha sarfi</p>
                            <p className="text-xl font-semibold">{stats.discharge.mean?.toFixed(1)} m³/s</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Minimal sarfi</p>
                            <p className="text-xl font-semibold">{stats.discharge.min?.toFixed(1)} m³/s</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Maksimal sarfi</p>
                            <p className="text-xl font-semibold">{stats.discharge.max?.toFixed(1)} m³/s</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Standart og'ish</p>
                            <p className="text-xl font-semibold">{stats.discharge.std?.toFixed(1)} m³/s</p>
                        </div>
                    </div>
                </div>
            )}

            {/* System Info */}
            <div className="mt-8 card bg-gradient-to-r from-blue-50 to-green-50">
                <h3 className="text-lg font-bold mb-2">🚀 GIMAT Tizimi</h3>
                <p className="text-sm text-gray-600">
                    Gidrologik Intellektual Monitoring va Axborot Tizimi — gibrid AI modellar asosida
                    vaqt qatorlarini tahlil qilish va prognozlash platformasi.
                </p>
                <div className="mt-4 flex space-x-4 text-xs">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Wavelet-tahlil</span>
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">SARIMA</span>
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">Bi-LSTM</span>
                    <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded">GNN</span>
                    <span className="bg-pink-100 text-pink-800 px-2 py-1 rounded">XAI</span>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
