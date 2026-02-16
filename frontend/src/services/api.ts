import axios from 'axios';
import API_BASE_URL from '../config';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Data API
export const dataAPI = {
    getObservations: (params?: any) => api.get('/api/data/observations', { params }),
    getStations: () => api.get('/api/data/stations'),
    getLatestObservation: (stationId: string) => api.get(`/api/data/stations/${stationId}/latest`),
    getTimeSeries: (stationId: string, params: any) => api.get(`/api/data/timeseries/${stationId}`, { params }),
    getStatistics: (stationId: string, params?: any) => api.get(`/api/data/stations/${stationId}/statistics`, { params }),
};

// Prediction API
export const predictionAPI = {
    getPredictions: (stationId: string, params?: any) => api.get(`/api/predictions/predictions/${stationId}`, { params }),
    createForecast: (data: any) => api.post('/api/predictions/forecast', data),
    getModels: () => api.get('/api/predictions/models'),
    getEvaluation: (stationId: string, modelName: string) =>
        api.get(`/api/predictions/evaluation/${stationId}`, { params: { model_name: modelName } }),
};

// Ontology API
export const ontologyAPI = {
    getNetwork: (riverName: string) => api.get(`/api/ontology/network/${riverName}`),
    getUpstreamStations: (stationId: string) => api.get(`/api/ontology/hydroposts/${stationId}/upstream`),
    getDownstreamStations: (stationId: string) => api.get(`/api/ontology/hydroposts/${stationId}/downstream`),
    getBasins: () => api.get('/api/ontology/basins'),
    getStatistics: () => api.get('/api/ontology/statistics'),
};

export default api;
