import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Table, Spinner, Row, Col, Badge, Alert } from 'react-bootstrap';
import api from '../services/api';
import NovaOSWizard from '../components/NovaOSWizard';
import { abrirImpressao, campo } from '../utils/print';

export default function OrdensPage() {
  const [ordens, setOrdens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState(null);

  // Edição via assistente
  const [editando, setEditando] = useState(false);
  const [osEdit, setOsEdit] = useState(null);   // dados completos da OS
  const [novo, setNovo] = useState(false);

  useEffect(() => {
    carregarOrdens();
  }, []);

  const flash = (variant, texto) => {
    setMsg({ variant, texto });
    setTimeout(() => setMsg(null), 5000);
  };

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
    const fechada = String(status || '').toLowerCase().startsWith('fech');
    return <Badge bg={fechada ? 'primary' : 'danger'}>{fechada ? 'Fechada' : 'Aberta'}</Badge>;
  };

  // Abrir o assistente para editar uma OS (carrega dados completos)
  const editar = async (id) => {
    try {
      const res = await api.get(`/api/os/${id}`);
      setOsEdit(res);
      setNovo(false);
      setEditando(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
      flash('danger', `Erro ao abrir OS: ${e.response?.data?.detail || e.message}`);
    }
  };

  const novaOS = () => {
    setOsEdit(null);
    setNovo(true);
    setEditando(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const aoConcluir = () => {
    setEditando(false);
    setOsEdit(null);
    setNovo(false);
    carregarOrdens();
  };

  // Imprimir a OS completa direto da lista
  const imprimir = async (id) => {
    try {
      const os = await api.get(`/api/os/${id}`);
      const html =
        `<h2>Cliente e Endereço</h2>` +
        campo('Cliente', os.nome_cliente) + campo('Rua', os.endereco_rua) +
        campo('Número', os.endereco_numero) + campo('Complemento', os.endereco_complemento) +
        campo('Bairro', os.bairro) + campo('Cidade', os.cidade_os) + campo('Telefone', os.telefone_contato) +
        `<h2>Produto</h2>` +
        campo('Tipo', os.produto_tipo) + campo('Marca', os.marca) + campo('Modelo', os.modelo) + campo('IMEI', os.imei) +
        `<h2>Problema</h2>` + campo('Problema', os.problema_descricao) +
        `<h2>Assinatura</h2>` +
        (os.assinatura_cliente ? `<img src="${os.assinatura_cliente}" />` : '<p>(sem assinatura)</p>') +
        `<div class="assinatura-linha">${os.nome_cliente || 'Cliente'}</div>`;
      abrirImpressao(`OS ${os.numero_os || id} — Completa`, html);
    } catch (e) {
      flash('danger', `Erro ao imprimir: ${e.response?.data?.detail || e.message}`);
    }
  };

  if (loading) {
    return <Spinner animation="border" />;
  }

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h1>📋 Ordens de Serviço</h1>
          <p className="text-muted">Lista de todas as OS — editar, salvar e imprimir</p>
        </Col>
        <Col className="text-end">
          <Button variant="primary" onClick={novaOS}>➕ Nova Ordem</Button>
        </Col>
      </Row>

      {msg && <Alert variant={msg.variant}>{msg.texto}</Alert>}

      {/* Assistente (mesmo das Ferramentas OS) para criar/editar */}
      {editando && (
        <NovaOSWizard
          key={osEdit?.id || 'nova'}
          ordemId={novo ? null : String(osEdit?.id)}
          clienteId={osEdit?.cliente_id || 1}
          numeroOS={osEdit?.numero_os}
          dadosIniciais={novo ? null : osEdit}
          onConcluir={aoConcluir}
          onCancelar={() => { setEditando(false); setOsEdit(null); setNovo(false); }}
          flash={flash}
        />
      )}

      {!editando && (
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
                    <td>#{ordem.numero_os || ordem.numero || ordem.id}</td>
                    <td>{ordem.nome_cliente || ordem.cliente?.nome || '-'}</td>
                    <td>{ordem.data_abertura ? new Date(ordem.data_abertura).toLocaleDateString() : '-'}</td>
                    <td>{getStatusBadge(ordem.status)}</td>
                    <td>R$ {Number(ordem.valor_total || 0).toFixed(2)}</td>
                    <td>
                      <Button size="sm" variant="outline-primary" className="me-1" onClick={() => editar(ordem.id)}>
                        ✏️ Editar
                      </Button>
                      <Button size="sm" variant="outline-dark" onClick={() => imprimir(ordem.id)}>
                        🖨️ Imprimir
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
            {ordens.length === 0 && <p className="text-center">Sem ordens</p>}
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}
