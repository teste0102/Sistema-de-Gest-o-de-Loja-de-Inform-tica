import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col, Modal, Form, Alert } from 'react-bootstrap';
import api from '../services/api';

export default function ClientesPage() {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const [msg, setMsg] = useState(null);
  const [importando, setImportando] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [imp, setImp] = useState({
    modo: 'local', subpasta: '', arquivo: 'CADA.MDB', tabela: 'CADA',
    host: '', porta: 22, usuario: '', senha: '', caminho: '.',
  });

  useEffect(() => {
    carregarClientes();
  }, []);

  const carregarClientes = async () => {
    try {
      setLoading(true);
      const data = await api.get('/api/clientes/?limit=100');
      setClientes(data.items || []);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const importarAccess = async () => {
    try {
      setImportando(true);
      setMsg(null);
      let r;
      if (imp.modo === 'ssh') {
        r = await api.post('/api/clientes/importar-mdb-ssh', {
          host: imp.host, porta: Number(imp.porta) || 22, usuario: imp.usuario,
          senha: imp.senha, caminho: imp.caminho || '.', arquivo: imp.arquivo, tabela: imp.tabela,
        });
      } else {
        r = await api.post('/api/clientes/importar-mdb', {
          subpasta: imp.subpasta, arquivo: imp.arquivo, tabela: imp.tabela,
        });
      }
      setShowImport(false);
      setMsg({ tipo: 'success', texto: `Importação: ${r.total_lidos} lidos, ${r.criados} criados, ${r.atualizados} atualizados.` });
      carregarClientes();
    } catch (e) {
      setMsg({ tipo: 'danger', texto: `Falha: ${e?.response?.data?.detail || e.message}` });
    } finally {
      setImportando(false);
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
          <Button variant="success" className="me-2" onClick={() => setShowImport(true)} disabled={importando}>
            📥 Importar do Access
          </Button>
          <Button
            variant="primary"
            onClick={() => setShowForm(!showForm)}
          >
            ➕ Novo Cliente
          </Button>
        </Col>
      </Row>

      {msg && <Alert variant={msg.tipo} dismissible onClose={() => setMsg(null)}>{msg.texto}</Alert>}

      <Modal show={showImport} onHide={() => setShowImport(false)}>
        <Modal.Header closeButton><Modal.Title>📥 Importar clientes do Access</Modal.Title></Modal.Header>
        <Modal.Body>
          <div className="mb-3 d-flex gap-2">
            <Button variant={imp.modo === 'local' ? 'primary' : 'outline-primary'} size="sm"
              onClick={() => setImp({ ...imp, modo: 'local' })}>📁 Pasta na rede</Button>
            <Button variant={imp.modo === 'ssh' ? 'primary' : 'outline-primary'} size="sm"
              onClick={() => setImp({ ...imp, modo: 'ssh' })}>🔐 Outro PC (SSH)</Button>
          </div>
          {imp.modo === 'local' ? (
            <>
              <Form.Label>Subpasta compartilhada (vazio = raiz)</Form.Label>
              <Form.Control className="mb-2" placeholder="ex.: Backup 02.01.2026"
                value={imp.subpasta} onChange={(e) => setImp({ ...imp, subpasta: e.target.value })} />
            </>
          ) : (
            <Row className="g-2">
              <Col md={8}><Form.Label>IP</Form.Label>
                <Form.Control placeholder="192.168.0.10" value={imp.host} onChange={(e) => setImp({ ...imp, host: e.target.value })} /></Col>
              <Col md={4}><Form.Label>Porta</Form.Label>
                <Form.Control value={imp.porta} onChange={(e) => setImp({ ...imp, porta: e.target.value })} /></Col>
              <Col md={6}><Form.Label>Usuário</Form.Label>
                <Form.Control value={imp.usuario} onChange={(e) => setImp({ ...imp, usuario: e.target.value })} /></Col>
              <Col md={6}><Form.Label>Senha</Form.Label>
                <Form.Control type="password" value={imp.senha} onChange={(e) => setImp({ ...imp, senha: e.target.value })} /></Col>
              <Col md={12}><Form.Label>Pasta do arquivo no outro PC</Form.Label>
                <Form.Control placeholder="ex.: C:/loja/dados ou ." value={imp.caminho} onChange={(e) => setImp({ ...imp, caminho: e.target.value })} /></Col>
            </Row>
          )}
          <Row className="g-2 mt-1">
            <Col md={6}><Form.Label>Arquivo</Form.Label>
              <Form.Control value={imp.arquivo} onChange={(e) => setImp({ ...imp, arquivo: e.target.value })} /></Col>
            <Col md={6}><Form.Label>Tabela</Form.Label>
              <Form.Control value={imp.tabela} onChange={(e) => setImp({ ...imp, tabela: e.target.value })} /></Col>
          </Row>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImport(false)}>Cancelar</Button>
          <Button variant="success" onClick={importarAccess} disabled={importando}>
            {importando ? (<><Spinner size="sm" animation="border" /> Importando...</>) : '📥 Importar'}
          </Button>
        </Modal.Footer>
      </Modal>

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
