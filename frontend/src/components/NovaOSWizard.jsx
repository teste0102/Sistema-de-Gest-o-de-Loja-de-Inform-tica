import React, { useState } from 'react';
import { Card, Button, Form, Row, Col, Badge, ProgressBar, Alert } from 'react-bootstrap';
import api from '../services/api';
import PatternDraw from './PatternDraw';
import AssinaturaDigital from './AssinaturaDigital';
import { MARCAS_CELULAR, MODELOS_POR_MARCA, TIPOS_PRODUTO } from '../data/marcasModelos';

// ===== Helpers de moeda (formato BR: 1.234,56) =====
const soDigitos = (s) => String(s || '').replace(/\D/g, '');
const centavosParaNumero = (cent) => parseInt(soDigitos(cent) || '0', 10) / 100;
const numeroParaCentavos = (n) => (n ? Math.round(n * 100).toString() : '');
const fmtBRL = (n) => Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Campo de valor (moeda) + parcelas (vezes) com valor por parcela automático
function CampoValorParcela({ titulo, cent, setCent, parcelas, setParcelas }) {
  const valor = centavosParaNumero(cent);
  const porParcela = parcelas > 0 ? valor / parcelas : valor;
  return (
    <div className="mb-3 p-3" style={{ border: '1px solid #e0e0e0', borderRadius: 8, background: '#fafafa' }}>
      <Form.Label className="fw-bold">{titulo}</Form.Label>
      <Row className="g-2 align-items-end">
        <Col md={6}>
          <Form.Label className="small mb-1">Valor</Form.Label>
          <div className="input-group">
            <span className="input-group-text">R$</span>
            <Form.Control
              inputMode="numeric"
              value={fmtBRL(valor)}
              onChange={(e) => setCent(soDigitos(e.target.value))}
              placeholder="0,00"
            />
          </div>
        </Col>
        <Col md={3}>
          <Form.Label className="small mb-1">Vezes</Form.Label>
          <Form.Select value={parcelas} onChange={(e) => setParcelas(parseInt(e.target.value, 10))}>
            {[1,2,3,4,5,6,7,8,9,10,11,12].map((n) => <option key={n} value={n}>{n}x</option>)}
          </Form.Select>
        </Col>
        <Col md={3}>
          <Form.Label className="small mb-1">Por parcela</Form.Label>
          <div className="form-control bg-white text-success fw-bold">R$ {fmtBRL(porParcela)}</div>
        </Col>
      </Row>
    </div>
  );
}

// Assistente de cadastro/alteração de OS em janelas sequenciais.
// Props:
//   ordemId       - ID da OS (null = nova; número gerado ao salvar)
//   clienteId     - cliente da OS nova (default 1)
//   numeroOS      - número para exibição
//   dadosIniciais - objeto do GET da OS (modo Alterar) ou null (nova)
//   onConcluir(id)- callback ao finalizar (recebe o id da OS)
//   onCancelar()  - callback ao cancelar
//   flash(v, msg) - função para mensagens do pai
const PASSOS = ['Endereço', 'Produto', 'Senha', 'Problema', 'Assinatura'];

