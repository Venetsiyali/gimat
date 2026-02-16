import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NetworkView from './pages/NetworkView';
import Predictions from './pages/Predictions';
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
                        </nav>
                    </div>
                </header>

                {/* Main Content */}
                <main className="app-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route to="/network" element={<NetworkView />} />
                        <Route path="/predictions" element={<Predictions />} />
                    </Routes>
                </main>

                {/* Footer */}
                <footer className="app-footer">
                    <div className="container mx-auto px-4 py-4 text-center text-gray-600">
                        <p>© 2024 GIMAT - PhD Dissertatsiya Loyihasi</p>
                    </div>
                </footer>
            </div>
        </Router>
    );
}

export default App;
