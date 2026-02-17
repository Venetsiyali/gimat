import React from 'react';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import './MetricCard.css';

interface MetricCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: string;
    icon?: React.ReactNode;
    gradient?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
    title,
    value,
    subtitle,
    trend,
    trendValue,
    icon,
    gradient = 'primary'
}) => {
    const getTrendColor = () => {
        if (trend === 'up') return '#10b981';
        if (trend === 'down') return '#ef4444';
        return '#6b7280';
    };

    const getGradientClass = () => {
        switch (gradient) {
            case 'success': return 'gradient-success';
            case 'warning': return 'gradient-warning';
            case 'secondary': return 'gradient-secondary';
            default: return 'gradient-primary';
        }
    };

    return (
        <div className="metric-card fade-in">
            <div className="metric-header">
                {icon && <div className={`metric-icon ${getGradientClass()}`}>{icon}</div>}
                <span className="metric-title">{title}</span>
            </div>

            <div className="metric-value">{value}</div>

            {subtitle && <div className="metric-subtitle">{subtitle}</div>}

            {trend && trendValue && (
                <div className="metric-trend" style={{ color: getTrendColor() }}>
                    <span className="trend-arrow">
                        {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
                    </span>
                    <span className="trend-value">{trendValue}</span>
                </div>
            )}
        </div>
    );
};

interface TimeSeriesChartProps {
    data: any[];
    dataKeys: {
        key: string;
        name: string;
        color: string;
    }[];
    xAxisKey: string;
    title?: string;
    height?: number;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
    data,
    dataKeys,
    xAxisKey,
    title,
    height = 300
}) => {
    return (
        <div className="chart-container fade-in">
            {title && <h3 className="chart-title">{title}</h3>}
            <ResponsiveContainer width="100%" height={height}>
                <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <defs>
                        {dataKeys.map((dk, idx) => (
                            <linearGradient key={idx} id={`gradient-${idx}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={dk.color} stopOpacity={0.8} />
                                <stop offset="95%" stopColor={dk.color} stopOpacity={0.1} />
                            </linearGradient>
                        ))}
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey={xAxisKey}
                        stroke="rgba(255,255,255,0.6)"
                        style={{ fontSize: '12px' }}
                    />
                    <YAxis
                        stroke="rgba(255,255,255,0.6)"
                        style={{ fontSize: '12px' }}
                    />
                    <Tooltip
                        contentStyle={{
                            background: 'rgba(255, 255, 255, 0.15)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            borderRadius: '12px',
                            color: '#fff'
                        }}
                    />
                    <Legend
                        wrapperStyle={{ color: '#fff' }}
                    />
                    {dataKeys.map((dk, idx) => (
                        <Line
                            key={idx}
                            type="monotone"
                            dataKey={dk.key}
                            name={dk.name}
                            stroke={dk.color}
                            strokeWidth={3}
                            dot={{ fill: dk.color, r: 4 }}
                            activeDot={{ r: 6 }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

interface ConfidenceAreaChartProps {
    data: any[];
    predictionKey: string;
    upperBoundKey: string;
    lowerBoundKey: string;
    xAxisKey: string;
    title?: string;
    height?: number;
}

export const ConfidenceAreaChart: React.FC<ConfidenceAreaChartProps> = ({
    data,
    predictionKey,
    upperBoundKey,
    lowerBoundKey,
    xAxisKey,
    title,
    height = 300
}) => {
    return (
        <div className="chart-container fade-in">
            {title && <h3 className="chart-title">{title}</h3>}
            <ResponsiveContainer width="100%" height={height}>
                <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <defs>
                        <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey={xAxisKey}
                        stroke="rgba(255,255,255,0.6)"
                        style={{ fontSize: '12px' }}
                    />
                    <YAxis
                        stroke="rgba(255,255,255,0.6)"
                        style={{ fontSize: '12px' }}
                    />
                    <Tooltip
                        contentStyle={{
                            background: 'rgba(255, 255, 255, 0.15)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            borderRadius: '12px',
                            color: '#fff'
                        }}
                    />
                    <Legend wrapperStyle={{ color: '#fff' }} />

                    {/* Confidence interval area */}
                    <Area
                        type="monotone"
                        dataKey={upperBoundKey}
                        stackId="1"
                        stroke="none"
                        fill="url(#colorConfidence)"
                        name="95% Confidence"
                    />
                    <Area
                        type="monotone"
                        dataKey={lowerBoundKey}
                        stackId="1"
                        stroke="none"
                        fill="url(#colorConfidence)"
                    />

                    {/* Main prediction line */}
                    <Line
                        type="monotone"
                        dataKey={predictionKey}
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={{ fill: '#3b82f6', r: 4 }}
                        name="Bashorat"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};
