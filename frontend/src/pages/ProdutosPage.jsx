import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col, Modal, Form, Alert, Badge } from 'react-bootstrap';
import api from '../services/api';

const BRL = (v) => (Number(v) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const PRODUTO_VAZIO = {
  codigo_barras: '', descricao: '', unidade: '', marca: '',
  preco_custo: 0, preco_venda: 0, estoque: 0, categoria: '', status: 'ATIVO', ncm: '',
};

export default function ProdutosPage() {
  const [produtos, setProdutos] = useState([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busca, setBusca] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editando, setEditando] = useState(PRODUTO_VAZIO);
  const [importando, setImportando] = useState(false);
  const [msg, setMsg] = useState(null);
  const [showImport, setShowImport] = useState(false);
  const [imp, setImp] = useState({
    modo: 'local', subpasta: '', arquivo: 'ESTO.MDB', tabela: 'ESTO',
    host: '', porta: 22, usuario: '', senha: '', caminho: '.',
  });

  useEffect(() => { carregar(); carregarStats(); }, []);

  const carregar = async (termo = '') => {
    try {
      setLoading(true);
      const data = await api.get(`/api/produtos/?limit=500&busca=${encodeURIComponent(termo)}`);
      setProdutos(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error('Erro ao carregar produtos:', e);
      setMsg({ tipo: 'danger', texto: 'Erro ao carregar produtos.' });
    } finally {
      setLoading(false);
    }
  };

  const carregarStats = async () => {
    try {
      const s = await api.get('/api/produtos/stats/resumo');
      setStats(s);
    } catch (e) { /* silencioso */ }
  };

  const buscar = (e) => {
    e.preventDefault();
    carregar(busca);
  };

  const abrirNovo = () => { setEditando(PRODUTO_VAZIO); setShowForm(true); };
  const abrirEditar = (p) => { setEditando({ ...p }); setShowForm(true); };

  const salvar = async () => {
    try {
      const payload = {
        ...editando,
        preco_custo: Number(editando.preco_custo) || 0,
        preco_venda: Number(editando.preco_venda) || 0,
        estoque: Number(editando.estoque) || 0,
      };
      if (editando.id) {
        await api.put(`/api/produtos/${editando.id}`, payload);
      } else {
        await api.post('/api/produtos/', payload);
      }
      setShowForm(false);
      setMsg({ tipo: 'success', texto: 'Produto salvo com sucesso!' });
      carregar(busca);
      carregarStats();
    } catch (e) {
      setMsg({ tipo: 'danger', texto: 'Erro ao salvar produto.' });
    }
  };

  const excluir = async (p) => {
    if (!window.confirm(`Excluir "${p.descricao}"?`)) return;
    try {
      await api.delete(`/api/produtos/${p.id}`);
      carregar(busca);
      carregarStats();
    } catch (e) {
      setMsg({ tipo: 'danger', texto: 'Erro ao excluir produto.' });
    }
  };

  const importarAccess = async () => {
    try {
      setImportando(true);
      setMsg(null);
      let r;
      if (imp.modo === 'ssh') {
        r = await api.post('/api/produtos/importar-mdb-ssh', {
          host: imp.host, porta: Number(imp.porta) || 22, usuario: imp.usuario,
          senha: imp.senha, caminho: imp.caminho || '.', arquivo: imp.arquivo, tabela: imp.tabela,
        });
      } else {
        r = await api.post('/api/produtos/importar-mdb', {
          subpasta: imp.subpasta, arquivo: imp.arquivo, tabela: imp.tabela,
        });
      }
      setShowImport(false);
      setMsg({
        tipo: 'success',
        texto: `Importação concluída: ${r.total_lidos} lidos, ${r.criados} criados, ${r.atualizados} atualizados.`,
      });
      carregar('');
      carregarStats();
    } catch (e) {
      const detalhe = e?.response?.data?.detail || e.message;
      setMsg({ tipo: 'danger', texto: `Falha na importação: ${detalhe}` });
    } finally {
      setImportando(false);
    }
  };

  return (
    <Container>
      <Row className="mb-3 align-items-center">
        <Col><h1>📦 Produtos / Estoque</h1></Col>
        <Col className="text-end">
          <Button variant="success" className="me-2" onClick={() => setShowImport(true)} disabled={importando}>
            📥 Importar do Access
          </Button>
          <Button variant="primary" onClick={abrirNovo}>➕ Novo Produto</Button>
        </Col>
      </Row>

      {msg && (
        <Alert variant={msg.tipo} dismissible onClose={() => setMsg(null)}>{msg.texto}</Alert>
      )}

      {stats && (
        <Row className="mb-3">
          <Col md={4}>
            <Card body className="text-center">
              <div className="text-muted small">Total de produtos</div>
              <div className="h4 mb-0">{stats.total_produtos}</div>
            </Card>
          </Col>
          <Col md={4}>
            <Card body className="text-center">
              <div className="text-muted small">Valor em estoque (custo)</div>
              <div className="h4 mb-0">{BRL(stats.valor_estoque_custo)}</div>
            </Card>
          </Col>
          <Col md={4}>
            <Card body className="text-center">
              <div className="text-muted small">Sem estoque</div>
              <div className="h4 mb-0">{stats.sem_estoque}</div>
            </Card>
          </Col>
        </Row>
      )}

      <Card>
        <Card.Header>
          <Form onSubmit={buscar} className="d-flex gap-2">
            <input
              type="text"
              placeholder="🔍 Buscar por descrição, marca, categoria ou código de barras..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="form-control"
            />
            <Button type="submit" variant="outline-primary">Buscar</Button>
          </Form>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <div className="text-center"><Spinner animation="border" /></div>
          ) : (
            <>
              <div className="text-muted small mb-2">{total} produto(s)</div>
              <Table hover responsive size="sm">
                <thead>
                  <tr>
                    <th>Cód. Barras</th>
                    <th>Descrição</th>
                    <th>Marca</th>
                    <th>Categoria</th>
                    <th>Un.</th>
                    <th className="text-end">Custo</th>
                    <th className="text-end">Venda</th>
                    <th className="text-end">Estoque</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {produtos.map((p) => (
                    <tr key={p.id}>
                      <td><small>{p.codigo_barras || '—'}</small></td>
                      <td>{p.descricao}</td>
                      <td>{p.marca || '—'}</td>
                      <td>{p.categoria || '—'}</td>
                      <td>{p.unidade || '—'}</td>
                      <td className="text-end">{BRL(p.preco_custo)}</td>
                      <td className="text-end">{BRL(p.preco_venda)}</td>
                      <td className="text-end">
                        <Badge bg={p.estoque > 0 ? 'success' : 'danger'}>{p.estoque}</Badge>
                      </td>
                      <td className="text-nowrap">
                        <Button size="sm" variant="outline-primary" onClick={() => abrirEditar(p)}>✏️</Button>{' '}
                        <Button size="sm" variant="outline-danger" onClick={() => excluir(p)}>🗑️</Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {produtos.length === 0 && (
                <p className="text-center text-muted">
                  Nenhum produto. Clique em <b>Importar do Access</b> para trazer o estoque do programa antigo.
                </p>
              )}
            </>
          )}
        </Card.Body>
      </Card>

      {/* Modal de importação (pasta na rede / SSH) */}
      <Modal show={showImport} onHide={() => setShowImport(false)}>
        <Modal.Header closeButton>
          <Modal.Title>📥 Importar produtos do Access</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-3 d-flex gap-2">
            <Button variant={imp.modo === 'local' ? 'primary' : 'outline-primary'} size="sm"
              onClick={() => setImp({ ...imp, modo: 'local' })}>📁 Pasta na rede</Button>
            <Button variant={imp.modo === 'ssh' ? 'primary' : 'outline-primary'} size="sm"
              onClick={() => setImp({ ...imp, modo: 'ssh' })}>🔐 Outro PC (SSH)</Button>
          </div>

          {imp.modo === 'local' ? (
            <>
              <Form.Label>Subpasta compartilhada (dentro da pasta montada)</Form.Label>
              <Form.Control className="mb-2" placeholder="ex.: Backup 02.01.2026 (vazio = raiz)"
                value={imp.subpasta} onChange={(e) => setImp({ ...imp, subpasta: e.target.value })} />
              <small className="text-muted">A pasta do outro computador precisa estar mapeada/compartilhada na pasta de dados.</small>
            </>
          ) : (
            <Row className="g-2">
              <Col md={8}><Form.Label>IP do computador</Form.Label>
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
          <small className="text-muted d-block mt-2">Produtos existentes (mesmo código de barras) são atualizados; novos são criados.</small>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImport(false)}>Cancelar</Button>
          <Button variant="success" onClick={importarAccess} disabled={importando}>
            {importando ? (<><Spinner size="sm" animation="border" /> Importando...</>) : '📥 Importar'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Modal de edição / novo */}
      <Modal show={showForm} onHide={() => setShowForm(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{editando.id ? 'Editar Produto' : 'Novo Produto'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row className="g-3">
            <Col md={6}>
              <Form.Label>Código de barras</Form.Label>
              <Form.Control value={editando.codigo_barras || ''} onChange={(e) => setEditando({ ...editando, codigo_barras: e.target.value })} />
            </Col>
            <Col md={6}>
              <Form.Label>Descrição</Form.Label>
              <Form.Control value={editando.descricao || ''} onChange={(e) => setEditando({ ...editando, descricao: e.target.value })} />
            </Col>
            <Col md={4}>
              <Form.Label>Marca</Form.Label>
              <Form.Control value={editando.marca || ''} onChange={(e) => setEditando({ ...editando, marca: e.target.value })} />
            </Col>
            <Col md={4}>
              <Form.Label>Categoria</Form.Label>
              <Form.Control value={editando.categoria || ''} onChange={(e) => setEditando({ ...editando, categoria: e.target.value })} />
            </Col>
            <Col md={4}>
              <Form.Label>Unidade</Form.Label>
              <Form.Control value={editando.unidade || ''} onChange={(e) => setEditando({ ...editando, unidade: e.target.value })} />
            </Col>
            <Col md={4}>
              <Form.Label>Preço de custo (R$)</Form.Label>
              <Form.Control type="number" step="0.01" value={editando.preco_custo} onChange={(e) => setEditando({ ...editando, preco_custo: e.target.value })} />
            </Col>
            <Col md={4}>
              <Form.Label>Preço de venda (R$)</Form.Label>
              <Form.Control type="number" step="0.01" value={editando.preco_venda} onChange={(e) => setEditando({ ...editando, preco_venda: e.target.value })} />
            </Col>
            <Col md={4}>
              <Form.Label>Estoque</Form.Label>
              <Form.Control type="number" step="1" value={editando.estoque} onChange={(e) => setEditando({ ...editando, estoque: e.target.value })} />
            </Col>
            <Col md={6}>
              <Form.Label>NCM (fiscal)</Form.Label>
              <Form.Control value={editando.ncm || ''} onChange={(e) => setEditando({ ...editando, ncm: e.target.value })} />
            </Col>
            <Col md={6}>
              <Form.Label>Status</Form.Label>
              <Form.Control value={editando.status || 'ATIVO'} onChange={(e) => setEditando({ ...editando, status: e.target.value })} />
            </Col>
          </Row>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowForm(false)}>Cancelar</Button>
          <Button variant="primary" onClick={salvar}>💾 Salvar</Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}
