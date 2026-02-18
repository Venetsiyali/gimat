import React, { useEffect, useRef, useCallback } from 'react';

interface Station {
    station_id: string;
    station_name: string;
    river_name: string;
    latitude: number;
    longitude: number;
}

interface GoogleMapProps {
    stations: Station[];
    selectedStation: string;
    onStationSelect: (stationId: string) => void;
    waterLevel?: number;
}

/* Determine marker color based on water level */
const getMarkerColor = (stationId: string, selectedStation: string, waterLevel?: number): string => {
    if (stationId !== selectedStation) return '#10B981'; // green — default
    if (!waterLevel) return '#10B981';
    if (waterLevel > 4.0) return '#EF4444'; // critical red
    if (waterLevel > 3.0) return '#F59E0B'; // warning amber
    return '#10B981'; // safe green
};

/* Dark map style matching Deep Blue design */
const DARK_MAP_STYLE = [
    { elementType: 'geometry', stylers: [{ color: '#0A1628' }] },
    { elementType: 'labels.text.stroke', stylers: [{ color: '#0A1628' }] },
    { elementType: 'labels.text.fill', stylers: [{ color: '#CBD5E1' }] },
    { featureType: 'administrative', elementType: 'geometry.stroke', stylers: [{ color: '#1E3A5F' }] },
    { featureType: 'administrative.land_parcel', elementType: 'labels.text.fill', stylers: [{ color: '#64748B' }] },
    { featureType: 'landscape.natural', elementType: 'geometry', stylers: [{ color: '#0F172A' }] },
    { featureType: 'poi', elementType: 'geometry', stylers: [{ color: '#0F172A' }] },
    { featureType: 'poi', elementType: 'labels.text.fill', stylers: [{ color: '#64748B' }] },
    { featureType: 'poi.park', elementType: 'geometry', stylers: [{ color: '#052E16' }] },
    { featureType: 'poi.park', elementType: 'labels.text.fill', stylers: [{ color: '#10B981' }] },
    { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#1E293B' }] },
    { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#0F172A' }] },
    { featureType: 'road', elementType: 'labels.text.fill', stylers: [{ color: '#94A3B8' }] },
    { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: '#1E3A5F' }] },
    { featureType: 'road.highway', elementType: 'geometry.stroke', stylers: [{ color: '#0A1628' }] },
    { featureType: 'road.highway', elementType: 'labels.text.fill', stylers: [{ color: '#CBD5E1' }] },
    { featureType: 'transit', elementType: 'geometry', stylers: [{ color: '#0F172A' }] },
    { featureType: 'transit.station', elementType: 'labels.text.fill', stylers: [{ color: '#64748B' }] },
    { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#0C2340' }] },
    { featureType: 'water', elementType: 'labels.text.fill', stylers: [{ color: '#38BDF8' }] },
    { featureType: 'water', elementType: 'labels.text.stroke', stylers: [{ color: '#0A1628' }] },
];

declare global {
    interface Window {
        google: any;
    }
}

const GMap: React.FC<GoogleMapProps> = ({ stations, selectedStation, onStationSelect, waterLevel }) => {
    const mapRef = useRef<HTMLDivElement>(null);
    const mapInstanceRef = useRef<any>(null);
    const markersRef = useRef<any[]>([]);
    const infoWindowRef = useRef<any>(null);

    const initMap = useCallback(() => {
        if (!mapRef.current || !window.google) return;

        const map = new window.google.maps.Map(mapRef.current, {
            center: { lat: 41.2995, lng: 63.2401 }, // O'zbekiston markazi
            zoom: 6,
            styles: DARK_MAP_STYLE,
            disableDefaultUI: false,
            zoomControl: true,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: true,
            backgroundColor: '#0A1628',
        });

        mapInstanceRef.current = map;
        infoWindowRef.current = new window.google.maps.InfoWindow();

        // Add markers for each station
        stations.forEach(station => {
            if (!station.latitude || !station.longitude) return;

            const color = getMarkerColor(station.station_id, selectedStation, waterLevel);
            const isSelected = station.station_id === selectedStation;

            const marker = new window.google.maps.Marker({
                position: { lat: station.latitude, lng: station.longitude },
                map,
                title: station.station_name,
                icon: {
                    path: window.google.maps.SymbolPath.CIRCLE,
                    scale: isSelected ? 12 : 8,
                    fillColor: color,
                    fillOpacity: 1,
                    strokeColor: '#FFFFFF',
                    strokeWeight: isSelected ? 2.5 : 1.5,
                },
                animation: isSelected ? window.google.maps.Animation.BOUNCE : null,
                zIndex: isSelected ? 100 : 1,
            });

            marker.addListener('click', () => {
                onStationSelect(station.station_id);

                const wl = waterLevel && station.station_id === selectedStation ? waterLevel : null;
                const statusText = wl
                    ? wl > 4 ? '🔴 Kritik' : wl > 3 ? '🟡 Diqqat' : '🟢 Xavfsiz'
                    : '🟢 Xavfsiz';

                infoWindowRef.current.setContent(`
                    <div style="
                        background: #0F172A;
                        color: #FFFFFF;
                        padding: 12px 16px;
                        border-radius: 8px;
                        font-family: Inter, system-ui, sans-serif;
                        min-width: 200px;
                        border: 1px solid #1E293B;
                    ">
                        <div style="font-size: 1rem; font-weight: 700; color: #38BDF8; margin-bottom: 6px;">
                            📍 ${station.station_name}
                        </div>
                        <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 4px;">
                            🌊 Daryo: <strong style="color:#FFFFFF">${station.river_name}</strong>
                        </div>
                        <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 8px;">
                            📍 ${station.latitude.toFixed(4)}°N, ${station.longitude.toFixed(4)}°E
                        </div>
                        <div style="
                            display: inline-block;
                            padding: 3px 10px;
                            border-radius: 999px;
                            font-size: 0.8rem;
                            font-weight: 700;
                            background: #1E293B;
                            color: #FFFFFF;
                            border: 1px solid #334155;
                        ">${statusText}</div>
                    </div>
                `);
                infoWindowRef.current.open(map, marker);
            });

            markersRef.current.push(marker);
        });

        // Fit bounds to all stations
        if (stations.length > 0) {
            const bounds = new window.google.maps.LatLngBounds();
            stations.forEach(s => {
                if (s.latitude && s.longitude) {
                    bounds.extend({ lat: s.latitude, lng: s.longitude });
                }
            });
            if (!bounds.isEmpty()) {
                map.fitBounds(bounds, { top: 40, right: 40, bottom: 40, left: 40 });
            }
        }
    }, [stations, selectedStation, waterLevel, onStationSelect]);

    /* Initialize map when Google Maps script is ready */
    useEffect(() => {
        const tryInit = () => {
            if (window.google && window.google.maps) {
                initMap();
            } else {
                setTimeout(tryInit, 200);
            }
        };
        tryInit();
    }, [initMap]);

    /* Update marker styles when selection changes */
    useEffect(() => {
        if (!mapInstanceRef.current || !window.google) return;
        markersRef.current.forEach((marker, i) => {
            const station = stations[i];
            if (!station) return;
            const color = getMarkerColor(station.station_id, selectedStation, waterLevel);
            const isSelected = station.station_id === selectedStation;
            marker.setIcon({
                path: window.google.maps.SymbolPath.CIRCLE,
                scale: isSelected ? 12 : 8,
                fillColor: color,
                fillOpacity: 1,
                strokeColor: '#FFFFFF',
                strokeWeight: isSelected ? 2.5 : 1.5,
            });
            marker.setAnimation(isSelected ? window.google.maps.Animation.BOUNCE : null);
            marker.setZIndex(isSelected ? 100 : 1);

            // Pan to selected station
            if (isSelected && station.latitude && station.longitude) {
                mapInstanceRef.current.panTo({ lat: station.latitude, lng: station.longitude });
                mapInstanceRef.current.setZoom(10);
            }
        });
    }, [selectedStation, waterLevel, stations]);

    return (
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
            <div ref={mapRef} style={{ width: '100%', height: '100%', minHeight: '520px' }} />
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
                zIndex: 10,
                pointerEvents: 'none',
            }}>
                🗺️ O'zbekiston Gidropost Tarmog'i — {stations.length} ta stansiya
            </div>
            {/* Legend — Google Maps style */}
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
                zIndex: 10,
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
                        <svg width="14" height="14" viewBox="0 0 14 14">
                            <circle cx="7" cy="7" r="6" fill={color} stroke="#FFFFFF" strokeWidth="1.5" />
                        </svg>
                        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#FFFFFF', whiteSpace: 'nowrap' }}>{label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GMap;
