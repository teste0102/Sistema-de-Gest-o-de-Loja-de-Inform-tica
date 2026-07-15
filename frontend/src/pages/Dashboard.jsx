import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Spinner } from 'react-bootstrap';
import api from '../services/api';
import '../styles/Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState({
    clientes: 0,
    ordens: 0,
    financeiro: {},
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarEstatisticas();
  }, []);

  const carregarEstatisticas = async () => {
    try {
      setLoading(true);
      const [clientesRes, ordensRes, financeiroRes] = await Promise.all([
        api.get('/api/clientes/stats/total'),
        api.get('/api/ordens/stats/resumo'),
        api.get('/api/financeiro/relatorio/saldo'),
      ]);

      setStats({
        clientes: clientesRes.total_ativos || 0,
        ordens: ordensRes.total_aberto || 0,
        financeiro: financeiroRes,
      });
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Carregando...</span>
        </Spinner>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1 className="mb-4">📊 Dashboard</h1>

      <Row>
        <Col md={6} lg={3} className="mb-4">
          <Card className="stat-card clients">
            <Card.Body>
              <h6>Clientes Ativos</h6>
              <h2>{stats.clientes}</h2>
              <small>Total de clientes</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-4">
          <Card className="stat-card orders">
            <Card.Body>
              <h6>Ordens Abertas</h6>
              <h2>{stats.ordens}</h2>
              <small>Aguardando fechamento</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-4">
          <Card className="stat-card revenue">
            <Card.Body>
              <h6>Receita</h6>
              <h2>R$ {(stats.financeiro.receita_total || 0).toFixed(2)}</h2>
              <small>Receitas totais</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3} className="mb-4">
          <Card className="stat-card balance">
            <Card.Body>
              <h6>Saldo</h6>
              <h2 className={stats.financeiro.saldo >= 0 ? 'text-success' : 'text-danger'}>
                R$ {(stats.financeiro.saldo || 0).toFixed(2)}
              </h2>
              <small>Saldo atual</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-4">
        <Col lg={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Ações Rápidas</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <a href="/clientes" className="btn btn-outline-primary">
                  ➕ Novo Cliente
                </a>
                <a href="/ordens" className="btn btn-outline-primary">
                  📋 Nova Ordem
                </a>
                <a href="/os" className="btn btn-outline-primary">
                  🔧 Ferramentas OS (Senha / Fotos / Laudo)
                </a>
                <a href="/financeiro" className="btn btn-outline-primary">
                  💰 Lançar Receita
                </a>
                <a href="/sincronizacao" className="btn btn-outline-primary">
                  🔄 Sincronização Multi-Servidor
                </a>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Informações do Sistema</h5>
            </Card.Header>
            <Card.Body>
              <p>
                <strong>Versão:</strong> 1.0.0
              </p>
              <p>
                <strong>Status:</strong>{' '}
                <span className="badge bg-success">Operacional</span>
              </p>
              <p>
                <strong>Última atualização:</strong> {new Date().toLocaleDateString('pt-BR')}
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
