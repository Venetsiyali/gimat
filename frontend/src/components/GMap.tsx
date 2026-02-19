import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface Station {
    station_id: string;
    station_name: string;
    river_name: string;
    latitude: number;
    longitude: number;
}

interface LeafletMapProps {
    stations: Station[];
    selectedStation: string;
    onStationSelect: (stationId: string) => void;
    waterLevel?: number;
}

/* Custom Marker Icons based on status */
const createCustomIcon = (color: string, isSelected: boolean) => {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: ${color};
            width: ${isSelected ? '24px' : '16px'};
            height: ${isSelected ? '24px' : '16px'};
            border-radius: 50%;
            border: 2px solid #FFFFFF;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        "></div>`,
        iconSize: [isSelected ? 24 : 16, isSelected ? 24 : 16],
        iconAnchor: [isSelected ? 12 : 8, isSelected ? 12 : 8],
        popupAnchor: [0, isSelected ? -12 : -8],
    });
};

/* Component to handle map interactions like panning */
const MapUpdater: React.FC<{ center: [number, number], zoom: number }> = ({ center, zoom }) => {
    const map = useMap();
    useEffect(() => {
        map.setView(center, zoom);
    }, [center, zoom, map]);
    return null;
};

const GMap: React.FC<LeafletMapProps> = ({ stations, selectedStation, onStationSelect, waterLevel }) => {
    const [mapCenter, setMapCenter] = useState<[number, number]>([41.2995, 66.2401]); // Center roughly on Uzbekistan
    const [zoomLevel, setZoomLevel] = useState(6);

    useEffect(() => {
        const selected = stations.find(s => s.station_id === selectedStation);
        if (selected && selected.latitude && selected.longitude) {
            setMapCenter([selected.latitude, selected.longitude]);
            setZoomLevel(10);
        }
    }, [selectedStation, stations]);

    const getStatusColor = (stationId: string) => {
        if (stationId !== selectedStation) return '#10B981'; // Default green
        if (!waterLevel) return '#10B981';
        if (waterLevel > 4.0) return '#EF4444'; // Critical
        if (waterLevel > 3.0) return '#F59E0B'; // Warning
        return '#10B981'; // Safe
    };

    const getStatusText = (wl?: number) => {
        if (!wl) return '🟢 Xavfsiz';
        if (wl > 4.0) return '🔴 Kritik';
        if (wl > 3.0) return '🟡 Diqqat';
        return '🟢 Xavfsiz';
    };

    return (
        <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '520px', background: '#0A1628' }}>
            <MapContainer
                center={mapCenter}
                zoom={zoomLevel}
                style={{ width: '100%', height: '100%', borderRadius: '12px' }}
                zoomControl={false}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapUpdater center={mapCenter} zoom={zoomLevel} />

                {stations.map(station => {
                    if (!station.latitude || !station.longitude) return null;
                    const isSelected = station.station_id === selectedStation;
                    const color = getStatusColor(station.station_id);

                    return (
                        <Marker
                            key={station.station_id}
                            position={[station.latitude, station.longitude]}
                            icon={createCustomIcon(color, isSelected)}
                            eventHandlers={{
                                click: () => onStationSelect(station.station_id),
                            }}
                        >
                            <Popup closeButton={false} autoPan={true} className="custom-popup">
                                <div style={{
                                    fontFamily: 'Inter, sans-serif',
                                    color: '#0F172A',
                                    padding: '5px',
                                }}>
                                    <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0369A1', marginBottom: '4px' }}>
                                        📍 {station.station_name}
                                    </div>
                                    <div style={{ fontSize: '0.85rem', marginBottom: '4px' }}>
                                        🌊 Daryo: <strong>{station.river_name}</strong>
                                    </div>
                                    <div style={{ fontSize: '0.85rem', marginBottom: '8px', color: '#64748B' }}>
                                        Location: {station.latitude.toFixed(4)}, {station.longitude.toFixed(4)}
                                    </div>
                                    {isSelected && waterLevel && (
                                        <div style={{
                                            display: 'inline-block',
                                            padding: '2px 8px',
                                            borderRadius: '999px',
                                            fontSize: '0.8rem',
                                            fontWeight: 700,
                                            background: color === '#EF4444' ? '#FEE2E2' : color === '#F59E0B' ? '#FEF3C7' : '#D1FAE5',
                                            color: color === '#EF4444' ? '#991B1B' : color === '#F59E0B' ? '#92400E' : '#065F46',
                                            border: `1px solid ${color}`
                                        }}>{getStatusText(waterLevel)}</div>
                                    )}
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>

            {/* Map overlay label */}
            <div style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'rgba(10, 22, 40, 0.92)',
                border: '1px solid #1E293B',
                borderRadius: '8px',
                padding: '0.5rem 0.9rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#CBD5E1',
                fontFamily: 'Inter, system-ui, sans-serif',
                zIndex: 1000,
                pointerEvents: 'none',
            }}>
                🗺️ O'zbekiston Gidropost Tarmog'i — {stations.length} ta stansiya
            </div>

            {/* Legend */}
            <div style={{
                position: 'absolute',
                bottom: '2.5rem',
                left: '1rem',
                background: '#0F172A',
                border: '1px solid #1E3A5F',
                borderRadius: '10px',
                padding: '0.75rem 1.1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
                zIndex: 1000,
                boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
                fontFamily: 'Inter, system-ui, sans-serif',
            }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.15rem' }}>Holat</div>
                {[
                    { color: '#10B981', label: 'Xavfsiz  (≤ 3m)' },
                    { color: '#F59E0B', label: 'Diqqat   (3–4m)' },
                    { color: '#EF4444', label: 'Kritik   (> 4m)' },
                ].map(({ color, label }) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: color, border: '2px solid #FFF' }}></div>
                        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#FFFFFF', whiteSpace: 'nowrap' }}>{label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GMap;
