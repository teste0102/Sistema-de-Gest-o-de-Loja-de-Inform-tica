import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Row, Col, Form, Alert, Table, Badge, Spinner } from 'react-bootstrap';
import api from '../services/api';

export default function SincronizacaoPage() {
  const [fila, setFila] = useState([]);
  const [estrategias, setEstrategias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState(null);

  // Form servidor
  const [nome, setNome] = useState('');
  const [url, setUrl] = useState('');
  const [chaveApi, setChaveApi] = useState('');

  useEffect(() => {
    carregarTudo();
  }, []);

  const flash = (variant, texto) => {
    setMsg({ variant, texto });
    setTimeout(() => setMsg(null), 5000);
  };

  const carregarTudo = async () => {
    try {
      setLoading(true);
      const [filaRes, estrRes] = await Promise.all([
        api.get('/api/sync/fila').catch(() => null),
        api.get('/api/sync/estrategias').catch(() => null),
      ]);
      if (filaRes) setFila(filaRes.itens || []);
      if (estrRes) setEstrategias(estrRes.estrategias || []);
    } catch (e) {
      console.error('Erro ao carregar sincronização:', e);
    } finally {
      setLoading(false);
    }
  };

  const registrarServidor = async () => {
    if (!nome || !url || !chaveApi) return flash('warning', 'Preencha todos os campos');
    try {
      await api.post('/api/sync/servidores', {
        nome,
        url,
        chave_api: chaveApi,
        ativo: true,
      });
      flash('success', `Servidor "${nome}" registrado com sucesso`);
      setNome('');
      setUrl('');
      setChaveApi('');
      carregarTudo();
    } catch (e) {
      flash('danger', `Erro ao registrar servidor: ${e.response?.data?.detail || e.message}`);
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
          <h1>🔄 Sincronização Multi-Servidor</h1>
          <p className="text-muted">Arquitetura offline-first com resolução de conflitos</p>
        </Col>
        <Col className="text-end">
          <Button variant="outline-primary" onClick={carregarTudo}>
            🔄 Atualizar
          </Button>
        </Col>
      </Row>

      {msg && <Alert variant={msg.variant}>{msg.texto}</Alert>}

      {/* Cards de Status */}
      <Row>
        <Col md={4} className="mb-4">
          <Card className="text-center">
            <Card.Body>
              <h6>Fila de Sincronização</h6>
              <h2>{fila.length}</h2>
              <small className="text-muted">Itens na fila</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="text-center">
            <Card.Body>
              <h6>Pendentes</h6>
              <h2>{fila.filter((i) => !i.sincronizado).length}</h2>
              <small className="text-muted">Aguardando sync</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="text-center">
            <Card.Body>
              <h6>Estratégias</h6>
              <h2>{estrategias.length}</h2>
              <small className="text-muted">Resolução de conflitos</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        {/* Registrar Servidor */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>🖥️ Registrar Servidor Remoto</Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Nome</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Ex: Servidor Filial 2"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>URL</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Ex: http://192.168.1.100:8000"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Chave API</Form.Label>
                <Form.Control
                  type="password"
                  placeholder="Chave de autenticação"
                  value={chaveApi}
                  onChange={(e) => setChaveApi(e.target.value)}
                />
              </Form.Group>
              <Button variant="primary" onClick={registrarServidor}>
                ➕ Registrar Servidor
              </Button>
            </Card.Body>
          </Card>
        </Col>

        {/* Estratégias */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>⚙️ Estratégias de Resolução de Conflitos</Card.Header>
            <Card.Body>
              {estrategias.length > 0 ? (
                <ul className="mb-0">
                  {estrategias.map((e) => (
                    <li key={e}>
                      <Badge bg="secondary">{e}</Badge>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted mb-0">Nenhuma estratégia disponível</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Fila de Sincronização */}
      <Card>
        <Card.Header>📋 Fila de Sincronização</Card.Header>
        <Card.Body>
          <Table hover responsive size="sm">
            <thead>
              <tr>
                <th>Tabela</th>
                <th>Operação</th>
                <th>Registro ID</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {fila.map((item, idx) => (
                <tr key={idx}>
                  <td>{item.tabela}</td>
                  <td>{item.operacao}</td>
                  <td>{item.registro_id}</td>
                  <td>
                    {item.sincronizado ? (
                      <Badge bg="success">Sincronizado</Badge>
                    ) : (
                      <Badge bg="warning">Pendente</Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
          {fila.length === 0 && (
            <p className="text-center text-muted mb-0">Fila vazia — tudo sincronizado ✅</p>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}
