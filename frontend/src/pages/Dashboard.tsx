import React, { useState, useEffect } from 'react';
import { dataAPI } from '../services/api';
import { MetricCard, TimeSeriesChart } from '../components/Charts';
import GMap from '../components/GMap';
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

/* Search terms defined outside component to avoid exhaustive-deps lint warning */
const SEARCH_TERMS = [
    'Zarafshon suv sathi', 'Amudaryo sarfi', 'Sirdaryo monitoring',
    'Qashqadaryo prognoz', 'Surxondaryo tahlil', 'Chirchiq daryosi',
    'Toshkent viloyati', 'Samarqand gidropost', 'Buxoro suv resurslari',
];

const Dashboard: React.FC = () => {
    const [stations, setStations] = useState<Station[]>([]);
    const [selectedStation, setSelectedStation] = useState<string>('');
    const [latestData, setLatestData] = useState<LatestData | null>(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<any>(null);
    const [historicalData, setHistoricalData] = useState<any[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
    const [showBottomSheet, setShowBottomSheet] = useState(false);

    useEffect(() => { loadStations(); }, []);

    useEffect(() => {
        if (selectedStation) {
            loadLatestData();
            loadStatistics();
            loadHistoricalData();
            setShowBottomSheet(true);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedStation]);

    useEffect(() => {
        if (searchQuery.length > 1) {
            const filtered = SEARCH_TERMS.filter(t =>
                t.toLowerCase().includes(searchQuery.toLowerCase())
            );
            setSearchSuggestions(filtered);
        } else {
            setSearchSuggestions([]);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchQuery]);

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
            const mockData = Array.from({ length: 30 }, (_, i) => ({
                date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000)
                    .toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric' }),
                discharge: 150 + Math.sin(i / 5) * 30 + Math.random() * 20,
                water_level: 2.5 + Math.sin(i / 7) * 0.5 + Math.random() * 0.3,
                temperature: 18 + Math.sin(i / 10) * 5 + Math.random() * 2,
            }));
            setHistoricalData(mockData);
        } catch (error) {
            console.error('Error loading historical data:', error);
        }
    };

    if (loading) {
        return (
            <div className="dash-loading">
                <div className="spinner"></div>
                <p className="dash-loading-text">Ma'lumotlar yuklanmoqda...</p>
            </div>
        );
    }

    const selectedStationObj = stations.find(s => s.station_id === selectedStation);

    return (
        <div className="flood-hub-layout">

            {/* ── SEMANTIC SEARCH BAR ─────────────────────── */}
            <div className="fh-search-bar">
                <div className="fh-search-inner">
                    <span className="fh-search-icon">🔍</span>
                    <input
                        className="fh-search-input"
                        type="text"
                        placeholder="Qidiring: 'Zarafshon suv sathi', 'Amudaryo sarfi'..."
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === 'Escape') { setSearchQuery(''); setSearchSuggestions([]); }
                        }}
                    />
                    {searchQuery && (
                        <button className="fh-search-clear" onClick={() => { setSearchQuery(''); setSearchSuggestions([]); }}>✕</button>
                    )}
                </div>
                {searchSuggestions.length > 0 && (
                    <div className="fh-search-suggestions">
                        {searchSuggestions.map(s => (
                            <div key={s} className="fh-suggestion-item" onClick={() => { setSearchQuery(s); setSearchSuggestions([]); }}>
                                <span className="fh-suggestion-icon">📍</span>
                                {s}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* ── MAIN AREA: MAP + SIDE PANEL ────────────── */}
            <div className="fh-main-area">

                {/* LEFT SIDE PANEL */}
                <aside className="fh-side-panel">
                    <div className="fh-panel-section">
                        <div className="fh-panel-label">📍 Gidropost</div>
                        <select
                            className="fh-select"
                            value={selectedStation}
                            onChange={e => setSelectedStation(e.target.value)}
                        >
                            {stations.map(s => (
                                <option key={s.station_id} value={s.station_id}>
                                    {s.station_name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {selectedStationObj && (
                        <div className="fh-panel-section">
                            <div className="fh-panel-label">🌊 Daryo</div>
                            <div className="fh-panel-value">{selectedStationObj.river_name}</div>
                        </div>
                    )}

                    {/* Live Metrics */}
                    {latestData && (
                        <div className="fh-panel-section">
                            <div className="fh-panel-label">📊 Joriy ko'rsatkichlar</div>
                            <div className="fh-metric-row">
                                <span className="fh-metric-icon">💧</span>
                                <div>
                                    <div className="fh-metric-label">Suv sathi</div>
                                    <div className="fh-metric-value">{latestData.water_level?.toFixed(2)} m</div>
                                </div>
                            </div>
                            <div className="fh-metric-row">
                                <span className="fh-metric-icon">🌊</span>
                                <div>
                                    <div className="fh-metric-label">Suv sarfi</div>
                                    <div className="fh-metric-value">{latestData.discharge?.toFixed(1)} m³/s</div>
                                </div>
                            </div>
                            <div className="fh-metric-row">
                                <span className="fh-metric-icon">🌡️</span>
                                <div>
                                    <div className="fh-metric-label">Harorat</div>
                                    <div className="fh-metric-value">{latestData.temperature?.toFixed(1)}°C</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Status indicator */}
                    {latestData && (
                        <div className="fh-panel-section">
                            <div className="fh-panel-label">🚦 Holat</div>
                            <div className={`fh-status-badge ${latestData.water_level > 4 ? 'fh-status-critical' : latestData.water_level > 3 ? 'fh-status-warning' : 'fh-status-safe'}`}>
                                {latestData.water_level > 4 ? '🔴 Kritik' : latestData.water_level > 3 ? '🟡 Diqqat' : '🟢 Xavfsiz'}
                            </div>
                        </div>
                    )}

                    {/* Chart toggle */}
                    <button
                        className="fh-chart-toggle"
                        onClick={() => setShowBottomSheet(v => !v)}
                    >
                        {showBottomSheet ? '📈 Grafikni yashirish' : '📈 Grafikni ko\'rish'}
                    </button>
                </aside>

                {/* MAP AREA — Google Maps */}
                <div className="fh-map-area">
                    <div className="fh-map-container">
                        <GMap
                            stations={stations}
                            selectedStation={selectedStation}
                            onStationSelect={setSelectedStation}
                            waterLevel={latestData?.water_level}
                        />
                    </div>
                </div>
            </div>

            {/* ── BOTTOM SHEET: CHARTS ────────────────────── */}
            {showBottomSheet && historicalData.length > 0 && (
                <div className="fh-bottom-sheet">
                    <div className="fh-bottom-sheet-header">
                        <h3 className="fh-bottom-title">
                            📈 {selectedStationObj?.station_name || 'Gidropost'} — Vaqt qatori tahlili
                        </h3>
                        <button className="fh-close-btn" onClick={() => setShowBottomSheet(false)}>✕</button>
                    </div>

                    {/* Metric cards row */}
                    {latestData && (
                        <div className="fh-metric-cards">
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

                    {/* Charts */}
                    <div className="fh-charts-grid">
                        <TimeSeriesChart
                            title="📈 Suv sarfi dinamikasi (oxirgi 30 kun)"
                            data={historicalData}
                            xAxisKey="date"
                            dataKeys={[{ key: 'discharge', name: 'Suv sarfi (m³/s)', color: '#0ea5e9' }]}
                            height={260}
                        />
                        <TimeSeriesChart
                            title="📊 Suv sathi va harorat"
                            data={historicalData}
                            xAxisKey="date"
                            dataKeys={[
                                { key: 'water_level', name: 'Suv sathi (m)', color: '#10b981' },
                                { key: 'temperature', name: 'Harorat (°C)', color: '#f59e0b' },
                            ]}
                            height={260}
                        />
                    </div>

                    {/* Statistics row */}
                    {stats && stats.discharge && (
                        <div className="fh-stats-row">
                            <div className="fh-stat-item">
                                <div className="fh-stat-label">O'rtacha sarfi</div>
                                <div className="fh-stat-value">{stats.discharge.mean?.toFixed(1)} <span className="fh-stat-unit">m³/s</span></div>
                            </div>
                            <div className="fh-stat-item">
                                <div className="fh-stat-label">Minimal</div>
                                <div className="fh-stat-value">{stats.discharge.min?.toFixed(1)} <span className="fh-stat-unit">m³/s</span></div>
                            </div>
                            <div className="fh-stat-item">
                                <div className="fh-stat-label">Maksimal</div>
                                <div className="fh-stat-value">{stats.discharge.max?.toFixed(1)} <span className="fh-stat-unit">m³/s</span></div>
                            </div>
                            <div className="fh-stat-item">
                                <div className="fh-stat-label">Standart og'ish</div>
                                <div className="fh-stat-value">{stats.discharge.std?.toFixed(1)} <span className="fh-stat-unit">m³/s</span></div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
