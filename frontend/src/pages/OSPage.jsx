import React, { useState } from 'react';
import { Container, Card, Button, Row, Col, Form, Tabs, Tab, Alert, Table, Badge, Spinner } from 'react-bootstrap';
import api from '../services/api';
import PatternDraw from '../components/PatternDraw';
import NovaOSWizard from '../components/NovaOSWizard';

export default function OSPage() {
  // Estado geral
  const [ordemId, setOrdemId] = useState('');
  const [ordemAtiva, setOrdemAtiva] = useState(null);
  const [msg, setMsg] = useState(null);

  // Gerar número OS
  const [clienteId, setClienteId] = useState('');
  const [gerando, setGerando] = useState(false);

  // Senha
  const [senhaTipo, setSenhaTipo] = useState('pin');
  const [senhaValor, setSenhaValor] = useState('');
  const [senhaInfo, setSenhaInfo] = useState(null);

  // Fotos
  const [fotos, setFotos] = useState([]);
  const [arquivo, setArquivo] = useState(null);
  const [descricaoFoto, setDescricaoFoto] = useState('');

  // Laudo
  const [laudo, setLaudo] = useState(null);
  const [obsLaudo, setObsLaudo] = useState('');

  // Padrão (Desenho de Senha)
  const [mostrarPattern, setMostrarPattern] = useState(false);
  const [patternData, setPatternData] = useState(null);
  const [patternReplay, setPatternReplay] = useState(null);

  // Assistente (Wizard) de cadastro/alteração
  const [mostrarWizard, setMostrarWizard] = useState(false);
  const [wizardDados, setWizardDados] = useState(null); // null = novo, objeto = alterar

  // Modo da tela: 'nova' abre direto no assistente (endereço); 'existente' carrega OS
  const [modo, setModo] = useState('nova');
  const [wizardKey, setWizardKey] = useState(0); // recria o assistente ao cancelar

  const flash = (variant, texto) => {
    setMsg({ variant, texto });
    setTimeout(() => setMsg(null), 5000);
  };

  // ===== NÚMERO OS =====
  const gerarNumeroOS = async () => {
    if (!clienteId) return flash('warning', 'Informe o ID do cliente');
    try {
      setGerando(true);
      const res = await api.post(`/api/os/gerar-numero?cliente_id=${clienteId}`);
      flash('success', `OS gerada: ${res.numero_os}. Preencha o assistente.`);
      setOrdemId(String(res.ordem_id));
      setOrdemAtiva(res);
      // Abrir o assistente (novo cadastro)
      setWizardDados(null);
      setMostrarWizard(true);
    } catch (e) {
      flash('danger', `Erro ao gerar OS: ${e.response?.data?.detail || e.message}`);
    } finally {
      setGerando(false);
    }
  };

  const carregarOS = async () => {
    if (!ordemId) return flash('warning', 'Informe o ID da OS');
    try {
      const res = await api.get(`/api/os/${ordemId}`);
      setOrdemAtiva(res);
      flash('success', `OS ${res.numero_os} carregada`);
      // Carregar recursos vinculados
      carregarFotos();
      carregarSenha();
      carregarLaudo();
    } catch (e) {
      flash('danger', `Erro ao carregar OS: ${e.response?.data?.detail || e.message}`);
      setOrdemAtiva(null);
    }
  };

  // ===== ASSISTENTE (WIZARD) =====
  // Abrir em modo Alterar: carrega dados atuais e abre o wizard preenchido
  const abrirAlterar = async () => {
    if (!ordemId) return flash('warning', 'Carregue uma OS primeiro');
    try {
      const res = await api.get(`/api/os/${ordemId}`);
      setOrdemAtiva(res);
      setWizardDados(res);
      setMostrarWizard(true);
    } catch (e) {
      flash('danger', `Erro ao abrir alteração: ${e.response?.data?.detail || e.message}`);
    }
  };

  // Ao concluir o assistente: fecha e recarrega a OS
  const aoConcluirWizard = () => {
    setMostrarWizard(false);
    setWizardDados(null);
    carregarOS();
  };

  // Carregar uma OS por ID explícito (usado após criar no assistente)
  const carregarOSPorId = async (id) => {
    try {
      const res = await api.get(`/api/os/${id}`);
      setOrdemId(String(id));
      setOrdemAtiva(res);
    } catch (e) {
      flash('danger', `Erro ao carregar OS ${id}: ${e.response?.data?.detail || e.message}`);
    }
  };

  // Concluir o assistente no modo NOVA: cria a OS e mostra ela em "existente"
  const aoConcluirNova = (novoId) => {
    setModo('existente');
    if (novoId) carregarOSPorId(novoId);
    setWizardKey((k) => k + 1); // reseta o assistente para a próxima
  };

  // ===== SENHA =====
  const carregarSenha = async () => {
    if (!ordemId) return;
    try {
      const res = await api.get(`/api/os/${ordemId}/senhas`);
      setSenhaInfo(res);
    } catch (e) {
      setSenhaInfo(null);
    }
  };

  const criarSenha = async () => {
    if (!ordemId) return flash('warning', 'Carregue uma OS primeiro');
    try {
      const body = { tipo: senhaTipo };
      if (senhaTipo === 'pin') body.valor = senhaValor;
      await api.post(`/api/os/${ordemId}/senhas`, body);
      flash('success', `Senha ${senhaTipo} criada com sucesso`);
      setSenhaValor('');
      carregarSenha();
    } catch (e) {
      flash('danger', `Erro ao criar senha: ${e.response?.data?.detail || e.message}`);
    }
  };

  const gerarSenhaAleatoria = async () => {
    if (!ordemId) return flash('warning', 'Carregue uma OS primeiro');
    try {
      const res = await api.post(`/api/os/${ordemId}/senhas/gerar?tipo=pin&tamanho=4`);
      flash('success', `PIN gerado: ${res.valor}`);
      setSenhaValor(res.valor);
    } catch (e) {
      flash('danger', `Erro ao gerar senha: ${e.response?.data?.detail || e.message}`);
    }
  };

  const deletarSenha = async () => {
    if (!ordemId) return;
    try {
      await api.delete(`/api/os/${ordemId}/senhas`);
      flash('success', 'Senha removida');
      carregarSenha();
    } catch (e) {
      flash('danger', `Erro ao remover senha: ${e.response?.data?.detail || e.message}`);
    }
  };

  // ===== PADRÃO (PATTERN DRAW) =====
  // Apenas captura o padrão desenhado (NÃO salva ainda — usuário clica em "Salvar Padrão")
  const handlePatternComplete = (pattern) => {
    setPatternData(pattern);
    flash('info', `Padrão desenhado (${pattern.dotCount} pontos). Clique em "Salvar Padrão" para gravar.`);
  };

  // Salva o padrão capturado no backend
  const salvarPadrao = async () => {
    if (!ordemId) {
      flash('warning', 'Carregue uma OS primeiro');
      return;
    }
    if (!patternData) {
      flash('warning', 'Desenhe um padrão primeiro');
      return;
    }

    try {
      const device = {
        tipo: 'browser',
        navegador: navigator.userAgent,
        resolucao: `${window.innerWidth}x${window.innerHeight}`,
      };

      await api.post(`/api/os/${ordemId}/senhas/pattern`, {
        pattern: patternData.pattern,
        sequence: patternData.sequence,
        duracao_ms: patternData.duration,
        dispositivo: device,
        timestamp: patternData.timestamp,
      });

      flash('success', `Padrão salvo com sucesso! (${patternData.dotCount} pontos conectados)`);
      setMostrarPattern(false);
      setPatternData(null);

      // Carregar senha atualizada
      setTimeout(() => carregarSenha(), 500);
    } catch (e) {
      flash('danger', `Erro ao salvar padrão: ${e.response?.data?.detail || e.message}`);
    }
  };

  // Replay do padrão que ACABOU de ser desenhado (antes de salvar)
  const verReplayLocal = () => {
    if (!patternData) {
      flash('warning', 'Desenhe um padrão primeiro');
      return;
    }
    setPatternReplay({ pattern: patternData.pattern, sequence: patternData.sequence });
  };

  // Replay do padrão JÁ SALVO no backend (para conferir depois)
  const visualizarReplay = async () => {
    if (!ordemId || !senhaInfo?.tem_replay) {
      flash('warning', 'Nenhum replay disponível');
      return;
    }

    try {
      const res = await api.get(`/api/os/${ordemId}/senhas/replay`);
      setPatternReplay({ pattern: res.pattern || '', sequence: res.sequence || [] });
      setMostrarPattern(true);
    } catch (e) {
      flash('danger', `Erro ao carregar replay: ${e.response?.data?.detail || e.message}`);
    }
  };

  // ===== FOTOS =====
  const carregarFotos = async () => {
    if (!ordemId) return;
    try {
      const res = await api.get(`/api/os/${ordemId}/fotos`);
      setFotos(res.fotos || []);
    } catch (e) {
      setFotos([]);
    }
  };

  const uploadFoto = async () => {
    if (!ordemId) return flash('warning', 'Carregue uma OS primeiro');
    if (!arquivo) return flash('warning', 'Selecione um arquivo');
    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('descricao', descricaoFoto);
      const axios = (await import('axios')).default;
      const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      await axios.post(`${API_BASE}/api/os/${ordemId}/fotos/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      flash('success', 'Foto enviada com sucesso');
      setArquivo(null);
      setDescricaoFoto('');
      carregarFotos();
    } catch (e) {
      flash('danger', `Erro ao enviar foto: ${e.response?.data?.detail || e.message}`);
    }
  };

  const deletarFoto = async (fotoId) => {
    try {
      await api.delete(`/api/os/${ordemId}/fotos/${fotoId}`);
      flash('success', 'Foto removida');
      carregarFotos();
    } catch (e) {
      flash('danger', `Erro ao remover foto: ${e.response?.data?.detail || e.message}`);
    }
  };

  // ===== LAUDO =====
  const carregarLaudo = async () => {
    if (!ordemId) return;
    try {
      const res = await api.get(`/api/os/${ordemId}/laudo`);
      setLaudo(res.laudo);
    } catch (e) {
      setLaudo(null);
    }
  };

  const criarLaudo = async () => {
    if (!ordemId) return flash('warning', 'Carregue uma OS primeiro');
    try {
      const body = {
        danos: [
          { tipo: 'tela', descricao: 'Dano registrado via sistema', severidade: 'media', foto_ids: [] },
        ],
        observacoes_gerais: obsLaudo,
        recomendacoes: [],
      };
      await api.post(`/api/os/${ordemId}/laudo`, body);
      flash('success', 'Laudo técnico criado (assinado digitalmente RSA-2048)');
      setObsLaudo('');
      carregarLaudo();
    } catch (e) {
      flash('danger', `Erro ao criar laudo: ${e.response?.data?.detail || e.message}`);
    }
  };

  const validarLaudo = async () => {
    if (!ordemId) return;
    try {
      const res = await api.post(`/api/os/${ordemId}/laudo/validar`);
      flash(res.valido ? 'success' : 'warning', `Validação: ${res.mensagem}`);
    } catch (e) {
      flash('danger', `Erro ao validar laudo: ${e.response?.data?.detail || e.message}`);
    }
  };

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h1>🔧 Ordem de Serviço — Ferramentas</h1>
          <p className="text-muted">Número OS, Senhas, Fotos e Laudo Técnico</p>
        </Col>
      </Row>

      {msg && <Alert variant={msg.variant}>{msg.texto}</Alert>}

      {/* Seletor de modo: Nova OS (assistente direto) x OS Existente */}
      <div className="d-flex gap-2 mb-4">
        <Button
          variant={modo === 'nova' ? 'primary' : 'outline-primary'}
          onClick={() => { setModo('nova'); setOrdemAtiva(null); setMostrarWizard(false); }}
        >
          🆕 Nova OS
        </Button>
        <Button
          variant={modo === 'existente' ? 'primary' : 'outline-primary'}
          onClick={() => setModo('existente')}
        >
          📂 OS Existente
        </Button>
      </div>

      {/* MODO NOVA: assistente abre direto na tela de endereço (número gerado ao salvar) */}
      {modo === 'nova' && (
        <NovaOSWizard
          key={`nova-${wizardKey}`}
          ordemId={null}
          clienteId={clienteId || 1}
          onConcluir={aoConcluirNova}
          onCancelar={() => setWizardKey((k) => k + 1)}
          flash={flash}
        />
      )}

      {/* MODO EXISTENTE: carregar OS pelo ID */}
      {modo === 'existente' && (
      <Row>
        <Col md={6} className="mb-4">
          <Card>
            <Card.Header>📂 Carregar OS Existente</Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>ID da OS</Form.Label>
                <Form.Control
                  type="number"
                  placeholder="Ex: 1"
                  value={ordemId}
                  onChange={(e) => setOrdemId(e.target.value)}
                />
              </Form.Group>
              <Button variant="outline-primary" onClick={carregarOS}>
                📂 Carregar OS
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      )}

      {ordemAtiva && (() => {
        const fechada = String(ordemAtiva.status || '').toLowerCase().startsWith('fech');
        return (
          <Card className="mb-4">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
                <h5 className="mb-0 d-flex align-items-center gap-2">
                  {/* Bolinha de status: 🔴 aberta / 🔵 fechada */}
                  <span
                    title={fechada ? 'OS Fechada' : 'OS Aberta'}
                    style={{
                      display: 'inline-block',
                      width: 16,
                      height: 16,
                      borderRadius: '50%',
                      background: fechada ? '#0d6efd' : '#dc3545',
                      border: '1px solid rgba(0,0,0,0.2)',
                    }}
                  />
                  OS: <Badge bg="info">{ordemAtiva.numero_os}</Badge>{' '}
                  <Badge bg="secondary">ID {ordemAtiva.ordem_id || ordemAtiva.id}</Badge>{' '}
                  <Badge bg={fechada ? 'primary' : 'danger'}>
                    {fechada ? 'Fechada' : 'Aberta'}
                  </Badge>
                </h5>
                <Button variant="warning" onClick={abrirAlterar}>
                  ✏️ Alterar
                </Button>
              </div>

              {/* Resumo dos dados cadastrados */}
              {(ordemAtiva.marca || ordemAtiva.produto_tipo || ordemAtiva.endereco_rua) && (
                <div className="mt-3 small text-muted">
                  {ordemAtiva.produto_tipo && <span className="me-3">📦 {ordemAtiva.produto_tipo}</span>}
                  {ordemAtiva.marca && <span className="me-3">🏷️ {ordemAtiva.marca} {ordemAtiva.modelo}</span>}
                  {ordemAtiva.endereco_rua && (
                    <span className="me-3">📍 {ordemAtiva.endereco_rua}, {ordemAtiva.endereco_numero} - {ordemAtiva.bairro} {ordemAtiva.cidade_os}</span>
                  )}
                  {ordemAtiva.telefone_contato && <span className="me-3">📞 {ordemAtiva.telefone_contato}</span>}
                  {ordemAtiva.tem_assinatura && <Badge bg="success">✍️ Assinado</Badge>}
                  {ordemAtiva.problema_descricao && (
                    <div className="mt-1">🔧 <em>{ordemAtiva.problema_descricao}</em></div>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>
        );
      })()}

      {/* Assistente (Wizard) de cadastro/alteração */}
      {mostrarWizard && ordemId && (
        <NovaOSWizard
          ordemId={ordemId}
          numeroOS={ordemAtiva?.numero_os}
          dadosIniciais={wizardDados}
          onConcluir={aoConcluirWizard}
          onCancelar={() => { setMostrarWizard(false); setWizardDados(null); }}
          flash={flash}
        />
      )}

      {/* Ferramentas por OS (só no modo existente) */}
      {modo === 'existente' && (
      <Card className={mostrarWizard ? 'd-none' : ''}>
        <Card.Body>
          <Tabs defaultActiveKey="senha" className="mb-3">
            {/* SENHA */}
            <Tab eventKey="senha" title="🔐 Senha">
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Tipo de Senha</Form.Label>
                    <Form.Select value={senhaTipo} onChange={(e) => setSenhaTipo(e.target.value)}>
                      <option value="pin">PIN (4-6 dígitos)</option>
                      <option value="padrao">Padrão (Desenho)</option>
                      <option value="nenhuma">Nenhuma</option>
                    </Form.Select>
                  </Form.Group>
                  {senhaTipo === 'pin' && (
                    <Form.Group className="mb-3">
                      <Form.Label>Valor do PIN</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Ex: 1234"
                        value={senhaValor}
                        onChange={(e) => setSenhaValor(e.target.value)}
                      />
                    </Form.Group>
                  )}
                  {senhaTipo === 'padrao' && (
                    <Button
                      variant="primary"
                      onClick={() => setMostrarPattern(true)}
                      className="mb-3 w-100"
                    >
                      {patternData ? '✏️ Redefinir Padrão' : '🎨 Desenhar Padrão'}
                    </Button>
                  )}
                  <Button variant="primary" onClick={criarSenha} className="me-2" disabled={senhaTipo === 'padrao' && !patternData}>
                    💾 Salvar Senha
                  </Button>
                  {senhaTipo === 'pin' && (
                    <Button variant="outline-secondary" onClick={gerarSenhaAleatoria} className="me-2">
                      🎲 Gerar PIN
                    </Button>
                  )}
                  <Button variant="outline-danger" onClick={deletarSenha}>
                    🗑️ Remover
                  </Button>
                </Col>
                <Col md={6}>
                  <Card bg="light">
                    <Card.Body>
                      <h6>Status da Senha</h6>
                      {senhaInfo?.tem_senha ? (
                        <>
                          <p className="mb-1">Tipo: <Badge bg="info">{senhaInfo.tipo}</Badge></p>
                          <p className="mb-1 text-muted small">{senhaInfo.mensagem_seguranca}</p>
                          {senhaInfo.tem_replay && (
                            <Button
                              size="sm"
                              variant="outline-info"
                              onClick={visualizarReplay}
                              className="mt-2"
                            >
                              ▶️ Ver Replay do Padrão
                            </Button>
                          )}
                        </>
                      ) : (
                        <p className="text-muted mb-0">Nenhuma senha cadastrada</p>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {mostrarPattern && (
                <Row className="mt-4">
                  <Col>
                    <Card>
                      <Card.Header>
                        {patternReplay ? '▶️ Reprodução do Padrão' : '🎨 Desenhe o Padrão'}
                      </Card.Header>
                      <Card.Body>
                        <PatternDraw
                          key={patternReplay ? 'replay' : 'draw'}
                          onPatternComplete={handlePatternComplete}
                          onReplay={!!patternReplay}
                          replayData={patternReplay}
                        />

                        {/* Modo REPLAY: só botão de voltar */}
                        {patternReplay && (
                          <Button
                            variant="secondary"
                            onClick={() => setPatternReplay(null)}
                            className="mt-3 w-100"
                          >
                            ◀️ Voltar
                          </Button>
                        )}

                        {/* Modo DESENHO: botões Salvar / Replay / Cancelar */}
                        {!patternReplay && (
                          <>
                            {patternData && (
                              <Alert variant="success" className="mt-3 mb-3">
                                ✅ Padrão desenhado: <strong>{patternData.pattern}</strong>{' '}
                                ({patternData.dotCount} pontos)
                              </Alert>
                            )}
                            <div className="d-flex gap-2 mt-3">
                              <Button
                                variant="success"
                                onClick={salvarPadrao}
                                disabled={!patternData}
                                className="flex-fill"
                              >
                                💾 Salvar Padrão
                              </Button>
                              <Button
                                variant="outline-info"
                                onClick={verReplayLocal}
                                disabled={!patternData}
                                className="flex-fill"
                              >
                                ▶️ Ver Replay
                              </Button>
                              <Button
                                variant="outline-secondary"
                                onClick={() => {
                                  setMostrarPattern(false);
                                  setPatternReplay(null);
                                  setPatternData(null);
                                }}
                                className="flex-fill"
                              >
                                ✖️ Cancelar
                              </Button>
                            </div>
                          </>
                        )}
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              )}
            </Tab>

            {/* FOTOS */}
            <Tab eventKey="fotos" title="📷 Fotos">
              <Row className="mb-3">
                <Col md={5}>
                  <Form.Group className="mb-2">
                    <Form.Label>Arquivo de Imagem</Form.Label>
                    <Form.Control
                      type="file"
                      accept="image/*"
                      onChange={(e) => setArquivo(e.target.files[0])}
                    />
                  </Form.Group>
                </Col>
                <Col md={5}>
                  <Form.Group className="mb-2">
                    <Form.Label>Descrição</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Ex: Tela quebrada"
                      value={descricaoFoto}
                      onChange={(e) => setDescricaoFoto(e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={2} className="d-flex align-items-end">
                  <Button variant="primary" onClick={uploadFoto} className="mb-2 w-100">
                    ⬆️ Enviar
                  </Button>
                </Col>
              </Row>
              <Table hover responsive size="sm">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Descrição</th>
                    <th>Tipo Dano</th>
                    <th>Tamanho</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {fotos.map((f) => (
                    <tr key={f.id}>
                      <td className="small">{f.id?.substring(0, 8)}...</td>
                      <td>{f.descricao}</td>
                      <td>{f.tipo_dano || '-'}</td>
                      <td>{f.tamanho} bytes</td>
                      <td>
                        <Button size="sm" variant="outline-danger" onClick={() => deletarFoto(f.id)}>
                          🗑️
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {fotos.length === 0 && <p className="text-center text-muted">Nenhuma foto</p>}
            </Tab>

            {/* LAUDO */}
            <Tab eventKey="laudo" title="📄 Laudo Técnico">
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Observações Gerais</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      placeholder="Descreva o estado do equipamento..."
                      value={obsLaudo}
                      onChange={(e) => setObsLaudo(e.target.value)}
                    />
                  </Form.Group>
                  <Button variant="primary" onClick={criarLaudo} className="me-2">
                    📝 Criar Laudo
                  </Button>
                  <Button variant="outline-info" onClick={validarLaudo}>
                    🔏 Validar Assinatura
                  </Button>
                </Col>
                <Col md={6}>
                  <Card bg="light">
                    <Card.Body>
                      <h6>Laudo Atual</h6>
                      {laudo ? (
                        <>
                          <p className="mb-1">✅ Laudo criado e assinado digitalmente</p>
                          <p className="mb-0 text-muted small">
                            {JSON.stringify(laudo).substring(0, 120)}...
                          </p>
                        </>
                      ) : (
                        <p className="text-muted mb-0">Nenhum laudo criado</p>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>
      )}
    </Container>
  );
}
