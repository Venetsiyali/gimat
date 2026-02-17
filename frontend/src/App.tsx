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
                    <div className="container mx-auto px-4 py-6 text-center">
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>© 2026 GIMAT Platform</p>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>Yaratuvchi: Venetsiyali</p>
                    </div>
                </footer>
            </div>
        </Router>
    );
}

export default App;