export default function NovaOSWizard({ ordemId = null, clienteId = 1, numeroOS, dadosIniciais = null, onConcluir, onCancelar, flash }) {
  const [passo, setPasso] = useState(1);
  const [salvando, setSalvando] = useState(false);
  const d = dadosIniciais || {};

  // ---- Janela 1: Endereço / Contato
  const [nomeCliente, setNomeCliente] = useState(d.nome_cliente || '');
  const [enderecoRua, setEnderecoRua] = useState(d.endereco_rua || '');
  const [enderecoTipo, setEnderecoTipo] = useState(d.endereco_tipo || 'casa');
  const [enderecoComplemento, setEnderecoComplemento] = useState(d.endereco_complemento || '');
  const [enderecoNumero, setEnderecoNumero] = useState(d.endereco_numero || '');
  const [bairro, setBairro] = useState(d.bairro || '');
  const [cidade, setCidade] = useState(d.cidade_os || '');
  const [telefone, setTelefone] = useState(d.telefone_contato || '');

  // ---- Janela 2: Produto
  const [produtoTipo, setProdutoTipo] = useState(d.produto_tipo || 'celular');
  const [marca, setMarca] = useState(d.marca || '');
  const [modelo, setModelo] = useState(d.modelo || '');
  const [marcaLivre, setMarcaLivre] = useState('');
  const [modeloLivre, setModeloLivre] = useState('');
  const [imei, setImei] = useState(d.imei || '');
  const [produtoDescricao, setProdutoDescricao] = useState(d.produto_descricao || '');

  // ---- Janela 3: Senha
  const [senhaTipo, setSenhaTipo] = useState('pin');
  const [senhaPin, setSenhaPin] = useState('');
  const [mostrarPattern, setMostrarPattern] = useState(false);
  const [patternData, setPatternData] = useState(null);

  // ---- Janela 4: Problema + Orçamento
  const [problema, setProblema] = useState(d.problema_descricao || '');
  const [valorAprovadoCent, setValorAprovadoCent] = useState(numeroParaCentavos(d.valor_aprovado_estimado));
  const [parcelasAprovado, setParcelasAprovado] = useState(d.valor_aprovado_parcelas || 1);
  const [valorTotalCent, setValorTotalCent] = useState(numeroParaCentavos(d.valor_total_estimado));
  const [parcelasTotal, setParcelasTotal] = useState(d.valor_total_parcelas || 1);

  // ---- Janela 5: Assinatura
  const [assinatura, setAssinatura] = useState(d.assinatura_cliente || null);

  // Replay da senha no mesmo canvas
  const [replaySignal, setReplaySignal] = useState(0);      // incrementa para tocar o replay
  const [replaySavedData, setReplaySavedData] = useState(null); // senha salva (modo Alterar)

  const proximo = () => setPasso((p) => Math.min(p + 1, PASSOS.length));
  const voltar = () => setPasso((p) => Math.max(p - 1, 1));

  // Marca/modelo efetivos (considerando opção "Outra"/"Outro modelo")
  const marcaFinal = marca === 'Outra' ? marcaLivre : marca;
  const modeloFinal = modelo === 'Outro modelo' ? modeloLivre : modelo;

  const finalizar = async () => {
    setSalvando(true);
    try {
      // 0) Se for uma OS nova (sem id), gerar o número LOCAL agora.
      //    O número é sequencial local; a sincronização com o servidor
      //    remoto (IP + pasta) acontece depois, no final do programa.
      let idOS = ordemId;
      let numeroFinal = numeroOS;
      if (!idOS) {
        const gerada = await api.post(`/api/os/gerar-numero?cliente_id=${clienteId}`);
        idOS = gerada.ordem_id;
        numeroFinal = gerada.numero_os;
      }

      // 1) Salvar campos gerais (endereço, produto, problema)
      const payload = {
        produto_tipo: produtoTipo,
        produto_descricao: produtoTipo === 'outro' ? produtoDescricao : null,
        marca: produtoTipo === 'celular' ? marcaFinal : null,
        modelo: produtoTipo === 'celular' ? modeloFinal : null,
        imei: produtoTipo === 'celular' ? imei : null,
        nome_cliente: nomeCliente,
        endereco_rua: enderecoRua,
        endereco_tipo: enderecoTipo,
        endereco_complemento: enderecoComplemento,
        endereco_numero: enderecoNumero,
        bairro: bairro,
        cidade_os: cidade,
        telefone_contato: telefone,
        problema_descricao: problema,
        valor_aprovado_estimado: centavosParaNumero(valorAprovadoCent),
        valor_aprovado_parcelas: parseInt(parcelasAprovado, 10) || 1,
        valor_total_estimado: centavosParaNumero(valorTotalCent),
        valor_total_parcelas: parseInt(parcelasTotal, 10) || 1,
      };
      await api.put(`/api/os/${idOS}/completo`, payload);

      // 2) Salvar senha
      if (senhaTipo === 'pin' && senhaPin) {
        await api.post(`/api/os/${idOS}/senhas`, { tipo: 'pin', valor: senhaPin });
      } else if (senhaTipo === 'padrao' && patternData) {
        await api.post(`/api/os/${idOS}/senhas/pattern`, {
          pattern: patternData.pattern,
          sequence: patternData.sequence,
          duracao_ms: patternData.duration,
          dispositivo: { tipo: 'browser', navegador: navigator.userAgent, resolucao: `${window.innerWidth}x${window.innerHeight}` },
          timestamp: patternData.timestamp,
        });
      } else if (senhaTipo === 'nenhuma') {
        await api.post(`/api/os/${idOS}/senhas`, { tipo: 'nenhuma' });
      }

      // 3) Salvar assinatura
      if (assinatura) {
        await api.post(`/api/os/${idOS}/assinatura`, { assinatura });
      }

      flash && flash('success', `OS ${numeroFinal || idOS} salva com sucesso!`);
      onConcluir && onConcluir(idOS);
    } catch (e) {
      flash && flash('danger', `Erro ao salvar OS: ${e.response?.data?.detail || e.message}`);
    } finally {
      setSalvando(false);
    }
  };

  const progresso = Math.round((passo / PASSOS.length) * 100);

  return (
    <Card className="mt-3">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <span>
          🪟 {ordemId ? 'Alterar OS' : 'Nova OS'} {numeroOS ? <Badge bg="info">{numeroOS}</Badge> : <Badge bg="secondary">nº gerado ao salvar</Badge>}
        </span>
        <span className="text-muted small">Passo {passo} de {PASSOS.length}: {PASSOS[passo - 1]}</span>
      </Card.Header>
      <Card.Body>
        <ProgressBar now={progresso} label={`${progresso}%`} className="mb-4" />

        {/* JANELA 1 - ENDEREÇO */}
        {passo === 1 && (
          <div>
            <h5 className="mb-3">📍 Cliente, Endereço e Contato</h5>
            <Row>
              <Col md={12}>
                <Form.Group className="mb-3">
                  <Form.Label>Nome do cliente</Form.Label>
                  <Form.Control value={nomeCliente} onChange={(e) => setNomeCliente(e.target.value)} placeholder="Ex: João da Silva" />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Nome da rua</Form.Label>
                  <Form.Control value={enderecoRua} onChange={(e) => setEnderecoRua(e.target.value)} placeholder="Ex: Rua das Flores" />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Casa ou AP</Form.Label>
                  <Form.Select value={enderecoTipo} onChange={(e) => setEnderecoTipo(e.target.value)}>
                    <option value="casa">Casa</option>
                    <option value="ap">Apartamento</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Número</Form.Label>
                  <Form.Control value={enderecoNumero} onChange={(e) => setEnderecoNumero(e.target.value)} placeholder="Ex: 123" />
                </Form.Group>
              </Col>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Complemento</Form.Label>
                  <Form.Control value={enderecoComplemento} onChange={(e) => setEnderecoComplemento(e.target.value)} placeholder="Ex: Bloco B, Apto 42" />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={5}>
                <Form.Group className="mb-3">
                  <Form.Label>Bairro</Form.Label>
                  <Form.Control value={bairro} onChange={(e) => setBairro(e.target.value)} placeholder="Ex: Centro" />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Cidade</Form.Label>
                  <Form.Control value={cidade} onChange={(e) => setCidade(e.target.value)} placeholder="Ex: São Paulo" />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Telefone</Form.Label>
                  <Form.Control value={telefone} onChange={(e) => setTelefone(e.target.value)} placeholder="Ex: 11 99999-9999" />
                </Form.Group>
              </Col>
            </Row>
          </div>
        )}

        {/* JANELA 2 - PRODUTO */}
        {passo === 2 && (
          <div>
            <h5 className="mb-3">📦 Produto</h5>
            <Form.Group className="mb-3">
              <Form.Label>Tipo do produto</Form.Label>
              <div className="d-flex gap-2 flex-wrap">
                {TIPOS_PRODUTO.map((t) => (
                  <Button
                    key={t.valor}
                    variant={produtoTipo === t.valor ? 'primary' : 'outline-primary'}
                    onClick={() => setProdutoTipo(t.valor)}
                  >
                    {t.label}
                  </Button>
                ))}
              </div>
            </Form.Group>

            {produtoTipo === 'celular' && (
              <>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Marca</Form.Label>
                      <Form.Select value={marca} onChange={(e) => { setMarca(e.target.value); setModelo(''); }}>
                        <option value="">-- Escolha a marca --</option>
                        {MARCAS_CELULAR.map((m) => <option key={m} value={m}>{m}</option>)}
                      </Form.Select>
                    </Form.Group>
                    {marca === 'Outra' && (
                      <Form.Group className="mb-3">
                        <Form.Label>Digite a marca</Form.Label>
                        <Form.Control value={marcaLivre} onChange={(e) => setMarcaLivre(e.target.value)} placeholder="Ex: Nokia" />
                      </Form.Group>
                    )}
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Modelo</Form.Label>
                      <Form.Select value={modelo} onChange={(e) => setModelo(e.target.value)} disabled={!marca}>
                        <option value="">-- Escolha o modelo --</option>
                        {(MODELOS_POR_MARCA[marca] || []).map((m) => <option key={m} value={m}>{m}</option>)}
                      </Form.Select>
                    </Form.Group>
                    {modelo === 'Outro modelo' && (
                      <Form.Group className="mb-3">
                        <Form.Label>Digite o modelo</Form.Label>
                        <Form.Control value={modeloLivre} onChange={(e) => setModeloLivre(e.target.value)} placeholder="Ex: Lumia 630" />
                      </Form.Group>
                    )}
                  </Col>
                </Row>
                <Form.Group className="mb-3">
                  <Form.Label>IMEI (opcional)</Form.Label>
                  <Form.Control value={imei} onChange={(e) => setImei(e.target.value)} placeholder="Ex: 356938035643809" />
                </Form.Group>
              </>
            )}

            {(produtoTipo === 'pc' || produtoTipo === 'pc_gamer') && (
              <Alert variant="info">
                Produto selecionado: <strong>{produtoTipo === 'pc' ? 'PC' : 'PC Gamer'}</strong>.
                Você pode detalhar mais no campo de problema (próximas janelas).
              </Alert>
            )}

            {produtoTipo === 'outro' && (
              <Form.Group className="mb-3">
                <Form.Label>Descreva o produto</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={produtoDescricao}
                  onChange={(e) => setProdutoDescricao(e.target.value)}
                  placeholder="Ex: Tablet, Videogame, Impressora..."
                />
              </Form.Group>
            )}
          </div>
        )}

        {/* JANELA 3 - SENHA */}
        {passo === 3 && (
          <div>
            <h5 className="mb-3">🔐 Senha do Aparelho</h5>
            <Form.Group className="mb-3">
              <Form.Label>Tipo de senha</Form.Label>
              <Form.Select value={senhaTipo} onChange={(e) => { setSenhaTipo(e.target.value); setMostrarPattern(false); }}>
                <option value="pin">PIN (4-6 dígitos)</option>
                <option value="padrao">Padrão (Desenho)</option>
                <option value="nenhuma">Nenhuma</option>
              </Form.Select>
            </Form.Group>

            {senhaTipo === 'pin' && (
              <Form.Group className="mb-3" style={{ maxWidth: 240 }}>
                <Form.Label>Valor do PIN</Form.Label>
                <Form.Control value={senhaPin} onChange={(e) => setSenhaPin(e.target.value)} placeholder="Ex: 1234" />
              </Form.Group>
            )}

            {senhaTipo === 'padrao' && (
              <div className="mt-2">
                {/* Canvas sempre visível: desenhe direto. O replay toca no MESMO canvas. */}
                <PatternDraw
                  key="draw-wizard"
                  onPatternComplete={(p) => setPatternData(p)}
                  replayData={replaySavedData}
                  replaySignal={replaySignal}
                />

                {/* Botões logo abaixo das bolinhas */}
                <div className="d-flex gap-2 flex-wrap justify-content-center mt-1">
                  {patternData && (
                    <>
                      <Button
                        size="sm"
                        variant="info"
                        onClick={() => {
                          // Usa o patternData (persiste mesmo após trocar de janela e voltar)
                          setReplaySavedData({ pattern: patternData.pattern, sequence: patternData.sequence });
                          setReplaySignal((s) => s + 1);
                        }}
                      >
                        ▶️ Ver Replay
                      </Button>
                      <Button
                        size="sm"
                        variant="success"
                        onClick={() => flash && flash('success', 'Padrão registrado! Será gravado ao finalizar a OS.')}
                      >
                        💾 Salvar Padrão
                      </Button>
                    </>
                  )}
                  {ordemId && dadosIniciais?.tem_replay && (
                    <Button
                      size="sm"
                      variant="outline-warning"
                      onClick={async () => {
                        try {
                          const r = await api.get(`/api/os/${ordemId}/senhas/replay`);
                          setReplaySavedData({ pattern: r.pattern || '', sequence: r.sequence || [] });
                          setReplaySignal((s) => s + 1);
                        } catch (e) {
                          flash && flash('danger', `Erro ao carregar replay: ${e.response?.data?.detail || e.message}`);
                        }
                      }}
                    >
                      🔒 Ver Senha Salva
                    </Button>
                  )}
                </div>

                {patternData && (
                  <div className="text-center small text-success mt-1">
                    ✅ Padrão: <strong>{patternData.pattern}</strong> ({patternData.dotCount} pontos)
                  </div>
                )}
              </div>
            )}

            {senhaTipo === 'nenhuma' && (
              <Alert variant="secondary">Aparelho sem senha (desbloqueado).</Alert>
            )}
          </div>
        )}

        {/* JANELA 4 - PROBLEMA + ORÇAMENTO */}
        {passo === 4 && (
          <div>
            <h5 className="mb-3">🔧 Problema do Aparelho</h5>
            <Form.Group className="mb-4">
              <Form.Label>Descreva o problema relatado</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={problema}
                onChange={(e) => setProblema(e.target.value)}
                placeholder="Ex: Tela quebrada, não liga, bateria vicia, molhou..."
              />
            </Form.Group>

            <h6 className="mb-3">💰 Orçamento</h6>
            <CampoValorParcela
              titulo="Valor aprovado (referência)"
              cent={valorAprovadoCent}
              setCent={setValorAprovadoCent}
              parcelas={parcelasAprovado}
              setParcelas={setParcelasAprovado}
            />
            <CampoValorParcela
              titulo="Valor total estimado"
              cent={valorTotalCent}
              setCent={setValorTotalCent}
              parcelas={parcelasTotal}
              setParcelas={setParcelasTotal}
            />
          </div>
        )}

        {/* JANELA 5 - ASSINATURA */}
        {passo === 5 && (
          <div>
            <h5 className="mb-3">✍️ Assinatura do Cliente</h5>
            <AssinaturaDigital onChange={setAssinatura} valorInicial={dadosIniciais?.assinatura_cliente || null} />
          </div>
        )}

        {/* NAVEGAÇÃO */}
        <hr />
        <div className="d-flex justify-content-between">
          <Button variant="outline-secondary" onClick={onCancelar} disabled={salvando}>
            ✖️ Cancelar
          </Button>
          <div className="d-flex gap-2">
            {passo > 1 && (
              <Button variant="secondary" onClick={voltar} disabled={salvando}>
                ◀️ Voltar
              </Button>
            )}
            {passo < PASSOS.length && (
              <Button variant="primary" onClick={proximo} disabled={salvando}>
                Próximo ▶️
              </Button>
            )}
            {passo === PASSOS.length && (
              <Button variant="success" onClick={finalizar} disabled={salvando}>
                {salvando ? 'Salvando...' : '💾 Finalizar e Salvar OS'}
              </Button>
            )}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
