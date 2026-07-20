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
  const [modoSync, setModoSync] = useState('local'); // 'local' | 'ssh'
  const [mdbStatus, setMdbStatus] = useState(null);
  const [subpasta, setSubpasta] = useState('');
  const [scan, setScan] = useState(null);
  const [tabelas, setTabelas] = useState(null);
  const [arquivoSel, setArquivoSel] = useState(null);
  const [preview, setPreview] = useState(null);
  const [carregandoMdb, setCarregandoMdb] = useState(false);

  // Conexão SSH / Rede
  const [ssh, setSsh] = useState({ host: '', porta: 22, usuario: '', senha: '', caminho: '.' });
  const [redeBase, setRedeBase] = useState('192.168.0');
  const [redeHosts, setRedeHosts] = useState(null);
  const [escaneandoRede, setEscaneandoRede] = useState(false);

  // Sincronização automática entre terminais (dois lados)
  const [auto, setAuto] = useState(null);
  const [sincronizandoAgora, setSincronizandoAgora] = useState(false);

  useEffect(() => {
    carregarTudo();
    verificarMdb();
    carregarAuto();
  }, []);

  const carregarAuto = async () => {
    try {
      const res = await api.get('/api/sync-auto/config');
      setAuto(res.config);
    } catch (e) { /* silencioso */ }
  };

  const salvarAuto = async (patch = {}) => {
    try {
      const corpo = { ...auto, ...patch };
      // não reenvia a senha mascarada
      if (corpo.ssh_senha === '***') delete corpo.ssh_senha;
      const res = await api.put('/api/sync-auto/config', corpo);
      setAuto(res.config);
      flash('success', 'Configuração salva.');
    } catch (e) {
      flash('danger', `Erro ao salvar: ${e.response?.data?.detail || e.message}`);
    }
  };

  const sincronizarAgora = async () => {
    try {
      setSincronizandoAgora(true);
      const res = await api.post('/api/sync-auto/agora', {});
      flash('success', res.mensagem || 'Sincronizado!');
      carregarAuto();
    } catch (e) {
      flash('danger', `Erro: ${e.response?.data?.detail || e.message}`);
    } finally {
      setSincronizandoAgora(false);
    }
  };

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

  // ===== Descoberta de rede (procura IPs com SSH/compartilhamento) =====
  const escanearRede = async () => {
    try {
      setEscaneandoRede(true);
      setRedeHosts(null);
      const res = await api.post('/api/sync/mdb/rede/descobrir', { base: redeBase });
      if (res.ok) {
        setRedeHosts(res.hosts || []);
        if (!res.hosts || res.hosts.length === 0) flash('warning', `Nenhum host encontrado em ${res.base}.x`);
      } else {
        flash('danger', res.erro || 'Falha ao escanear a rede');
      }
    } catch (e) {
      flash('danger', `Erro ao escanear rede: ${e.response?.data?.detail || e.message}`);
    } finally {
      setEscaneandoRede(false);
    }
  };

  // ===== SSH / Rede =====
  const escanearSsh = async (caminho) => {
    const alvo = caminho !== undefined ? caminho : ssh.caminho;
    try {
      setCarregandoMdb(true);
      setTabelas(null); setPreview(null); setArquivoSel(null);
      const res = await api.post('/api/sync/mdb/ssh/escanear', { ...ssh, caminho: alvo });
      setScan(res);
      setSsh((s) => ({ ...s, caminho: alvo }));
      if (!res.ok) flash('danger', res.erro || 'Falha ao escanear via SSH');
    } catch (e) {
      flash('danger', `Erro SSH: ${e.response?.data?.detail || e.message}`);
    } finally {
      setCarregandoMdb(false);
    }
  };

  const abrirTabelasSsh = async (arquivoNome) => {
    try {
      setCarregandoMdb(true);
      setPreview(null);
      setArquivoSel(arquivoNome);
      const res = await api.post('/api/sync/mdb/ssh/tabelas', { ...ssh, arquivo: arquivoNome });
      setTabelas(res);
      if (!res.ok) flash('warning', res.erro);
    } catch (e) {
      flash('danger', `Erro SSH tabelas: ${e.response?.data?.detail || e.message}`);
    } finally {
      setCarregandoMdb(false);
    }
  };

  const verPreviewSsh = async (tabela) => {
    try {
      setCarregandoMdb(true);
      const res = await api.post('/api/sync/mdb/ssh/preview', { ...ssh, arquivo: arquivoSel, tabela });
      setPreview(res);
      if (!res.ok) flash('warning', res.erro);
    } catch (e) {
      flash('danger', `Erro SSH preview: ${e.response?.data?.detail || e.message}`);
    } finally {
      setCarregandoMdb(false);
    }
  };

  // Handlers unificados (chamam local ou ssh conforme o modo)
  const doTabelas = (arq) => (modoSync === 'ssh' ? abrirTabelasSsh(arq) : abrirTabelas(arq));
  const doPreview = (tab) => (modoSync === 'ssh' ? verPreviewSsh(tab) : verPreview(tab));
  const doEntrarPasta = (sp) => (modoSync === 'ssh'
    ? escanearSsh(ssh.caminho === '.' ? sp : `${ssh.caminho}/${sp}`)
    : escanear(subpasta ? `${subpasta}/${sp}` : sp));

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

      {/* ===== SINCRONIZAÇÃO AUTOMÁTICA ENTRE TERMINAIS (DOIS LADOS) ===== */}
      <Card className="mb-4 border-success">
        <Card.Header className="bg-success text-white d-flex justify-content-between align-items-center">
          <span>🔁 Sincronização Automática entre Terminais (dois lados)</span>
          {auto && <Badge bg={auto.ativo ? 'light' : 'secondary'} text={auto.ativo ? 'success' : 'light'}>
            {auto.ativo ? 'LIGADA' : 'Desligada'}
          </Badge>}
        </Card.Header>
        <Card.Body>
          {!auto ? (
            <div className="text-muted">Carregando configuração...</div>
          ) : (
            <>
              <p className="text-muted mb-3">
                Aponte a pasta compartilhada (rede) ou o outro PC (SSH). O sistema envia o que
                mudou aqui e traz o que mudou lá, automaticamente. Vence sempre a última edição.
              </p>

              <Row className="g-2 mb-3">
                <Col md={3}>
                  <Form.Label>Este terminal</Form.Label>
                  <Form.Control value={auto.terminal_id || ''} readOnly size="sm" />
                </Col>
                <Col md={3}>
                  <Form.Label>Como conectar</Form.Label>
                  <Form.Select size="sm" value={auto.modo || 'pasta'} onChange={(e) => setAuto({ ...auto, modo: e.target.value })}>
                    <option value="pasta">📁 Pasta na rede</option>
                    <option value="ssh">🔐 Outro PC (SSH)</option>
                  </Form.Select>
                </Col>
                <Col md={3}>
                  <Form.Label>Sincronizar a cada (min)</Form.Label>
                  <Form.Control type="number" min="1" size="sm" value={auto.intervalo_min || 5}
                    onChange={(e) => setAuto({ ...auto, intervalo_min: Number(e.target.value) })} />
                </Col>
                <Col md={3} className="d-flex align-items-end">
                  <Form.Check type="switch" id="auto-ativo" label="Automático ligado"
                    checked={!!auto.ativo} onChange={(e) => setAuto({ ...auto, ativo: e.target.checked })} />
                </Col>
              </Row>

              {auto.modo === 'ssh' ? (
                <Row className="g-2 mb-3">
                  <Col md={4}><Form.Label>IP do outro PC</Form.Label>
                    <Form.Control size="sm" placeholder="192.168.0.10" value={auto.ssh_host || ''} onChange={(e) => setAuto({ ...auto, ssh_host: e.target.value })} /></Col>
                  <Col md={2}><Form.Label>Porta</Form.Label>
                    <Form.Control size="sm" value={auto.ssh_porta || 22} onChange={(e) => setAuto({ ...auto, ssh_porta: Number(e.target.value) })} /></Col>
                  <Col md={3}><Form.Label>Usuário</Form.Label>
                    <Form.Control size="sm" value={auto.ssh_usuario || ''} onChange={(e) => setAuto({ ...auto, ssh_usuario: e.target.value })} /></Col>
                  <Col md={3}><Form.Label>Senha</Form.Label>
                    <Form.Control size="sm" type="password" placeholder={auto.ssh_senha === '***' ? '•••• (salva)' : ''} onChange={(e) => setAuto({ ...auto, ssh_senha: e.target.value })} /></Col>
                  <Col md={12}><Form.Label>Pasta compartilhada no outro PC</Form.Label>
                    <Form.Control size="sm" placeholder="ex.: C:/loja/sync ou ." value={auto.ssh_caminho || ''} onChange={(e) => setAuto({ ...auto, ssh_caminho: e.target.value })} /></Col>
                </Row>
              ) : (
                <Row className="g-2 mb-3">
                  <Col md={12}><Form.Label>Pasta compartilhada (na rede, montada na pasta de dados)</Form.Label>
                    <Form.Control size="sm" placeholder="ex.: sync (vazio = pasta padrão de dados/sync)" value={auto.pasta_local || ''} onChange={(e) => setAuto({ ...auto, pasta_local: e.target.value })} />
                    <small className="text-muted">Os dois terminais devem apontar para a MESMA pasta compartilhada.</small>
                  </Col>
                </Row>
              )}

              <div className="d-flex gap-2 align-items-center">
                <Button variant="success" onClick={() => salvarAuto()}>💾 Salvar configuração</Button>
                <Button variant="outline-success" onClick={sincronizarAgora} disabled={sincronizandoAgora}>
                  {sincronizandoAgora ? (<><Spinner size="sm" animation="border" /> Sincronizando...</>) : '🔁 Sincronizar agora'}
                </Button>
                {auto.ultima_sync && (
                  <span className="text-muted small ms-2">
                    Última: {new Date(auto.ultima_sync).toLocaleString('pt-BR')} — {auto.ultimo_status}
                  </span>
                )}
              </div>
            </>
          )}
        </Card.Body>
      </Card>

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
            )}
          </div>

          {/* Seletor de modo: Local x SSH/Rede */}
          <div className="d-flex gap-2 mb-3">
            <Button
              variant={modoSync === 'local' ? 'primary' : 'outline-primary'}
              onClick={() => { setModoSync('local'); setScan(null); setTabelas(null); setPreview(null); }}
            >
              💻 Pasta Local
            </Button>
            <Button
              variant={modoSync === 'ssh' ? 'primary' : 'outline-primary'}
              onClick={() => { setModoSync('ssh'); setScan(null); setTabelas(null); setPreview(null); }}
            >
              🌐 Servidor SSH / Rede
            </Button>
          </div>

          {/* MODO LOCAL */}
          {modoSync === 'local' && (
            <div className="mb-3">
              <Form.Label className="small text-muted">
                Pasta montada no servidor: <code>{mdbStatus?.mdb_dir || '/dados_mdb'}</code>{' '}
                (aponte com <code>MDB_PATH</code> no <code>.env</code>, ex.: <code>MDB_PATH=C:/Users/User/Desktop/Informatica2023</code>)
              </Form.Label>
              <Row className="g-2">
                <Col md={8}>
                  <Form.Control
                    placeholder="Subpasta (opcional). Ex.: Backup 02.01.2026 — vazio = raiz"
                    value={subpasta}
                    onChange={(e) => setSubpasta(e.target.value)}
                  />
                </Col>
                <Col md={4}>
                  <Button variant="primary" className="w-100" onClick={() => escanear(subpasta)} disabled={carregandoMdb}>
                    {carregandoMdb ? <Spinner size="sm" /> : '🔍 Escanear'}
                  </Button>
                </Col>
              </Row>
            </div>
          )}

          {/* MODO SSH / REDE */}
          {modoSync === 'ssh' && (
            <div className="mb-3">
              {/* Passo 1: escanear a rede procurando IPs */}
              <div className="p-2 mb-3" style={{ background: '#f0f7ff', borderRadius: 6 }}>
                <div className="small fw-bold mb-2">1️⃣ Procurar máquinas na rede</div>
                <Row className="g-2 align-items-end">
                  <Col md={6}>
                    <Form.Label className="small mb-1">Faixa da rede (os 3 primeiros números do seu IP)</Form.Label>
                    <Form.Control value={redeBase} onChange={(e) => setRedeBase(e.target.value)} placeholder="Ex.: 192.168.0" />
                  </Col>
                  <Col md={6}>
                    <Button variant="info" className="w-100" onClick={escanearRede} disabled={escaneandoRede}>
                      {escaneandoRede ? <Spinner size="sm" /> : '🔎 Escanear Rede'}
                    </Button>
                  </Col>
                </Row>
                <small className="text-muted">Dica: no Windows, veja seu IP com <code>ipconfig</code> (ex.: 192.168.0.15 → digite 192.168.0).</small>

                {redeHosts && redeHosts.length > 0 && (
                  <div className="mt-2">
                    <div className="small fw-bold">Máquinas encontradas ({redeHosts.length}) — clique para usar:</div>
                    <div className="d-flex flex-wrap gap-1 mt-1">
                      {redeHosts.map((h) => (
                        <Button key={h.ip} size="sm"
                          variant={ssh.host === h.ip ? 'primary' : 'outline-primary'}
                          onClick={() => setSsh({ ...ssh, host: h.ip })}>
                          🖥️ {h.ip} {h.ssh ? '🔑SSH' : ''} {h.compartilhamento ? '📁' : ''}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="small fw-bold mb-2">2️⃣ Conectar (IP escolhido + usuário e senha)</div>
              <Row className="g-2">
                <Col md={5}>
                  <Form.Control placeholder="Host / IP (ex.: 192.168.0.10)" value={ssh.host}
                    onChange={(e) => setSsh({ ...ssh, host: e.target.value })} />
                </Col>
                <Col md={2}>
                  <Form.Control type="number" placeholder="Porta" value={ssh.porta}
                    onChange={(e) => setSsh({ ...ssh, porta: e.target.value })} />
                </Col>
                <Col md={5}>
                  <Form.Control placeholder="Usuário" value={ssh.usuario}
                    onChange={(e) => setSsh({ ...ssh, usuario: e.target.value })} />
                </Col>
                <Col md={5}>
                  <Form.Control type="password" placeholder="Senha" value={ssh.senha}
                    onChange={(e) => setSsh({ ...ssh, senha: e.target.value })} />
                </Col>
                <Col md={5}>
                  <Form.Control placeholder="Caminho remoto (ex.: /home/user/Informatica2023 ou . )" value={ssh.caminho}
                    onChange={(e) => setSsh({ ...ssh, caminho: e.target.value })} />
                </Col>
                <Col md={2}>
                  <Button variant="primary" className="w-100" onClick={() => escanearSsh()} disabled={carregandoMdb}>
                    {carregandoMdb ? <Spinner size="sm" /> : '🔍 Conectar'}
                  </Button>
                </Col>
              </Row>
              <small className="text-muted">Conecta via SSH/SFTP e baixa os .mdb temporariamente para leitura. Funciona em qualquer rede.</small>
            </div>
          )}

          {scan?.ok && (
            <Row>
              {/* Subpastas + arquivos */}
              <Col md={5}>
                <h6>📁 Pasta: <code>{scan.pasta_atual}</code></h6>
                {scan.subpastas?.length > 0 && (
                  <div className="mb-2">
                    {scan.subpastas.map((sp) => (
                      <Button key={sp} size="sm" variant="outline-secondary" className="me-1 mb-1"
                        onClick={() => doEntrarPasta(sp)}>
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
                            <Button size="sm" variant="outline-primary" onClick={() => doTabelas(a.nome)}>
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
                          onClick={() => doPreview(t)}>
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
