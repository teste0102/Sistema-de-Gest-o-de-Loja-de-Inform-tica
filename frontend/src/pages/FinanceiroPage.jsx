import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col, Badge } from 'react-bootstrap';
import api from '../services/api';

export default function FinanceiroPage() {
  const [lancamentos, setLancamentos] = useState([]);
  const [saldo, setSaldo] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [lancamentosRes, saldoRes] = await Promise.all([
        api.get('/api/financeiro/'),
        api.get('/api/financeiro/relatorio/saldo'),
      ]);
      setLancamentos(lancamentosRes.items || []);
      setSaldo(saldoRes);
    } catch (error) {
      console.error('Erro ao carregar financeiro:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTipoBadge = (tipo) => {
    return tipo === 'receita' ? (
      <Badge bg="success">{tipo}</Badge>
    ) : (
      <Badge bg="danger">{tipo}</Badge>
    );
  };

  if (loading) {
    return <Spinner animation="border" />;
  }

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h1>💰 Financeiro</h1>
        </Col>
        <Col className="text-end">
          <Button variant="success" className="me-2">
            ➕ Receita
          </Button>
          <Button variant="danger">➕ Despesa</Button>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={4}>
          <Card>
            <Card.Body>
              <h6>Receita Total</h6>
              <h2 className="text-success">
                R$ {(saldo.receita_total || 0).toFixed(2)}
              </h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Body>
              <h6>Despesa Total</h6>
              <h2 className="text-danger">
                R$ {(saldo.despesa_total || 0).toFixed(2)}
              </h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Body>
              <h6>Saldo</h6>
              <h2 className={saldo.saldo >= 0 ? 'text-success' : 'text-danger'}>
                R$ {(saldo.saldo || 0).toFixed(2)}
              </h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Body>
          <Table hover responsive>
            <thead>
              <tr>
                <th>Data</th>
                <th>Tipo</th>
                <th>Categoria</th>
                <th>Descrição</th>
                <th>Valor</th>
                <th>Forma de Pagamento</th>
              </tr>
            </thead>
            <tbody>
              {lancamentos.map((lancamento) => (
                <tr key={lancamento.id}>
                  <td>{new Date(lancamento.data).toLocaleDateString()}</td>
                  <td>{getTipoBadge(lancamento.tipo)}</td>
                  <td>{lancamento.categoria}</td>
                  <td>{lancamento.descricao}</td>
                  <td>R$ {lancamento.valor?.toFixed(2)}</td>
                  <td>{lancamento.forma_pagamento}</td>
                </tr>
              ))}
            </tbody>
          </Table>
          {lancamentos.length === 0 && <p className="text-center">Sem lançamentos</p>}
        </Card.Body>
      </Card>
    </Container>
  );
}
