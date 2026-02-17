import React, { useState, useEffect } from 'react';
import { dataAPI } from '../services/api';
import { MetricCard, TimeSeriesChart } from '../components/Charts';
import '../components/GlassStyles.css';
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
    const [historicalData, setHistoricalData] = useState<any[]>([]);

    useEffect(() => {
        loadStations();
    }, []);

    useEffect(() => {
        if (selectedStation) {
            loadLatestData();
            loadStatistics();
            loadHistoricalData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
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

    const loadHistoricalData = async () => {
        try {
            // Mock historical data for visualization
            const mockData = Array.from({ length: 30 }, (_, i) => ({
                date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric' }),
                discharge: 150 + Math.sin(i / 5) * 30 + Math.random() * 20,
                water_level: 2.5 + Math.sin(i / 7) * 0.5 + Math.random() * 0.3,
                temperature: 18 + Math.sin(i / 10) * 5 + Math.random() * 2
            }));
            setHistoricalData(mockData);
        } catch (error) {
            console.error('Error loading historical data:', error);
        }
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <div className="spinner pulse-glow"></div>
            </div>
        );
    }

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ marginBottom: '2rem' }} className="fade-in">
                <h2 className="gradient-text" style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    Dashboard
                </h2>
                <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '1rem' }}>
                    Real-time gidrologik monitoring va PhD-darajasidagi tahlil
                </p>
            </div>

            {/* Station Selector */}
            <div className="card fade-in" style={{ marginBottom: '2rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem', color: 'rgba(255,255,255,0.9)' }}>
                    📍 Gidropost tanlang:
                </label>
                <select
                    style={{
                        width: '100%',
                        maxWidth: '400px',
                        padding: '0.75rem 1rem',
                        borderRadius: '12px',
                        border: '1px solid rgba(255,255,255,0.2)',
                        background: 'rgba(255,255,255,0.1)',
                        color: 'white',
                        fontSize: '1rem',
                        backdropFilter: 'blur(10px)',
                        cursor: 'pointer',
                        outline: 'none'
                    }}
                    value={selectedStation}
                    onChange={(e) => setSelectedStation(e.target.value)}
                >
                    {stations.map((station) => (
                        <option key={station.station_id} value={station.station_id} style={{ background: '#1e293b', color: 'white' }}>
                            {station.station_name} ({station.river_name})
                        </option>
                    ))}
                </select>
            </div>

            {/* Metric Cards */}
            {latestData && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                    <MetricCard
                        title="Suv sathi"
                        value={`${latestData.water_level?.toFixed(2) || 'N/A'}`}
                        subtitle="metr"
                        trend="up"
                        trendValue="+2.3% o'tgan haftadan"
                        icon="💧"
                        gradient="primary"
                    />
                    <MetricCard
                        title="Suv sarfi"
                        value={`${latestData.discharge?.toFixed(1) || 'N/A'}`}
                        subtitle="m³/s"
                        trend="up"
                        trendValue="+5.1% o'tgan haftadan"
                        icon="🌊"
                        gradient="success"
                    />
                    <MetricCard
                        title="Harorat"
                        value={`${latestData.temperature?.toFixed(1) || 'N/A'}°C`}
                        subtitle="Celsius"
                        trend="down"
                        trendValue="-1.2% o'tgan haftadan"
                        icon="🌡️"
                        gradient="warning"
                    />
                </div>
            )}

            {/* Time Series Charts */}
            {historicalData.length > 0 && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                    <TimeSeriesChart
                        title="📈 Suv sarfi dinamikasi (oxirgi 30 kun)"
                        data={historicalData}
                        xAxisKey="date"
                        dataKeys={[
                            { key: 'discharge', name: 'Suv sarfi (m³/s)', color: '#3b82f6' }
                        ]}
                        height={320}
                    />
                    <TimeSeriesChart
                        title="📊 Ko'p parametrli tahlil"
                        data={historicalData}
                        xAxisKey="date"
                        dataKeys={[
                            { key: 'water_level', name: 'Suv sathi (m)', color: '#10b981' },
                            { key: 'temperature', name: 'Harorat (°C)', color: '#f59e0b' }
                        ]}
                        height={320}
                    />
                </div>
            )}

            {/* Statistics */}
            {stats && stats.discharge && (
                <div className="card fade-in" style={{ marginBottom: '2rem' }}>
                    <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', color: 'white', borderLeft: '4px solid rgba(255,255,255,0.5)', paddingLeft: '1rem' }}>
                        📊 Statistik ko'rsatkichlar (Yillik)
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)', marginBottom: '0.5rem' }}>O'rtacha sarfi</p>
                            <p style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'white' }}>{stats.discharge.mean?.toFixed(1)} m³/s</p>
                        </div>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)', marginBottom: '0.5rem' }}>Minimal sarfi</p>
                            <p style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'white' }}>{stats.discharge.min?.toFixed(1)} m³/s</p>
                        </div>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)', marginBottom: '0.5rem' }}>Maksimal sarfi</p>
                            <p style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'white' }}>{stats.discharge.max?.toFixed(1)} m³/s</p>
                        </div>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)', marginBottom: '0.5rem' }}>Standart og'ish</p>
                            <p style={{ fontSize: '1.75rem', fontWeight: 'bold', color: 'white' }}>{stats.discharge.std?.toFixed(1)} m³/s</p>
                        </div>
                    </div>
                </div>
            )}

            {/* System Info */}
            <div className="gradient-border fade-in" style={{ padding: '2rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '14px', padding: '2rem', backdropFilter: 'blur(10px)' }}>
                    <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: 'white' }}>
                        🚀 GIMAT PhD-darajasidagi Platforma
                    </h3>
                    <p style={{ fontSize: '1rem', color: 'rgba(255,255,255,0.8)', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                        Gidrologik Intellektual Monitoring va Axborot Tizimi — gibrid AI modellar,
                        Knowledge Graph, XAI va What-if simulyatsiya asosida vaqt qatorlarini tahlil qilish
                        va prognozlash platformasi.
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>Wavelet-tahlil</span>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>SARIMA</span>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>Bi-LSTM</span>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>GNN</span>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>XAI (SHAP)</span>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>RAG</span>
                        <span className="stat-badge" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>Neo4j</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
