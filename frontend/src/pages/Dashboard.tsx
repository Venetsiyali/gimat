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

    /* Determine marker status color */
    const getMarkerStatus = (station: Station) => {
        if (!latestData || station.station_id !== selectedStation) return '#10B981'; // green
        const wl = latestData.water_level;
        if (wl > 4.0) return '#EF4444'; // critical red
        if (wl > 3.0) return '#F59E0B'; // warning amber
        return '#10B981'; // safe green
    };

    /* Generate SVG marker positions from lat/lon */
    const getMarkerXY = (lat: number, lon: number) => {
        // Uzbekistan approx bounds: lat 37–42, lon 56–73
        const x = ((lon - 56) / (73 - 56)) * 100;
        const y = ((42 - lat) / (42 - 37)) * 100;
        return { x: Math.max(5, Math.min(95, x)), y: Math.max(5, Math.min(95, y)) };
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

                {/* MAP AREA */}
                <div className="fh-map-area">
                    <div className="fh-map-container">
                        {/* SVG interactive map of Uzbekistan */}
                        <svg
                            viewBox="0 0 100 100"
                            className="fh-map-svg"
                            preserveAspectRatio="xMidYMid meet"
                        >
                            {/* Background grid */}
                            <defs>
                                <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                                    <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#1E293B" strokeWidth="0.3" />
                                </pattern>
                            </defs>
                            <rect width="100" height="100" fill="#0A1628" />
                            <rect width="100" height="100" fill="url(#grid)" />

                            {/* Uzbekistan simplified outline */}
                            <path
                                d="M 15,30 L 25,20 L 45,18 L 60,22 L 75,18 L 88,25 L 90,38 L 82,50 L 75,55 L 65,60 L 55,65 L 45,70 L 35,72 L 22,68 L 12,58 L 10,45 Z"
                                fill="#0F2040"
                                stroke="#1E3A5F"
                                strokeWidth="0.8"
                            />

                            {/* River lines */}
                            <path d="M 30,25 Q 45,40 55,55 Q 60,62 65,68" fill="none" stroke="#0EA5E9" strokeWidth="0.6" opacity="0.7" />
                            <path d="M 60,22 Q 65,35 70,50 Q 72,58 68,65" fill="none" stroke="#0EA5E9" strokeWidth="0.5" opacity="0.6" />
                            <path d="M 20,40 Q 35,45 50,48 Q 62,50 75,48" fill="none" stroke="#0EA5E9" strokeWidth="0.5" opacity="0.5" />

                            {/* Station markers */}
                            {stations.map((station, i) => {
                                const pos = station.latitude && station.longitude
                                    ? getMarkerXY(station.latitude, station.longitude)
                                    : { x: 20 + (i * 15) % 60, y: 30 + (i * 12) % 40 };
                                const color = getMarkerStatus(station);
                                const isSelected = station.station_id === selectedStation;
                                return (
                                    <g
                                        key={station.station_id}
                                        onClick={() => setSelectedStation(station.station_id)}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        {/* Pulse ring for selected */}
                                        {isSelected && (
                                            <circle cx={pos.x} cy={pos.y} r="4" fill="none" stroke={color} strokeWidth="0.8" opacity="0.5">
                                                <animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite" />
                                                <animate attributeName="opacity" values="0.5;0;0.5" dur="2s" repeatCount="indefinite" />
                                            </circle>
                                        )}
                                        {/* Marker dot */}
                                        <circle
                                            cx={pos.x} cy={pos.y}
                                            r={isSelected ? 3 : 2}
                                            fill={color}
                                            stroke="#FFFFFF"
                                            strokeWidth="0.5"
                                        />
                                        {/* Label */}
                                        <text
                                            x={pos.x + 3.5} y={pos.y + 1}
                                            fontSize="2.5"
                                            fill="#FFFFFF"
                                            fontFamily="Inter, sans-serif"
                                            fontWeight={isSelected ? '700' : '400'}
                                        >
                                            {station.station_name?.substring(0, 12)}
                                        </text>
                                    </g>
                                );
                            })}

                            {/* Legend */}
                            <g transform="translate(2, 85)">
                                <circle cx="2" cy="2" r="1.5" fill="#10B981" />
                                <text x="5" y="3" fontSize="2.2" fill="#CBD5E1" fontFamily="Inter, sans-serif">Xavfsiz</text>
                                <circle cx="20" cy="2" r="1.5" fill="#F59E0B" />
                                <text x="23" y="3" fontSize="2.2" fill="#CBD5E1" fontFamily="Inter, sans-serif">Diqqat</text>
                                <circle cx="38" cy="2" r="1.5" fill="#EF4444" />
                                <text x="41" y="3" fontSize="2.2" fill="#CBD5E1" fontFamily="Inter, sans-serif">Kritik</text>
                            </g>
                        </svg>

                        {/* Map overlay label */}
                        <div className="fh-map-label">
                            🗺️ O'zbekiston Gidropost Tarmog'i — {stations.length} ta stansiya
                        </div>
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
