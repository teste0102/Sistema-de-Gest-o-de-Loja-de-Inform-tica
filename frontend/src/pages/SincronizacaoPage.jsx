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

  // Scanner de arquivos Access (.mdb)
  const [mdbStatus, setMdbStatus] = useState(null);
  const [subpasta, setSubpasta] = useState('');
  const [scan, setScan] = useState(null);
  const [tabelas, setTabelas] = useState(null);
  const [arquivoSel, setArquivoSel] = useState(null);
  const [preview, setPreview] = useState(null);
  const [carregandoMdb, setCarregandoMdb] = useState(false);

  useEffect(() => {
    carregarTudo();
    verificarMdb();
  }, []);

  const verificarMdb = async () => {
    try {
      const res = await api.get('/api/sync/mdb/status');
      setMdbStatus(res);
    } catch (e) {
      setMdbStatus(null);
    }
  };

  const escanear = async (pasta = '') => {
    try {
      setCarregandoMdb(true);
      setTabelas(null); setPreview(null); setArquivoSel(null);
      const res = await api.get(`/api/sync/mdb/escanear?subpasta=${encodeURIComponent(pasta)}`);
      setScan(res);
      setSubpasta(pasta);
      if (!res.ok) flash('warning', res.erro || 'Pasta não encontrada');
    } catch (e) {
      flash('danger', `Erro ao escanear: ${e.response?.data?.detail || e.message}`);
    } finally {
      setCarregandoMdb(false);
    }
  };

  const abrirTabelas = async (arquivoNome) => {
    const caminho = subpasta ? `${subpasta}/${arquivoNome}` : arquivoNome;
    try {
      setCarregandoMdb(true);
      setPreview(null);
      setArquivoSel(caminho);
      const res = await api.get(`/api/sync/mdb/tabelas?arquivo=${encodeURIComponent(caminho)}`);
      setTabelas(res);
      if (!res.ok) flash('warning', res.erro);
    } catch (e) {
      flash('danger', `Erro ao ler tabelas: ${e.response?.data?.detail || e.message}`);
    } finally {
      setCarregandoMdb(false);
    }
  };

  const verPreview = async (tabela) => {
    try {
      setCarregandoMdb(true);
      const res = await api.get(`/api/sync/mdb/preview?arquivo=${encodeURIComponent(arquivoSel)}&tabela=${encodeURIComponent(tabela)}`);
      setPreview(res);
      if (!res.ok) flash('warning', res.erro);
    } catch (e) {
      flash('danger', `Erro no preview: ${e.response?.data?.detail || e.message}`);
    } finally {
      setCarregandoMdb(false);
    }
  };

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

      {/* ===== SCANNER DE ARQUIVOS ACCESS (.mdb) ===== */}
      <Card className="mb-4 border-primary">
        <Card.Header className="bg-primary text-white">
          📂 Sincronizar do Sistema Antigo (Access .mdb)
        </Card.Header>
        <Card.Body>
          <div className="mb-3 small">
            {mdbStatus?.mdbtools_disponivel ? (
              <Badge bg="success">✅ Leitor .mdb ativo</Badge>
            ) : (
              <Badge bg="danger">❌ Leitor .mdb indisponível</Badge>
            )}{' '}
            <span className="text-muted">
              Pasta montada no servidor: <code>{mdbStatus?.mdb_dir || '/dados_mdb'}</code>
            </span>
          </div>

          <Alert variant="light" className="small">
            Para apontar a pasta da rede: defina <code>MDB_PATH</code> no arquivo <code>.env</code> (ex.:
            <code> MDB_PATH=C:\Users\User\Desktop\Informatica2023</code> ou uma pasta de rede mapeada) e reconstrua o backend.
          </Alert>

          <div className="d-flex gap-2 mb-3 flex-wrap">
            <Button variant="primary" onClick={() => escanear('')} disabled={carregandoMdb}>
              {carregandoMdb ? <Spinner size="sm" /> : '🔍 Escanear Pasta'}
            </Button>
            {subpasta && (
              <Button variant="outline-secondary" onClick={() => escanear('')}>⬆️ Voltar à raiz</Button>
            )}
          </div>

          {scan?.ok && (
            <Row>
              {/* Subpastas + arquivos */}
              <Col md={5}>
                <h6>📁 Pasta: <code>{scan.pasta_atual}</code></h6>
                {scan.subpastas?.length > 0 && (
                  <div className="mb-2">
                    {scan.subpastas.map((sp) => (
                      <Button key={sp} size="sm" variant="outline-secondary" className="me-1 mb-1"
                        onClick={() => escanear(subpasta ? `${subpasta}/${sp}` : sp)}>
                        📁 {sp}
                      </Button>
                    ))}
                  </div>
                )}
                <div style={{ maxHeight: 300, overflowY: 'auto' }}>
                  <Table hover size="sm">
                    <thead><tr><th>Arquivo .mdb ({scan.total_mdb})</th><th>Tabelas</th></tr></thead>
                    <tbody>
                      {scan.arquivos.map((a) => (
                        <tr key={a.nome}>
                          <td>{a.nome} <small className="text-muted">({Math.round(a.tamanho/1024)} KB)</small></td>
                          <td>
                            <Button size="sm" variant="outline-primary" onClick={() => abrirTabelas(a.nome)}>
                              ver tabelas
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Col>

              {/* Tabelas do arquivo selecionado */}
              <Col md={3}>
                {tabelas?.ok && (
                  <>
                    <h6>🗂️ Tabelas de<br /><code className="small">{arquivoSel}</code></h6>
                    <div style={{ maxHeight: 300, overflowY: 'auto' }}>
                      {tabelas.tabelas.map((t) => (
                        <Button key={t} size="sm" variant="outline-info" className="d-block w-100 mb-1 text-start"
                          onClick={() => verPreview(t)}>
                          {t}
                        </Button>
                      ))}
                    </div>
                  </>
                )}
              </Col>

              {/* Preview dos dados */}
              <Col md={4}>
                {preview?.ok && (
                  <>
                    <h6>👁️ Amostra: <Badge bg="info">{preview.tabela}</Badge></h6>
                    <div style={{ maxHeight: 300, overflowY: 'auto', fontSize: 11 }}>
                      <Table bordered size="sm">
                        <thead><tr>{preview.colunas.slice(0, 4).map((c) => <th key={c}>{c}</th>)}</tr></thead>
                        <tbody>
                          {preview.linhas.map((linha, i) => (
                            <tr key={i}>{linha.slice(0, 4).map((v, j) => <td key={j}>{String(v).substring(0, 20)}</td>)}</tr>
                          ))}
                        </tbody>
                      </Table>
                    </div>
                    <small className="text-muted">{preview.total_colunas} colunas · amostra de {preview.total_amostra} linhas</small>
                  </>
                )}
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>

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
