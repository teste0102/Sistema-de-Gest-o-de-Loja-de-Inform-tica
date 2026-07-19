import React, { useState, useEffect, useRef } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col, Modal, Form, Alert, Badge } from 'react-bootstrap';
import api from '../services/api';

const BRL = (v) => (Number(v) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

export default function VendasPage() {
  const [vendas, setVendas] = useState([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busca, setBusca] = useState('');
  const [msg, setMsg] = useState(null);
  const [importando, setImportando] = useState(false);

  const [showImport, setShowImport] = useState(false);
  const [imp, setImp] = useState({
    modo: 'local', subpasta: '', arquivo: 'VENDAS.MDB', tabela: 'CADA',
    host: '', porta: 22, usuario: '', senha: '', caminho: '.',
  });

  const [showPDV, setShowPDV] = useState(false);
  const [pdv, setPdv] = useState({ cliente_nome: '', vendedor: '', pagamento: 'A VISTA', itens: [] });
  const [codigo, setCodigo] = useState('');
  const codRef = useRef(null);

  const [detalhe, setDetalhe] = useState(null);

  useEffect(() => { carregar(); carregarStats(); }, []);

  const carregar = async (termo = '') => {
    try {
      setLoading(true);
      const data = await api.get(`/api/vendas/?limit=500&busca=${encodeURIComponent(termo)}`);
      setVendas(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      setMsg({ tipo: 'danger', texto: 'Erro ao carregar vendas.' });
    } finally {
      setLoading(false);
    }
  };

  const carregarStats = async () => {
    try { setStats(await api.get('/api/vendas/stats/resumo')); } catch (e) { /* silencioso */ }
  };

  const importarAccess = async () => {
    try {
      setImportando(true);
      setMsg(null);
      const rota = imp.modo === 'ssh' ? '/api/vendas/importar-mdb-ssh' : '/api/vendas/importar-mdb';
      const corpo = imp.modo === 'ssh'
        ? { host: imp.host, porta: Number(imp.porta) || 22, usuario: imp.usuario, senha: imp.senha, caminho: imp.caminho || '.', arquivo: imp.arquivo, tabela: imp.tabela }
        : { subpasta: imp.subpasta, arquivo: imp.arquivo, tabela: imp.tabela };
      const r = await api.post(rota, corpo);
      setShowImport(false);
      setMsg({ tipo: 'success', texto: `Importação: ${r.total_vendas} vendas, ${r.criadas} novas, ${r.ja_existentes} já existentes.` });
      carregar(''); carregarStats();
    } catch (e) {
      setMsg({ tipo: 'danger', texto: `Falha: ${e?.response?.data?.detail || e.message}` });
    } finally {
      setImportando(false);
    }
  };

  // ===== PDV =====
  const bipar = async (e) => {
    e.preventDefault();
    const cod = codigo.trim();
    if (!cod) return;
    try {
      const p = await api.get(`/api/produtos/barras/${encodeURIComponent(cod)}`);
      setPdv((old) => {
        const itens = [...old.itens];
        const idx = itens.findIndex((i) => i.produto_id === p.id);
        if (idx >= 0) {
          itens[idx].quantidade += 1;
          itens[idx].subtotal = itens[idx].quantidade * itens[idx].preco_unitario;
        } else {
          itens.push({
            produto_id: p.id, codigo_produto: p.codigo_barras, descricao: p.descricao,
            unidade: p.unidade, quantidade: 1, preco_unitario: p.preco_venda, subtotal: p.preco_venda,
          });
        }
        return { ...old, itens };
      });
    } catch (e) {
      setMsg({ tipo: 'warning', texto: `Produto não encontrado: ${cod}` });
    }
    setCodigo('');
    if (codRef.current) codRef.current.focus();
  };

  const alterarQtd = (idx, qtd) => {
    setPdv((old) => {
      const itens = [...old.itens];
      itens[idx].quantidade = Number(qtd) || 0;
      itens[idx].subtotal = itens[idx].quantidade * itens[idx].preco_unitario;
      return { ...old, itens };
    });
  };

  const removerItem = (idx) => {
    setPdv((old) => ({ ...old, itens: old.itens.filter((_, i) => i !== idx) }));
  };

  const totalPDV = pdv.itens.reduce((s, i) => s + (i.subtotal || 0), 0);

  const finalizarVenda = async () => {
    if (pdv.itens.length === 0) { setMsg({ tipo: 'warning', texto: 'Adicione ao menos um item.' }); return; }
    try {
      await api.post('/api/vendas/', {
        vendedor: pdv.vendedor, cliente_nome: pdv.cliente_nome, pagamento: pdv.pagamento,
        desconto: 0, valor_total: totalPDV, itens: pdv.itens,
      });
      setShowPDV(false);
      setPdv({ cliente_nome: '', vendedor: '', pagamento: 'A VISTA', itens: [] });
      setMsg({ tipo: 'success', texto: 'Venda registrada com sucesso!' });
      carregar(''); carregarStats();
    } catch (e) {
      setMsg({ tipo: 'danger', texto: `Erro ao salvar venda: ${e?.response?.data?.detail || e.message}` });
    }
  };

  const abrirDetalhe = async (id) => {
    try { setDetalhe(await api.get(`/api/vendas/${id}`)); } catch (e) { /* ignore */ }
  };

  return (
    <Container>
      <Row className="mb-3 align-items-center">
        <Col><h1>🛒 Vendas</h1></Col>
        <Col className="text-end">
          <Button variant="success" className="me-2" onClick={() => setShowImport(true)} disabled={importando}>
            📥 Importar do Access
          </Button>
          <Button variant="primary" onClick={() => { setShowPDV(true); setTimeout(() => codRef.current?.focus(), 300); }}>
            ➕ Nova Venda (PDV)
          </Button>
        </Col>
      </Row>

      {msg && <Alert variant={msg.tipo} dismissible onClose={() => setMsg(null)}>{msg.texto}</Alert>}

      {stats && (
        <Row className="mb-3">
          <Col md={6}><Card body className="text-center">
            <div className="text-muted small">Total de vendas</div>
            <div className="h4 mb-0">{stats.total_vendas}</div>
          </Card></Col>
          <Col md={6}><Card body className="text-center">
            <div className="text-muted small">Faturamento</div>
            <div className="h4 mb-0">{BRL(stats.faturamento)}</div>
          </Card></Col>
        </Row>
      )}

      <Card>
        <Card.Header>
          <Form onSubmit={(e) => { e.preventDefault(); carregar(busca); }} className="d-flex gap-2">
            <input type="text" className="form-control" placeholder="🔍 Buscar por nº, cliente ou vendedor..."
              value={busca} onChange={(e) => setBusca(e.target.value)} />
            <Button type="submit" variant="outline-primary">Buscar</Button>
          </Form>
        </Card.Header>
        <Card.Body>
          {loading ? (<div className="text-center"><Spinner animation="border" /></div>) : (
            <>
              <div className="text-muted small mb-2">{total} venda(s)</div>
              <Table hover responsive size="sm">
                <thead>
                  <tr>
                    <th>Nº</th><th>Data</th><th>Cliente</th><th>Vendedor</th>
                    <th>Pgto</th><th className="text-end">Total</th><th>Itens</th><th>Origem</th><th></th>
                  </tr>
                </thead>
                <tbody>
                  {vendas.map((v) => (
                    <tr key={v.id} style={{ cursor: 'pointer' }} onClick={() => abrirDetalhe(v.id)}>
                      <td>{v.codigo}</td>
                      <td>{v.data || '—'}</td>
                      <td>{v.cliente_nome || '—'}</td>
                      <td>{v.vendedor || '—'}</td>
                      <td>{v.pagamento || '—'}</td>
                      <td className="text-end">{BRL(v.valor_total)}</td>
                      <td>{v.total_itens}</td>
                      <td><Badge bg={v.origem === 'novo' ? 'primary' : 'secondary'}>{v.origem}</Badge></td>
                      <td>🔎</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {vendas.length === 0 && (
                <p className="text-center text-muted">
                  Nenhuma venda. Clique em <b>Importar do Access</b> para trazer o histórico, ou <b>Nova Venda</b> para vender.
                </p>
              )}
            </>
          )}
        </Card.Body>
      </Card>

      {/* Modal Importação */}
      <Modal show={showImport} onHide={() => setShowImport(false)}>
        <Modal.Header closeButton><Modal.Title>📥 Importar vendas do Access</Modal.Title></Modal.Header>
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
          <small className="text-muted d-block mt-2">Vendas já importadas (mesmo número) não são duplicadas.</small>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImport(false)}>Cancelar</Button>
          <Button variant="success" onClick={importarAccess} disabled={importando}>
            {importando ? (<><Spinner size="sm" animation="border" /> Importando...</>) : '📥 Importar'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Modal PDV */}
      <Modal show={showPDV} onHide={() => setShowPDV(false)} size="lg">
        <Modal.Header closeButton><Modal.Title>🛒 Nova Venda (PDV)</Modal.Title></Modal.Header>
        <Modal.Body>
          <Row className="g-2 mb-3">
            <Col md={5}><Form.Label>Cliente</Form.Label>
              <Form.Control value={pdv.cliente_nome} onChange={(e) => setPdv({ ...pdv, cliente_nome: e.target.value })} placeholder="CONSUMIDOR FINAL" /></Col>
            <Col md={4}><Form.Label>Vendedor</Form.Label>
              <Form.Control value={pdv.vendedor} onChange={(e) => setPdv({ ...pdv, vendedor: e.target.value })} /></Col>
            <Col md={3}><Form.Label>Pagamento</Form.Label>
              <Form.Control value={pdv.pagamento} onChange={(e) => setPdv({ ...pdv, pagamento: e.target.value })} /></Col>
          </Row>

          <Form onSubmit={bipar} className="mb-3">
            <Form.Label>📷 Bipar código de barras</Form.Label>
            <div className="d-flex gap-2">
              <Form.Control ref={codRef} value={codigo} onChange={(e) => setCodigo(e.target.value)}
                placeholder="Passe o leitor ou digite o código e Enter" autoFocus />
              <Button type="submit" variant="outline-primary">Adicionar</Button>
            </div>
          </Form>

          <Table size="sm" bordered>
            <thead>
              <tr><th>Produto</th><th style={{ width: 90 }}>Qtd</th><th className="text-end">Unit.</th><th className="text-end">Subtotal</th><th></th></tr>
            </thead>
            <tbody>
              {pdv.itens.map((it, idx) => (
                <tr key={idx}>
                  <td><small>{it.descricao}</small></td>
                  <td><Form.Control size="sm" type="number" min="0" step="1" value={it.quantidade} onChange={(e) => alterarQtd(idx, e.target.value)} /></td>
                  <td className="text-end">{BRL(it.preco_unitario)}</td>
                  <td className="text-end">{BRL(it.subtotal)}</td>
                  <td><Button size="sm" variant="outline-danger" onClick={() => removerItem(idx)}>✕</Button></td>
                </tr>
              ))}
              {pdv.itens.length === 0 && (
                <tr><td colSpan={5} className="text-center text-muted">Nenhum item. Bipe um produto acima.</td></tr>
              )}
            </tbody>
          </Table>
          <div className="text-end h4">Total: {BRL(totalPDV)}</div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPDV(false)}>Cancelar</Button>
          <Button variant="success" onClick={finalizarVenda}>💾 Finalizar Venda</Button>
        </Modal.Footer>
      </Modal>

      {/* Modal Detalhe */}
      <Modal show={!!detalhe} onHide={() => setDetalhe(null)} size="lg">
        <Modal.Header closeButton><Modal.Title>Venda {detalhe?.codigo}</Modal.Title></Modal.Header>
        <Modal.Body>
          {detalhe && (
            <>
              <p className="mb-1"><b>Cliente:</b> {detalhe.cliente_nome || '—'} &nbsp; <b>Vendedor:</b> {detalhe.vendedor || '—'}</p>
              <p className="mb-1"><b>Data:</b> {detalhe.data || '—'} {detalhe.hora || ''} &nbsp; <b>Pgto:</b> {detalhe.pagamento || '—'}</p>
              <Table size="sm" bordered className="mt-2">
                <thead><tr><th>Cód.</th><th>Produto</th><th>Un.</th><th className="text-end">Qtd</th><th className="text-end">Unit.</th><th className="text-end">Subtotal</th></tr></thead>
                <tbody>
                  {detalhe.itens.map((it) => (
                    <tr key={it.id}>
                      <td><small>{it.codigo_produto}</small></td>
                      <td>{it.descricao}</td>
                      <td>{it.unidade}</td>
                      <td className="text-end">{it.quantidade}</td>
                      <td className="text-end">{BRL(it.preco_unitario)}</td>
                      <td className="text-end">{BRL(it.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              <div className="text-end h5">Total: {BRL(detalhe.valor_total)}</div>
            </>
          )}
        </Modal.Body>
      </Modal>
    </Container>
  );
}
