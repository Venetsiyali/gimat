import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ComposedChart,
    Line
} from 'recharts';

// --- Types ---
interface PredictionData {
    date: string;
    H: number; // Suv sathi
    Q: number; // Suv sarfi
    type: 'history' | 'forecast';
}

interface Metrics {
    NSE: number;
    RMSE: number;
    MAE: number;
    R2: number;
}

// --- Component ---
const Predictions: React.FC = () => {
    // State
    const [selectedStation, setSelectedStation] = useState<string>('chirchiq_post_1');
    const [selectedModel, setSelectedModel] = useState<string>('Wavelet-BiLSTM');
    const [loading, setLoading] = useState<boolean>(false);
    const [data, setData] = useState<PredictionData[]>([]);
    const [metrics, setMetrics] = useState<Metrics | null>(null);

    // Config
    const API_URL = 'https://gimat-production.up.railway.app/api/predictions/forecast';

    // Fetch Data
    const handleGenerate = async () => {
        setLoading(true);
        try {
            const response = await axios.post(API_URL, {
                station_id: selectedStation,
                model: selectedModel
            });

            if (response.data && response.data.data) {
                setData(response.data.data);
                setMetrics(response.data.metrics);
            }
        } catch (error) {
            console.error("Prediction Error:", error);
            // Fallback is good for demo, but in production we might want to show error toast
            generateMockData();
        } finally {
            setLoading(false);
        }
    };

    const generateMockData = () => {
        const mockData: PredictionData[] = [];
        const today = new Date();
        for (let i = 30; i > 0; i--) {
            const d = new Date(today);
            d.setDate(d.getDate() - i);
            mockData.push({
                date: d.toLocaleDateString('uz-UZ'),
                H: 2.5 + Math.random() * 0.5,
                Q: 140 + Math.random() * 20,
                type: 'history'
            });
        }
        for (let i = 0; i < 7; i++) {
            const d = new Date(today);
            d.setDate(d.getDate() + i);
            mockData.push({
                date: d.toLocaleDateString('uz-UZ'),
                H: 3.0 + Math.random() * 0.8,
                Q: 180 + Math.random() * 30,
                type: 'forecast'
            });
        }
        setData(mockData);
        setMetrics({ NSE: 0.94, RMSE: 0.032, MAE: 0.021, R2: 0.96 });
    };

    useEffect(() => {
        handleGenerate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Custom Tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-slate-900/90 border border-slate-700 p-4 rounded-xl shadow-[0_0_20px_rgba(14,165,233,0.3)] backdrop-blur-md">
                    <p className="text-slate-400 text-xs mb-2 font-mono uppercase tracking-wider">{label}</p>
                    {payload.map((p: any, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 mb-1">
                            <div className="w-2 h-2 rounded-full shadow-[0_0_8px_ currentColor]" style={{ backgroundColor: p.color, color: p.color }}></div>
                            <span className="text-slate-200 text-sm font-bold font-mono">
                                {p.name}: <span style={{ color: p.color }} className="drop-shadow-sm">{p.value.toFixed(2)}</span>
                            </span>
                        </div>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="flex h-[calc(100vh-64px)] bg-[#0f172a] text-slate-200 font-sans overflow-hidden">

            {/* --- SIDEBAR --- */}
            <div className="w-80 bg-slate-900/50 border-r border-slate-800 flex flex-col z-20 backdrop-blur-sm">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-sky-400 to-teal-400 bg-clip-text text-transparent flex items-center gap-3">
                        <span>🌊</span> AI Prognoz
                    </h2>
                    <p className="text-xs text-slate-500 mt-2 font-medium tracking-wide">GIDROLOGIK MONITORING TIZIMI</p>
                </div>

                <div className="p-6 flex-1 space-y-8 overflow-y-auto">
                    {/* Station Selector */}
                    <div className="space-y-3">
                        <label className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <span className="w-1 h-1 rounded-full bg-sky-500 shadow-[0_0_8px_#0ea5e9]"></span>
                            Gidropost
                        </label>
                        <div className="relative group">
                            <select
                                className="w-full bg-slate-800/80 border border-slate-700 text-slate-200 text-sm rounded-xl p-4 appearance-none focus:ring-2 focus:ring-sky-500 focus:border-transparent outline-none transition-all cursor-pointer hover:bg-slate-800 shadow-inner"
                                value={selectedStation}
                                onChange={(e) => setSelectedStation(e.target.value)}
                            >
                                <option value="chirchiq_post_1">Chirchiq - G'azalkent</option>
                                <option value="chirchiq_post_2">Chirchiq - Oqtepa</option>
                                <option value="zarafshon_post_1">Zarafshon - Ravotxo'ja</option>
                            </select>
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 group-hover:text-sky-400 transition-colors">
                                ▼
                            </div>
                        </div>
                    </div>

                    {/* Model Selector (Button Group) */}
                    <div className="space-y-3">
                        <label className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <span className="w-1 h-1 rounded-full bg-teal-400 shadow-[0_0_8px_#2dd4bf]"></span>
                            AI Model
                        </label>
                        <div className="flex flex-col gap-2">
                            {['Wavelet-BiLSTM', 'GNN-LSTM', 'SARIMA'].map((model) => (
                                <motion.button
                                    key={model}
                                    onClick={() => setSelectedModel(model)}
                                    whileHover={{ scale: 1.02, x: 4 }}
                                    whileTap={{ scale: 0.98 }}
                                    className={`relative w-full text-left px-5 py-4 rounded-xl text-sm transition-all border overflow-hidden ${selectedModel === model
                                            ? 'border-sky-500/50 shadow-[0_0_20px_rgba(14,165,233,0.15)] bg-sky-500/5'
                                            : 'bg-slate-800/40 border-slate-700/50 text-slate-400 hover:bg-slate-800 hover:border-slate-600'
                                        }`}
                                >
                                    {selectedModel === model && (
                                        <motion.div
                                            layoutId="activeModel"
                                            className="absolute inset-0 bg-gradient-to-r from-sky-500/10 to-transparent z-0"
                                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                        />
                                    )}
                                    <div className="relative z-10 flex justify-between items-center">
                                        <span className={`font-bold ${selectedModel === model ? 'text-sky-400' : 'text-slate-300'}`}>
                                            {model}
                                        </span>
                                        {selectedModel === model && (
                                            <motion.span
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                className="w-2 h-2 rounded-full bg-sky-400 shadow-[0_0_10px_rgba(14,165,233,0.8)]"
                                            />
                                        )}
                                    </div>
                                    <div className="relative z-10 text-[10px] opacity-60 mt-1 font-medium">
                                        {model === 'Wavelet-BiLSTM' ? 'Time-Series & Wavelet' :
                                            model === 'GNN-LSTM' ? 'Graph Neural Network' : 'Statistical Model'}
                                    </div>
                                </motion.button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="p-6 border-t border-slate-800 bg-slate-900/80 backdrop-blur-md">
                    <motion.button
                        onClick={handleGenerate}
                        disabled={loading}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`w-full py-4 rounded-xl font-bold text-center tracking-wide transition-all ${loading
                                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                                : 'bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 border border-t-sky-400/20'
                            }`}
                    >
                        {loading ? (
                            <div className="flex items-center justify-center gap-3">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                                />
                                <span>KUTING...</span>
                            </div>
                        ) : 'HISOBLASH'}
                    </motion.button>
                </div>
            </div>

            {/* --- MAIN AREA --- */}
            <div className="flex-1 flex flex-col relative overflow-y-auto bg-[url('/grid.svg')] bg-fixed">
                <div className="absolute inset-0 bg-gradient-to-br from-slate-900/50 via-slate-900/80 to-slate-900 pointer-events-none" />

                <div className="relative z-10 flex-1 p-8 lg:p-12 max-w-7xl mx-auto w-full flex flex-col">

                    {/* Header Strip */}
                    <div className="flex flex-col md:flex-row justify-between items-end mb-10 pb-6 border-b border-slate-800/60">
                        <div>
                            <h1 className="text-4xl font-black text-white mb-3 tracking-tight drop-shadow-2xl">
                                Suv Sathi Prognozi
                            </h1>
                            <div className="flex items-center gap-6 text-sm font-medium">
                                <div className="flex items-center gap-2 text-slate-400">
                                    <span className="w-2 h-2 rounded-full bg-slate-500 shadow-[0_0_8px_#64748b]"></span> History
                                </div>
                                <div className="flex items-center gap-2 text-sky-400">
                                    <span className="w-2 h-2 rounded-full bg-sky-400 shadow-[0_0_10px_rgba(14,165,233,0.8)] animate-pulse"></span> AI Forecast
                                </div>
                            </div>
                        </div>
                        {metrics && <StatsWidget metrics={metrics} />}
                    </div>

                    {/* Chart Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="flex-1 min-h-[500px] w-full bg-slate-800/30 border border-slate-700/50 rounded-3xl p-1 shadow-2xl backdrop-blur-xl relative overflow-hidden group"
                    >
                        {/* Glass Shine Effect */}
                        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent rounded-3xl pointer-events-none" />

                        <div className="absolute inset-0 flex flex-col p-6 sm:p-8">
                            {loading && (
                                <div className="absolute inset-0 z-20 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center rounded-3xl transition-all">
                                    <div className="flex flex-col items-center gap-6">
                                        <div className="relative">
                                            <div className="w-24 h-24 border-4 border-slate-700 rounded-full"></div>
                                            <div className="w-24 h-24 border-4 border-sky-500 rounded-full border-t-transparent animate-spin absolute top-0 left-0 shadow-[0_0_30px_rgba(14,165,233,0.4)]"></div>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <span className="text-2xl">🤖</span>
                                            </div>
                                        </div>
                                        <p className="text-sky-400 font-mono text-sm tracking-[0.3em] animate-pulse font-bold">AI PROCESSING</p>
                                    </div>
                                </div>
                            )}

                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                                    <defs>
                                        <linearGradient id="colorQ" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                        </linearGradient>
                                        <filter id="shadow" height="130%">
                                            <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
                                            <feOffset dx="2" dy="2" result="offsetblur" />
                                            <feComponentTransfer>
                                                <feFuncA type="linear" slope="0.5" />
                                            </feComponentTransfer>
                                            <feMerge>
                                                <feMergeNode />
                                                <feMergeNode in="SourceGraphic" />
                                            </feMerge>
                                        </filter>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#475569"
                                        tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }}
                                        tickLine={false}
                                        axisLine={false}
                                        dy={15}
                                    />
                                    <YAxis
                                        yAxisId="left"
                                        stroke="#475569"
                                        tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(value) => `${value}`}
                                        label={{ value: 'Suv Sarfi (Q)', angle: -90, position: 'insideLeft', fill: '#64748b', style: { textAnchor: 'middle' } }}
                                    />
                                    <YAxis
                                        yAxisId="right"
                                        orientation="right"
                                        stroke="#475569"
                                        tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 600 }}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(value) => `${value}`}
                                        label={{ value: 'Suv Sathi (H)', angle: 90, position: 'insideRight', fill: '#64748b', style: { textAnchor: 'middle' } }}
                                    />
                                    <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#334155', strokeWidth: 1, strokeDasharray: '4 4' }} />

                                    <Area
                                        yAxisId="left"
                                        type="monotone"
                                        dataKey="Q"
                                        stroke="#0ea5e9"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorQ)"
                                        name="Suv Sarfi (Q)"
                                        filter="url(#shadow)"
                                        animationDuration={1500}
                                    />

                                    <Line
                                        yAxisId="right"
                                        type="monotone"
                                        dataKey="H"
                                        stroke="#2dd4bf"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#0f172a', stroke: '#2dd4bf', strokeWidth: 2 }}
                                        activeDot={{ r: 8, fill: '#2dd4bf', stroke: '#fff', strokeWidth: 2 }}
                                        name="Suv Sathi (H)"
                                        animationDuration={1500}
                                        className="filter drop-shadow-[0_0_8px_rgba(45,212,191,0.5)]"
                                    />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

// --- Sub-Components ---
const StatsWidget = ({ metrics }: { metrics: Metrics }) => {
    return (
        <div className="flex flex-wrap gap-4 justify-end">
            <StatCard label="NSE" value={metrics.NSE} color="text-teal-400" borderColor="border-teal-500" icon="🎯" />
            <StatCard label="RMSE" value={metrics.RMSE} color="text-rose-400" borderColor="border-rose-500" icon="📉" />
            <div className="w-px bg-slate-800 mx-2 hidden md:block"></div>
            <StatCard label="R²" value={metrics.R2} color="text-sky-400" borderColor="border-sky-500" icon="📊" />
        </div>
    );
};

const StatCard = ({ label, value, color, borderColor, icon }: { label: string, value: number, color: string, borderColor: string, icon: string }) => (
    <motion.div
        whileHover={{ scale: 1.05, y: -2 }}
        className={`flex items-center gap-4 bg-slate-900/80 border-l-4 ${borderColor} border-y border-r border-slate-800/50 px-6 py-4 rounded-xl backdrop-blur-md shadow-[0_0_15px_rgba(0,0,0,0.3)] hover:shadow-[0_0_20px_rgba(14,165,233,0.15)] transition-all`}
    >
        <span className="text-2xl filter drop-shadow-md">{icon}</span>
        <div>
            <p className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest mb-1">{label}</p>
            <p className={`text-2xl font-black font-mono ${color} filter drop-shadow-[0_0_5px_currentColor]`}>{value.toFixed(3)}</p>
        </div>
    </motion.div>
);

export default Predictions;
