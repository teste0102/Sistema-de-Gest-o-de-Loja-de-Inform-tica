import axios from 'axios';
import Dexie from 'dexie';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Criar banco offline (IndexedDB)
class LojaDB extends Dexie {
  constructor() {
    super('LojaDB');
    this.version(1).stores({
      clientes: 'id',
      ordens: 'id',
      lancamentos: 'id',
      syncQueue: '++id',
    });
  }
}

const db = new LojaDB();

class APIClient {
  constructor() {
    this.isOnline = navigator.onLine;
    window.addEventListener('online', () => this.setOnline(true));
    window.addEventListener('offline', () => this.setOnline(false));
  }

  setOnline(status) {
    this.isOnline = status;
    if (status) {
      this.syncQueue();
    }
  }

  async request(method, endpoint, data = null) {
    const url = `${API_BASE}${endpoint}`;

    try {
      // Tentar chamar API
      let response;
      const config = {
        method,
        url,
        timeout: 5000,
      };

      if (data) {
        config.data = data;
      }

      response = await axios(config);

      // Sucesso: salvar no cache local (best-effort, nunca quebra a UI)
      if (response.status === 200 || response.status === 201) {
        this.cacheResponse(endpoint, response.data).catch((e) =>
          console.warn('Cache local falhou (ignorado):', e.message)
        );
        return response.data;
      }

      return response.data;
    } catch (error) {
      // Erro: verificar cache ou retornar do IndexedDB
      console.warn(`API erro (${method} ${endpoint}):`, error.message);

      if (this.isOnline) {
        throw error;
      }

      // Offline: retornar do cache
      return this.getCachedData(endpoint);
    }
  }

  async cacheResponse(endpoint, data) {
    // Determinar tabela baseado no endpoint
    let storeName = null;
    if (endpoint.includes('clientes')) storeName = 'clientes';
    if (endpoint.includes('ordens')) storeName = 'ordens';
    if (endpoint.includes('financeiro')) storeName = 'lancamentos';

    // Cache é best-effort: qualquer falha é ignorada e não afeta a UI
    try {
      if (storeName && data && Array.isArray(data.items) && db[storeName]) {
        await db[storeName].clear();
        await db[storeName].bulkAdd(data.items);
      }
    } catch (e) {
      console.warn(`Falha ao cachear ${storeName} (ignorado):`, e.message);
    }
  }

  async getCachedData(endpoint) {
    let storeName = null;
    if (endpoint.includes('clientes')) storeName = 'clientes';
    if (endpoint.includes('ordens')) storeName = 'ordens';
    if (endpoint.includes('financeiro')) storeName = 'lancamentos';

    if (!storeName) return null;

    const items = await db[storeName].toArray();
    return { items, total: items.length };
  }

  async addToSyncQueue(tabela, operacao, registro_id, dados) {
    await db.syncQueue.add({
      tabela,
      operacao,
      registro_id,
      dados,
      timestamp: new Date(),
    });
  }

  async syncQueue() {
    const itens = await db.syncQueue.toArray();

    if (itens.length === 0) return;

    try {
      const response = await axios.post(`${API_BASE}/api/sync/push`, {
        itens,
        timestamp: new Date(),
      });

      if (response.data.status === 'success') {
        await db.syncQueue.clear();
        console.log(`✅ ${response.data.sincronizados} registros sincronizados`);
      }
    } catch (error) {
      console.error('Erro ao sincronizar:', error);
    }
  }

  // Métodos CRUD padrão
  async get(endpoint) {
    return this.request('GET', endpoint);
  }

  async post(endpoint, data) {
    return this.request('POST', endpoint, data);
  }

  async put(endpoint, data) {
    return this.request('PUT', endpoint, data);
  }

  async delete(endpoint) {
    return this.request('DELETE', endpoint);
  }
}

export default new APIClient();
