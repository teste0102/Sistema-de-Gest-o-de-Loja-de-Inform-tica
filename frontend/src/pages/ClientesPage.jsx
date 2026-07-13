import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col } from 'react-bootstrap';
import api from '../services/api';

export default function ClientesPage() {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    carregarClientes();
  }, []);

  const carregarClientes = async () => {
    try {
      setLoading(true);
      const data = await api.get('/api/clientes/');
      setClientes(data.items || []);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center">
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h1>👥 Clientes</h1>
        </Col>
        <Col className="text-end">
          <Button
            variant="primary"
            onClick={() => setShowForm(!showForm)}
          >
            ➕ Novo Cliente
          </Button>
        </Col>
      </Row>

      {showForm && (
        <Card className="mb-4">
          <Card.Header>Formulário de Novo Cliente</Card.Header>
          <Card.Body>
            <p>Formulário em desenvolvimento...</p>
          </Card.Body>
        </Card>
      )}

      <Card>
        <Card.Header>
          <input
            type="text"
            placeholder="🔍 Buscar cliente..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="form-control"
          />
        </Card.Header>
        <Card.Body>
          <Table hover responsive>
            <thead>
              <tr>
                <th>Código</th>
                <th>Nome</th>
                <th>Telefone</th>
                <th>Email</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {clientes
                .filter((c) =>
                  c.nome.toLowerCase().includes(search.toLowerCase())
                )
                .map((cliente) => (
                  <tr key={cliente.id}>
                    <td>{cliente.codigo}</td>
                    <td>{cliente.nome}</td>
                    <td>{cliente.telefone}</td>
                    <td>{cliente.email}</td>
                    <td>
                      <Button size="sm" variant="outline-primary">
                        ✏️
                      </Button>
                      {' '}
                      <Button size="sm" variant="outline-danger">
                        🗑️
                      </Button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </Table>
          {clientes.length === 0 && (
            <p className="text-center text-muted">Nenhum cliente encontrado</p>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}
