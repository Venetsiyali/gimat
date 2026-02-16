import React, { useState, useEffect } from 'react';
import { predictionAPI, dataAPI } from '../services/api';
import './Predictions.css';

interface Model {
    model_name: string;
    description: string;
    status: string;
    accuracy_nse: number;
}

const Predictions: React.FC = () => {
    const [stations, setStations] = useState<any[]>([]);
    const [models, setModels] = useState<Model[]>([]);
    const [selectedStation, setSelectedStation] = useState<string>('');
    const [selectedModel, setSelectedModel] = useState<string>('hybrid');
    const [forecastDays, setForecastDays] = useState<number>(7);
    const [loading, setLoading] = useState(false);
    const [forecast, setForecast] = useState<any>(null);
    const [evaluation, setEvaluation] = useState<any>(null);

    useEffect(() => {
        loadInitialData();
    }, []);

    useEffect(() => {
        if (selectedStation && selectedModel) {
            loadEvaluation();
        }
    }, [selectedStation, selectedModel]);

    const loadInitialData = async () => {
        try {
            const [stationsResp, modelsResp] = await Promise.all([
                dataAPI.getStations(),
                predictionAPI.getModels(),
            ]);

            setStations(stationsResp.data);
            setModels(modelsResp.data);

            if (stationsResp.data.length > 0) {
                setSelectedStation(stationsResp.data[0].station_id);
            }
        } catch (error) {
            console.error('Error loading data:', error);
        }
    };

    const loadEvaluation = async () => {
        try {
            const response = await predictionAPI.getEvaluation(selectedStation, selectedModel);
            setEvaluation(response.data);
        } catch (error) {
            console.error('Error loading evaluation:', error);
        }
    };

    const handleGenerateForecast = async () => {
        setLoading(true);
        try {
            const response = await predictionAPI.createForecast({
                station_id: selectedStation,
                forecast_horizon_days: forecastDays,
                model_name: selectedModel,
            });
            setForecast(response.data);
        } catch (error) {
            console.error('Error generating forecast:', error);
            alert('Xatolik: Prognoz yaratilmadi');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-4">
            <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2">Prognozlar</h2>
                <p className="text-gray-600">Gibrid AI modellari asosida bashorat</p>
            </div>

            {/* Configuration */}
            <div className="card mb-6">
                <h3 className="text-lg font-bold mb-4">Konfiguratsiya</h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Gidropost:</label>
                        <select
                            className="w-full p-2 border rounded-lg"
                            value={selectedStation}
                            onChange={(e) => setSelectedStation(e.target.value)}
                        >
                            {stations.map((station) => (
                                <option key={station.station_id} value={station.station_id}>
                                    {station.station_name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Model:</label>
                        <select
                            className="w-full p-2 border rounded-lg"
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                        >
                            {models.map((model) => (
                                <option key={model.model_name} value={model.model_name}>
                                    {model.model_name.toUpperCase()}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Kunlar:</label>
                        <input
                            type="number"
                            className="w-full p-2 border rounded-lg"
                            value={forecastDays}
                            onChange={(e) => setForecastDays(Number(e.target.value))}
                            min="1"
                            max="30"
                        />
                    </div>
                </div>

                <button
                    className="mt-4 btn-primary"
                    onClick={handleGenerateForecast}
                    disabled={loading}
                >
                    {loading ? 'Yuklanmoqda...' : '🔮 Prognoz yaratish'}
                </button>
            </div>

            {/* Model Info */}
            {models.find(m => m.model_name === selectedModel) && (
                <div className="card mb-6">
                    <h3 className="text-lg font-bold mb-2">Model Ma'lumoti</h3>
                    <p className="text-gray-600 mb-2">
                        {models.find(m => m.model_name === selectedModel)?.description}
                    </p>
                    <div className="flex items-center space-x-4 text-sm">
                        <span className="bg-green-100 text-green-800 px-3 py-1 rounded">
                            NSE: {models.find(m => m.model_name === selectedModel)?.accuracy_nse.toFixed(2)}
                        </span>
                        <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded">
                            Status: {models.find(m => m.model_name === selectedModel)?.status}
                        </span>
                    </div>
                </div>
            )}

            {/* Evaluation Metrics */}
            {evaluation && evaluation.metrics && (
                <div className="card mb-6">
                    <h3 className="text-lg font-bold mb-4">Baholash Metrikalari</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-gray-500">NSE</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {evaluation.metrics.NSE?.toFixed(3)}
                            </p>
                            <p className="text-xs text-gray-400">Nash-Sutcliffe</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">KGE</p>
                            <p className="text-2xl font-bold text-green-600">
                                {evaluation.metrics.KGE?.toFixed(3)}
                            </p>
                            <p className="text-xs text-gray-400">Kling-Gupta</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">RMSE</p>
                            <p className="text-2xl font-bold text-orange-600">
                                {evaluation.metrics.RMSE?.toFixed(2)}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">MAE</p>
                            <p className="text-2xl font-bold text-purple-600">
                                {evaluation.metrics.MAE?.toFixed(2)}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Forecast Results */}
            {forecast && (
                <div className="card">
                    <h3 className="text-lg font-bold mb-4">Prognoz Natijalari</h3>
                    <p className="text-sm text-gray-600 mb-4">{forecast.message}</p>

                    <div className="overflow-x-auto">
                        <table className="min-w-full">
                            <thead>
                                <tr className="border-b">
                                    <th className="px-4 py-2 text-left">Sana</th>
                                    <th className="px-4 py-2 text-right">Sarfi (m³/s)</th>
                                    <th className="px-4 py-2 text-right">Sath (m)</th>
                                    <th className="px-4 py-2 text-right">Ishonch oralig'i</th>
                                </tr>
                            </thead>
                            <tbody>
                                {forecast.predictions?.map((pred: any, idx: number) => (
                                    <tr key={idx} className="border-b hover:bg-gray-50">
                                        <td className="px-4 py-2">
                                            {new Date(pred.timestamp).toLocaleDateString('uz-UZ')}
                                        </td>
                                        <td className="px-4 py-2 text-right font-semibold">
                                            {pred.predicted_discharge?.toFixed(1)}
                                        </td>
                                        <td className="px-4 py-2 text-right font-semibold">
                                            {pred.predicted_water_level?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-2 text-right text-sm text-gray-500">
                                            [{pred.lower_bound?.toFixed(1)} - {pred.upper_bound?.toFixed(1)}]
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* AI Models Info */}
            <div className="mt-8 card bg-gradient-to-r from-indigo-50 to-purple-50">
                <h3 className="text-lg font-bold mb-2">🤖 Gibrid Ensemble</h3>
                <p className="text-sm text-gray-600 mb-3">
                    GIMAT tizimi vaqt qatorlarini veyvlet dekompozitsiyasi yordamida
                    approksimatsiya va detalizatsiya komponentlariga ajratadi, keyin har bir
                    komponent uchun eng mos modelni qo'llaydi:
                </p>
                <ul className="text-sm space-y-1">
                    <li>• <strong>SARIMA</strong>: Approksimatsiya (trend) komponentlari uchun</li>
                    <li>• <strong>Bi-LSTM</strong>: Detalizatsiya (fluktuatsiya) komponentlari uchun</li>
                    <li>• <strong>Transformer</strong>: Uzoq muddatli bog'liqliklar uchun</li>
                    <li>• <strong>GNN</strong>: Fazoviy-topologik modellash uchun</li>
                </ul>
            </div>
        </div>
    );
};

export default Predictions;
