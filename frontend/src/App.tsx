import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NetworkView from './pages/NetworkView';
import Predictions from './pages/Predictions';
import About from './pages/About';
import './components/GlassStyles.css';
import './App.css';

function App() {
    return (
        <Router>
            <div className="app">
                {/* Header */}
                <header className="app-header">
                    <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <h1 className="text-2xl font-bold text-white">
                                🌊 GIMAT
                            </h1>
                            <p className="text-sm text-blue-200 hidden md:block">
                                Gidrologik Intellektual Monitoring va Axborot Tizimi
                            </p>
                        </div>

                        <nav className="flex space-x-6">
                            <Link to="/" className="nav-link">Dashboard</Link>
                            <Link to="/network" className="nav-link">Tarmoq</Link>
                            <Link to="/predictions" className="nav-link">Prognozlar</Link>
                            <Link to="/about" className="nav-link">Haqida</Link>
                        </nav>
                    </div>
                </header>

                {/* Main Content */}
                <main className="app-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/network" element={<NetworkView />} />
                        <Route path="/predictions" element={<Predictions />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                </main>

                {/* Footer */}
                <footer className="app-footer">
                    {/* AI Technology Badge Strip */}
                    <div className="footer-badge-strip">
                        <span className="footer-badge-label">🧠 AI Texnologiyalar:</span>
                        <div className="footer-badges">
                            <span className="ft-badge ft-badge-blue">Wavelet</span>
                            <span className="ft-badge ft-badge-blue">SARIMA</span>
                            <span className="ft-badge ft-badge-purple">Bi-LSTM</span>
                            <span className="ft-badge ft-badge-purple">GNN</span>
                            <span className="ft-badge ft-badge-green">XAI</span>
                            <span className="ft-badge ft-badge-green">RAG</span>
                            <span className="ft-badge ft-badge-yellow">Neo4j</span>
                        </div>
                    </div>

                    {/* Author Block */}
                    <div className="footer-author-block">
                        <div className="footer-author-info">
                            <span className="footer-author-icon">👨‍🎓</span>
                            <div>
                                <div className="footer-author-name">Rustamjon Nasridinov</div>
                                <div className="footer-author-title">PhD Student · Ixtisoslik: 05.01.10 · TATU</div>
                            </div>
                        </div>
                        <Link to="/about" className="footer-detail-btn">
                            Batafsil ma'lumot →
                        </Link>
                    </div>

                    {/* Copyright */}
                    <div className="footer-copyright">
                        <p>© 2026 GIMAT Platform — Gidrologik Intellektual Monitoring va Axborot Tizimi</p>
                    </div>
                </footer>
            </div>
        </Router>
    );
}

export default App;
