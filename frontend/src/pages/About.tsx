import React from 'react';
import './About.css';

const About: React.FC = () => {
    return (
        <div className="about-container-dark">
            {/* Hero Section */}
            <div className="about-hero-dark">
                <div className="hero-glow"></div>
                <h1 className="about-title-dark gradient-text fade-in">
                    <span className="title-icon">👨‍🎓</span>
                    Dastur yaratuvchisi
                </h1>
                <p className="about-subtitle-dark fade-in">GIMAT loyihasi muallifi va ilmiy tadqiqotchi</p>
                <div className="neon-divider"></div>
            </div>

            <div className="about-content-dark">
                {/* Main Creator Info - Featured Card */}
                <div className="creator-main-card card glow fade-in">
                    <div className="creator-header">
                        <div className="creator-avatar">
                            <span className="avatar-icon">🎓</span>
                        </div>
                        <div className="creator-title-section">
                            <h2 className="creator-name gradient-text">Rustamjon Nasridinov</h2>
                            <p className="creator-position">Assistent-o'qituvchi, Tayanch doktorant (PhD Student)</p>
                        </div>
                    </div>

                    <div className="creator-details">
                        <div className="detail-item">
                            <span className="detail-icon">🏛️</span>
                            <div>
                                <strong>Tashkilot:</strong>
                                <p>Muhammad al-Xorazmiy nomidagi Toshkent axborot texnologiyalari universiteti (TATU)</p>
                            </div>
                        </div>
                        <div className="detail-item">
                            <span className="detail-icon">📚</span>
                            <div>
                                <strong>Kafedra:</strong>
                                <p>"Axborot va ta'lim texnologiyalari" kafedrasi, "Kasbiy ta'lim" fakulteti</p>
                            </div>
                        </div>
                        <div className="detail-item">
                            <span className="detail-icon">🎓</span>
                            <div>
                                <strong>Ilmiy maqom:</strong>
                                <p>Tayanch doktorant (PhD Student) — Assistent-o'qituvchi</p>
                            </div>
                        </div>
                    </div>

                    {/* Specialization Highlight Block */}
                    <div className="specialization-block">
                        <div className="spec-label">🔬 Ilmiy ixtisoslik</div>
                        <div className="spec-code">05.01.10</div>
                        <div className="spec-title">Axborot qidirish va olish</div>
                        <div className="research-topic">
                            <div className="research-topic-label">📖 Dissertatsiya mavzusi</div>
                            <div className="research-topic-text">
                                "Gidrologik ko'rsatkichlar dinamikasini vaqt qatorlarida monitoring qilishning gibrid modellari va intellektual axborot tizimi"
                            </div>
                        </div>
                    </div>
                </div>

                {/* PhD Research Section */}
                <div className="card neon-border fade-in" style={{ animationDelay: '0.1s' }}>
                    <div className="section-header">
                        <span className="section-icon">📊</span>
                        <h2 className="section-title">Dissertatsiya tadqiqoti</h2>
                    </div>
                    <div className="research-content">
                        <h3 className="research-title gradient-text">
                            "Gidrologik ko'rsatkichlar dinamikasini vaqt qatorlarida monitoring qilishning gibrid modellari va intellektual axborot tizimi"
                        </h3>
                        <div className="research-objectives">
                            <h4 className="objectives-title">Tadqiqotning asosiy maqsadi:</h4>
                            <div className="objective-grid">
                                <div className="objective-item">
                                    <span className="objective-number">01</span>
                                    <div className="objective-content">
                                        <h5>AI-powered Prognozlash</h5>
                                        <p>O'zbekiston daryolari va suv havzalarida gidrologik jarayonlarni sun'iy intellekt (LSTM, GNN, Wavelet) yordamida aniq bashorat qilish</p>
                                    </div>
                                </div>
                                <div className="objective-item">
                                    <span className="objective-number">02</span>
                                    <div className="objective-content">
                                        <h5>Intellektual Monitoring Tizimi</h5>
                                        <p>Real-time monitoring, tahlil va qaror qabul qilishni qo'llab-quvvatlovchi zamonaviy platforma yaratish</p>
                                    </div>
                                </div>
                                <div className="objective-item">
                                    <span className="objective-number">03</span>
                                    <div className="objective-content">
                                        <h5>Gibrid Model Integratsiyasi</h5>
                                        <p>SARIMA, Bi-LSTM, GNN va Wavelet-tahlil modellarini birlashtirib, yuqori aniqlikdagi prognoz tizimini ishlab chiqish</p>
                                    </div>
                                </div>
                                <div className="objective-item">
                                    <span className="objective-number">04</span>
                                    <div className="objective-content">
                                        <h5>Knowledge Graph va XAI</h5>
                                        <p>Gidrologik bilimlar grafini (Neo4j) va tushuntirilishi mumkin AI (SHAP/LIME) orqali qarorlarning shaffofligini ta'minlash</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Achievements */}
                <div className="card fade-in" style={{ animationDelay: '0.2s' }}>
                    <div className="section-header">
                        <span className="section-icon">🏆</span>
                        <h2 className="section-title">Yutuqlar va loyihalar</h2>
                    </div>
                    <div className="achievements-grid">
                        <div className="achievement-card">
                            <div className="achievement-badge">🥈</div>
                            <h4>Agrobank AI500! Hackathon 2025</h4>
                            <p>Finalchi - AI texnologiyalarini qishloq xo'jaligida qo'llash</p>
                        </div>
                        <div className="achievement-card">
                            <div className="achievement-badge">🤖</div>
                            <h4>AI Solutions</h4>
                            <p>Machine Learning va Deep Learning loyihalarini ishlab chiqish</p>
                        </div>
                        <div className="achievement-card">
                            <div className="achievement-badge">🥽</div>
                            <h4>VR/AR Technologies</h4>
                            <p>Virtual va Augmented Reality ta'lim platformalari</p>
                        </div>
                        <div className="achievement-card">
                            <div className="achievement-badge">💧</div>
                            <h4>Gidroinformatika</h4>
                            <p>Suv resurslarini boshqarishda AI tatbiqi</p>
                        </div>
                    </div>
                </div>

                {/* Tech Stack */}
                <div className="card fade-in" style={{ animationDelay: '0.3s' }}>
                    <div className="section-header">
                        <span className="section-icon">⚙️</span>
                        <h2 className="section-title">GIMAT platformasi texnologiyalari</h2>
                    </div>
                    <div className="tech-stack-dark">
                        <div className="tech-category-dark">
                            <h4>🔧 Backend</h4>
                            <div className="tech-tags-dark">
                                <span className="tech-tag-dark">Python 3.11</span>
                                <span className="tech-tag-dark">FastAPI</span>
                                <span className="tech-tag-dark">PostgreSQL</span>
                                <span className="tech-tag-dark">Redis</span>
                                <span className="tech-tag-dark">Celery</span>
                            </div>
                        </div>
                        <div className="tech-category-dark">
                            <h4>🧠 AI/ML Models</h4>
                            <div className="tech-tags-dark">
                                <span className="tech-tag-dark glow">SARIMA</span>
                                <span className="tech-tag-dark glow">Bi-LSTM</span>
                                <span className="tech-tag-dark glow">GNN</span>
                                <span className="tech-tag-dark glow">Wavelet</span>
                                <span className="tech-tag-dark glow">SHAP/LIME</span>
                            </div>
                        </div>
                        <div className="tech-category-dark">
                            <h4>💻 Frontend</h4>
                            <div className="tech-tags-dark">
                                <span className="tech-tag-dark">React 18</span>
                                <span className="tech-tag-dark">TypeScript</span>
                                <span className="tech-tag-dark">Recharts</span>
                                <span className="tech-tag-dark">D3.js</span>
                            </div>
                        </div>
                        <div className="tech-category-dark">
                            <h4>🌐 Knowledge AI</h4>
                            <div className="tech-tags-dark">
                                <span className="tech-tag-dark">Neo4j</span>
                                <span className="tech-tag-dark">RAG</span>
                                <span className="tech-tag-dark">ChromaDB</span>
                                <span className="tech-tag-dark">LangChain</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Mission & Vision */}
                <div className="mission-card card neon-border fade-in" style={{ animationDelay: '0.4s' }}>
                    <div className="mission-content">
                        <h3 className="gradient-text">🎯 GIMAT loyihasi missiyasi</h3>
                        <p className="mission-text">
                            O'zbekiston suv resurslarini boshqarish va gidrologik monitoring sohasida zamonaviy sun'iy intellekt texnologiyalarini tatbiq etish orqali aniq va ishonchli bashorat tizimini yaratish.
                            Bu tizim suv havzalari xavfsizligini ta'minlash, qurg'oqchilik va toshqin xavfini oldindan aniqlash,
                            shuningdek ilmiy tadqiqotlar uchun kuchli asos yaratishga xizmat qiladi.
                        </p>
                        <div className="mission-stats">
                            <div className="stat-item">
                                <span className="stat-value gradient-text">4</span>
                                <span className="stat-label">AI Modellari</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-value gradient-text">30+</span>
                                <span className="stat-label">Gidropostlar</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-value gradient-text">24/7</span>
                                <span className="stat-label">Real-time Monitoring</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Contact */}
                <div className="contact-card-dark card fade-in" style={{ animationDelay: '0.5s' }}>
                    <div className="section-header">
                        <span className="section-icon">📧</span>
                        <h2 className="section-title">Aloqa va hamkorlik</h2>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: '1.8' }}>
                        Loyiha bo'yicha takliflar, hamkorlik va ilmiy muloqot uchun:
                    </p>
                    <div className="contact-links">
                        <a href="https://github.com/Venetsiyali/gimat" className="contact-link-dark pulse" target="_blank" rel="noopener noreferrer">
                            <span className="link-icon">🔗</span>
                            <span>GitHub Repository</span>
                        </a>
                        <a href="mailto:rustamjon.nasridinov@tatu.uz" className="contact-link-dark pulse" target="_blank" rel="noopener noreferrer">
                            <span className="link-icon">📧</span>
                            <span>Email: rustamjon.nasridinov@tatu.uz</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
