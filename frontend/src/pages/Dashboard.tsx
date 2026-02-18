import React, { useState, useEffect } from 'react';
import { dataAPI } from '../services/api';
import { MetricCard, TimeSeriesChart } from '../components/Charts';
import '../components/MetricCard.css';
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
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ marginBottom: '1.5rem' }} className="fade-in">
                <h2 style={{ fontSize: '2rem', fontWeight: '800', marginBottom: '0.5rem', color: '#38BDF8' }}>
                    📊 Dashboard
                </h2>
                <p style={{ color: '#FFFFFF', fontSize: '1.05rem', fontWeight: '500' }}>
                    Real-time gidrologik monitoring va PhD-darajasidagi tahlil
                </p>
            </div>

            {/* AI Technology Badge Banner */}
            <div className="dash-tech-banner fade-in">
                <span className="dash-tech-label">🧠 AI Texnologiyalar:</span>
                <div className="dash-tech-badges">
                    <span className="hc-badge hc-badge-preprocessing">Wavelet</span>
                    <span className="hc-badge hc-badge-preprocessing">SARIMA</span>
                    <span className="hc-badge hc-badge-ai">Bi-LSTM</span>
                    <span className="hc-badge hc-badge-ai">GNN</span>
                    <span className="hc-badge hc-badge-analytics">XAI</span>
                    <span className="hc-badge hc-badge-analytics">RAG</span>
                    <span className="hc-badge hc-badge-database">Neo4j</span>
                </div>
            </div>

            {/* Station Selector */}
            <div className="card fade-in" style={{ marginBottom: '2rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                    📍 Gidropost tanlang
                </label>
                <select
                    style={{
                        width: '100%',
                        maxWidth: '400px',
                        padding: '0.75rem 1rem',
                        borderRadius: '10px',
                        border: '1px solid var(--border-medium)',
                        background: 'white',
                        color: 'var(--text-primary)',
                        fontSize: '1rem',
                        cursor: 'pointer',
                        outline: 'none',
                        fontWeight: '500'
                    }}
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

            {/* Metric Cards */}
            {latestData && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                    <MetricCard
                        title="Suv sathi"
                        value={`${latestData.water_level?.toFixed(2) || 'N/A'}`}
                        subtitle="metr"
                        trend="up"
                        trendValue="+2.3%"
                        icon="💧"
                        gradient="primary"
                    />
                    <MetricCard
                        title="Suv sarfi"
                        value={`${latestData.discharge?.toFixed(1) || 'N/A'}`}
                        subtitle="m³/s"
                        trend="up"
                        trendValue="+5.1%"
                        icon="🌊"
                        gradient="success"
                    />
                    <MetricCard
                        title="Harorat"
                        value={`${latestData.temperature?.toFixed(1) || 'N/A'}°C`}
                        subtitle="Celsius"
                        trend="down"
                        trendValue="-1.2%"
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
                            { key: 'discharge', name: 'Suv sarfi (m³/s)', color: '#0ea5e9' }
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
                    <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', color: 'var(--text-primary)', borderLeft: '4px solid var(--primary-color)', paddingLeft: '1rem' }}>
                        📊 Statistik ko'rsatkichlar (Yillik)
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: '600' }}>O'rtacha sarfi</p>
                            <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{stats.discharge.mean?.toFixed(1)} m³/s</p>
                        </div>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: '600' }}>Minimal sarfi</p>
                            <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{stats.discharge.min?.toFixed(1)} m³/s</p>
                        </div>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: '600' }}>Maksimal sarfi</p>
                            <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{stats.discharge.max?.toFixed(1)} m³/s</p>
                        </div>
                        <div className="stat-badge">
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: '600' }}>Standart og'ish</p>
                            <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>{stats.discharge.std?.toFixed(1)} m³/s</p>
                        </div>
                    </div>
                </div>
            )}

            {/* System Info */}
            <div className="card fade-in" style={{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', borderColor: 'var(--primary-color)' }}>
                <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', color: 'var(--text-primary)' }}>
                    🚀 GIMAT PhD-darajasidagi Platforma
                </h3>
                <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: '1.6' }}>
                    Gidrologik Intellektual Monitoring va Axborot Tizimi — gibrid AI modellar,
                    Knowledge Graph, XAI va What-if simulyatsiya asosida vaqt qatorlarini tahlil qilish
                    va prognozlash platformasi.
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                    {['Wavelet-tahlil', 'SARIMA', 'Bi-LSTM', 'GNN', 'XAI (SHAP)', 'RAG', 'Neo4j'].map((tech) => (
                        <span key={tech} style={{
                            padding: '0.5rem 1rem',
                            background: 'white',
                            borderRadius: '8px',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            color: 'var(--primary-color)',
                            border: '1px solid var(--primary-color)',
                            boxShadow: 'var(--shadow-sm)'
                        }}>
                            {tech}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
