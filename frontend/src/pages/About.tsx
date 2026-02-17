import React from 'react';
import './About.css';

const About: React.FC = () => {
    return (
        <div className="about-container">
            <div className="about-hero">
                <h1 className="about-title fade-in">Yaratuvchi haqida</h1>
                <p className="about-subtitle fade-in">GIMAT platformasini ishlab chiquvchi</p>
            </div>

            <div className="about-content">
                {/* Creator Info */}
                <div className="about-card fade-in">
                    <div className="card-icon gradient-primary">👨‍💻</div>
                    <h2 className="card-title">Loyiha muallifi</h2>
                    <div className="creator-info">
                        <p><strong>Ism:</strong> Venetsiyali</p>
                        <p><strong>Mutaxassislik:</strong> AI/ML Engineer, Hydrological Data Scientist</p>
                        <p><strong>Maqsad:</strong> Gidrologiya sohasida AI va zamonaviy texnologiyalarni tatbiq etish</p>
                    </div>
                </div>

                {/* Project Info */}
                <div className="about-card fade-in" style={{ animationDelay: '0.1s' }}>
                    <div className="card-icon gradient-success">🚀</div>
                    <h2 className="card-title">Loyiha haqida</h2>
                    <p className="card-description">
                        <strong>GIMAT</strong> (Gidrologik Intellektual Monitoring va Axborot Tizimi) —
                        O'zbekiston daryolaridagi suv oqimi va boshqa gidrologik parametrlarni real vaqtda
                        monitoring qilish, tahlil qilish va prognozlash uchun mo'ljallangan zamonaviy platforma.
                    </p>
                    <p className="card-description">
                        Tizim gibrid AI modellar (SARIMA, Bi-LSTM, GNN), Wavelet-tahlil, XAI va Knowledge Graph
                        texnologiyalaridan foydalanadi.
                    </p>
                </div>

                {/* Tech Stack */}
                <div className="about-card fade-in" style={{ animationDelay: '0.2s' }}>
                    <div className="card-icon gradient-warning">⚙️</div>
                    <h2 className="card-title">Texnologiyalar</h2>
                    <div className="tech-grid">
                        <div className="tech-category">
                            <h3 className="tech-heading">Backend</h3>
                            <div className="tech-tags">
                                <span className="tech-tag">Python</span>
                                <span className="tech-tag">FastAPI</span>
                                <span className="tech-tag">PostgreSQL</span>
                                <span className="tech-tag">Redis</span>
                            </div>
                        </div>
                        <div className="tech-category">
                            <h3 className="tech-heading">AI/ML</h3>
                            <div className="tech-tags">
                                <span className="tech-tag">SARIMA</span>
                                <span className="tech-tag">BiLSTM</span>
                                <span className="tech-tag">GNN</span>
                                <span className="tech-tag">SHAP</span>
                            </div>
                        </div>
                        <div className="tech-category">
                            <h3 className="tech-heading">Frontend</h3>
                            <div className="tech-tags">
                                <span className="tech-tag">React</span>
                                <span className="tech-tag">TypeScript</span>
                                <span className="tech-tag">Recharts</span>
                                <span className="tech-tag">D3.js</span>
                            </div>
                        </div>
                        <div className="tech-category">
                            <h3 className="tech-heading">Knowledge AI</h3>
                            <div className="tech-tags">
                                <span className="tech-tag">Neo4j</span>
                                <span className="tech-tag">RAG</span>
                                <span className="tech-tag">Wavelet</span>
                                <span className="tech-tag">XAI</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Features */}
                <div className="about-card fade-in" style={{ animationDelay: '0.3s' }}>
                    <div className="card-icon gradient-secondary">✨</div>
                    <h2 className="card-title">Asosiy imkoniyatlar</h2>
                    <div className="features-list">
                        <div className="feature-item">
                            <span className="feature-icon">📊</span>
                            <div className="feature-content">
                                <h4>Real-time Monitoring</h4>
                                <p>Suv sathi, sarfi va haroratni onlayn kuzatish</p>
                            </div>
                        </div>
                        <div className="feature-item">
                            <span className="feature-icon">🎯</span>
                            <div className="feature-content">
                                <h4>AI Prognozlash</h4>
                                <p>Gibrid modellar asosida aniq bashorat</p>
                            </div>
                        </div>
                        <div className="feature-item">
                            <span className="feature-icon">🔍</span>
                            <div className="feature-content">
                                <h4>XAI Tahlil</h4>
                                <p>Model qarorlarini tushunish va izohlab berish</p>
                            </div>
                        </div>
                        <div className="feature-item">
                            <span className="feature-icon">🌐</span>
                            <div className="feature-content">
                                <h4>Knowledge Graph</h4>
                                <p>Daryo, suv ombori va GES bog'liqliklarini visual ko'rsatish</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Contact */}
                <div className="about-card contact-card fade-in" style={{ animationDelay: '0.4s' }}>
                    <h2 className="card-title">Aloqa</h2>
                    <p className="card-description">
                        Loyiha bo'yicha takliflar va hamkorlik uchun:
                    </p>
                    <div className="contact-info">
                        <a href="https://github.com/Venetsiyali/gimat" className="contact-link" target="_blank" rel="noopener noreferrer">
                            <span className="contact-icon">🔗</span>
                            GitHub Repository
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
