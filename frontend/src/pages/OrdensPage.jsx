import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col, Badge } from 'react-bootstrap';
import api from '../services/api';

export default function OrdensPage() {
  const [ordens, setOrdens] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarOrdens();
  }, []);

  const carregarOrdens = async () => {
    try {
      setLoading(true);
      const data = await api.get('/api/ordens/');
      setOrdens(data.items || []);
    } catch (error) {
      console.error('Erro ao carregar ordens:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      aberto: 'warning',
      fechado: 'success',
      suspenso: 'danger',
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  if (loading) {
    return <Spinner animation="border" />;
  }

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h1>📋 Ordens de Serviço</h1>
        </Col>
        <Col className="text-end">
          <Button variant="primary">➕ Nova Ordem</Button>
        </Col>
      </Row>

      <Card>
        <Card.Body>
          <Table hover responsive>
            <thead>
              <tr>
                <th>Nº</th>
                <th>Cliente</th>
                <th>Data</th>
                <th>Status</th>
                <th>Valor</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {ordens.map((ordem) => (
                <tr key={ordem.id}>
                  <td>#{ordem.numero}</td>
                  <td>{ordem.cliente?.nome}</td>
                  <td>{new Date(ordem.data_abertura).toLocaleDateString()}</td>
                  <td>{getStatusBadge(ordem.status)}</td>
                  <td>R$ {ordem.valor_total?.toFixed(2)}</td>
                  <td>
                    <Button size="sm" variant="outline-primary">
                      ✏️
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
          {ordens.length === 0 && <p className="text-center">Sem ordens</p>}
        </Card.Body>
      </Card>
    </Container>
  );
}
