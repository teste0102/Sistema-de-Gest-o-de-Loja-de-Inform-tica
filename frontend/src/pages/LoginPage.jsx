import React, { useState } from 'react';
import { Container, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import api from '../services/api';

// Tela de login. Ao autenticar, chama onLogin(dados) e guarda no localStorage.
export default function LoginPage({ onLogin }) {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState(null);
  const [carregando, setCarregando] = useState(false);

  const entrar = async (e) => {
    e.preventDefault();
    setErro(null);
    setCarregando(true);
    try {
      const res = await api.post('/api/auth/login', { usuario, senha });
      const dados = { usuario: res.usuario, nome: res.nome, token: res.token };
      localStorage.setItem('loja_auth', JSON.stringify(dados));
      onLogin && onLogin(dados);
    } catch (err) {
      setErro(err.response?.data?.detail || 'Falha ao entrar. Verifique usuário e senha.');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <Container style={{ maxWidth: 420, marginTop: '10vh' }}>
      <Card className="shadow">
        <Card.Body className="p-4">
          <div className="text-center mb-4">
            <h3>💼 Loja de Informática</h3>
            <p className="text-muted">Entre para continuar</p>
          </div>
          {erro && <Alert variant="danger">{erro}</Alert>}
          <Form onSubmit={entrar}>
            <Form.Group className="mb-3">
              <Form.Label>Usuário</Form.Label>
              <Form.Control
                autoFocus
                value={usuario}
                onChange={(e) => setUsuario(e.target.value)}
                placeholder="admin"
              />
            </Form.Group>
            <Form.Group className="mb-4">
              <Form.Label>Senha</Form.Label>
              <Form.Control
                type="password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder="••••••"
              />
            </Form.Group>
            <Button type="submit" variant="primary" className="w-100" disabled={carregando}>
              {carregando ? <Spinner size="sm" /> : '🔑 Entrar'}
            </Button>
          </Form>
          <p className="text-center text-muted small mt-3 mb-0">
            Padrão inicial: <strong>admin</strong> / <strong>admin</strong>
          </p>
        </Card.Body>
      </Card>
    </Container>
  );
}
