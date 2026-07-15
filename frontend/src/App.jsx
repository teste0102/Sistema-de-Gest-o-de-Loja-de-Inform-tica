import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, Navbar, Nav, Alert } from 'react-bootstrap';
import './App.css';

// Páginas
import Dashboard from './pages/Dashboard';
import ClientesPage from './pages/ClientesPage';
import OrdensPage from './pages/OrdensPage';
import FinanceiroPage from './pages/FinanceiroPage';
import OSPage from './pages/OSPage';
import SincronizacaoPage from './pages/SincronizacaoPage';

function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Detectar conexão online/offline
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Verificar saúde da API
    checkApiHealth();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setApiStatus('online');
      } else {
        setApiStatus('offline');
      }
    } catch (error) {
      setApiStatus('offline');
    }
  };

  return (
    <Router>
      <div className="App">
        {/* Navbar */}
        <Navbar bg="dark" expand="lg" sticky="top">
          <Container>
            <Navbar.Brand href="/">
              💼 Loja de Informática
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="ms-auto">
                <Nav.Link href="/">Dashboard</Nav.Link>
                <Nav.Link href="/clientes">Clientes</Nav.Link>
                <Nav.Link href="/ordens">Ordens</Nav.Link>
                <Nav.Link href="/os">Ferramentas OS</Nav.Link>
                <Nav.Link href="/financeiro">Financeiro</Nav.Link>
                <Nav.Link href="/sincronizacao">Sincronização</Nav.Link>
              </Nav>
              <div className="ms-3">
                <span className={`badge ${isOnline ? 'bg-success' : 'bg-danger'}`}>
                  {isOnline ? '🟢 Online' : '🔴 Offline'}
                </span>
              </div>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        {/* Alert de Status */}
        <Container className="mt-3">
          {!isOnline && (
            <Alert variant="warning" dismissible>
              ⚠️ Você está offline. Mudanças serão sincronizadas quando reconectar.
            </Alert>
          )}
          {apiStatus === 'offline' && isOnline && (
            <Alert variant="danger" dismissible>
              ❌ API não está respondendo. Conecte a `http://localhost:8000`
            </Alert>
          )}
        </Container>

        {/* Rotas */}
        <Container className="mt-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/ordens" element={<OrdensPage />} />
            <Route path="/os" element={<OSPage />} />
            <Route path="/financeiro" element={<FinanceiroPage />} />
            <Route path="/sincronizacao" element={<SincronizacaoPage />} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;
