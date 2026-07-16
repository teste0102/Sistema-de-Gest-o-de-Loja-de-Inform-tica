# 🎨 Pattern Drawing (Padrão de Senha) - Feature Documentation

## Overview

The pattern drawing feature allows users to create and record Android-style pattern-based passwords with full replay recording. This is particularly useful for the OS (Ordem de Serviço) creation workflow where technicians need to document the phone's unlock pattern.

**Key Features:**
- ✅ 3x3 grid of interactive dots
- ✅ Visual feedback (green = connected, gray = unconnected)
- ✅ Automatic touch/mouse event recording
- ✅ Pattern replay visualization with animation
- ✅ Minimum 4 dots required for security
- ✅ Mobile-friendly (touch and mouse support)
- ✅ Full offline-first support with Dexie caching

---

## Component Architecture

### Frontend Components

#### 1. **PatternDraw.jsx** (`frontend/src/components/PatternDraw.jsx`)

Main component for drawing and replaying patterns.

**Props:**
```javascript
<PatternDraw
  onPatternComplete={handlePatternComplete}  // Callback when pattern is drawn
  onReplay={false}                            // Enable replay mode
  replayData={replaySequence}                 // Sequence data for replay
/>
```

**Event Flow:**
1. User clicks/touches canvas
2. Component detects dot collision
3. Records (x, y, timestamp) for each touch
4. Visual line drawn between connected dots
5. Number shown in dot indicating sequence order
6. On release: validates (min 4 dots), calls onPatternComplete

**Replay Mode:**
- When `onReplay=true` and `replayData` provided
- Automatically animates the pattern drawing at 100ms intervals
- Shows sequence numbers as dots are connected

---

### Backend Integration

#### 2. **Pattern Endpoints** (`backend/routes/senhas.py`)

**POST `/api/os/{ordem_id}/senhas/pattern`**
- Saves pattern with replay data
- Validates sequence has minimum 4 dots
- Encrypts pattern using AES-256
- Stores replay for visualization
- Returns pattern metadata

**Request:**
```json
{
  "pattern": "1-2-3-4-5",
  "sequence": [
    {"x": 150, "y": 200, "t": 0, "tipo": "toque"},
    {"x": 200, "y": 250, "t": 50, "tipo": "movimento"},
    {"x": 250, "y": 200, "t": 100, "tipo": "toque"}
  ],
  "duracao_ms": 300,
  "dispositivo": {
    "tipo": "browser",
    "navegador": "Mozilla/5.0...",
    "resolucao": "1920x1080"
  },
  "timestamp": "2026-07-16T01:00:00Z"
}
```

**Response:**
```json
{
  "ok": true,
  "senha_id": "uuid-xxx",
  "tipo": "padrao",
  "ordem_id": 1,
  "pattern": "1-2-3-4-5",
  "dots_count": 5,
  "duracao_ms": 300,
  "replay_id": 1,
  "data_criada": "2026-07-16T01:00:00Z",
  "mensagem": "Padrão salvo com sucesso (replay registrado)"
}
```

**GET `/api/os/{ordem_id}/senhas/replay`**
- Retrieves stored replay data
- Used for pattern visualization/verification
- Returns full sequence for animation

**Response:**
```json
{
  "ok": true,
  "ordem_id": 1,
  "sequence": [
    {"x": 150, "y": 200, "t": 0, "tipo": "toque"},
    {"x": 200, "y": 250, "t": 50, "tipo": "movimento"}
  ],
  "duracao_ms": 300,
  "num_eventos": 10,
  "timestamp": "2026-07-16T01:00:00Z"
}
```

---

## Usage Flow

### 1. Creating a Pattern Password

**Step-by-step in UI:**

1. Navigate to "Ferramentas OS" → "Senha" tab
2. Select "Padrão (Desenho)" from tipo dropdown
3. Click "🎨 Desenhar Padrão"
4. PatternDraw component appears
5. Draw pattern by clicking/touching dots (minimum 4)
6. Visual feedback shows:
   - Connected dots turn green
   - Connection lines drawn
   - Sequence numbers shown
   - Duration displayed
7. Release to complete
8. Click "💾 Salvar Senha" to store with replay
9. Backend validates and stores pattern + replay data

**Code Flow:**

```javascript
// In OSPage.jsx
const handlePatternComplete = async (pattern) => {
  const device = {
    tipo: 'browser',
    navegador: navigator.userAgent,
    resolucao: `${window.innerWidth}x${window.innerHeight}`
  };

  const res = await api.post(`/api/os/${ordemId}/senhas/pattern`, {
    pattern: pattern.pattern,           // "1-2-3-4-5"
    sequence: pattern.sequence,         // Touch events
    duracao_ms: pattern.duration,
    dispositivo: device,
    timestamp: pattern.timestamp
  });

  flash('success', 'Padrão salvo com sucesso!');
};
```

### 2. Replaying a Saved Pattern

**Step-by-step in UI:**

1. Load an OS that has a pattern password
2. Senha tab shows "✅ Padrão criado"
3. Click "▶️ Ver Replay do Padrão"
4. PatternDraw component appears in replay mode
5. Animation automatically plays showing:
   - Each dot being connected in sequence
   - Lines drawn between dots
   - Full replay of original drawing

**Code Flow:**

```javascript
const visualizarReplay = async () => {
  const res = await api.get(`/api/os/${ordemId}/senhas/replay`);
  setPatternReplay(res.sequence);
  setMostrarPattern(true);
  // PatternDraw renders with onReplay=true
};
```

---

## Data Storage

### Database Fields

**OrdemServico table:**
```python
# Existing fields used:
node_senha_id: String(50)           # ID of password
senha_tipo: String(20) = "padrao"   # Type of password
senha_cifrada: String(255)          # Encrypted pattern
senha_imagem: Text                  # Pattern metadata (JSON)
replay_dados: Text                  # Replay sequence (JSON)
```

### Replay Data Format

Stored in `OrdemServico.replay_dados` as JSON:
```json
{
  "sequencia": [
    {"x": 150, "y": 200, "t": 0, "tipo": "toque", "forca": 0.8},
    {"x": 200, "y": 250, "t": 50, "tipo": "movimento", "forca": 0.9},
    {"x": 250, "y": 200, "t": 100, "tipo": "toque", "forca": 0.7},
    {"x": 200, "y": 150, "t": 150, "tipo": "levanta"}
  ],
  "duracao_ms": 300,
  "dispositivo": {
    "tipo": "browser",
    "navegador": "...",
    "resolucao": "1920x1080"
  },
  "data_criacao": "2026-07-16T01:00:00Z",
  "num_eventos": 10
}
```

---

## Security Considerations

### Encryption
- Patterns are encrypted using AES-256 before storage
- Encryption handled by `SenhaService.criptografar_padrao()`
- Keys managed by `CryptoService`

### Privacy
- Never expose decrypted patterns in API responses
- Endpoints return only metadata (count, duration, type)
- Replay data is safe (just coordinates, not password verification)

### Validation
- Minimum 4 connected dots required
- Sequence must be in chronological order
- Device info recorded for audit trail

---

## Technical Stack

### Frontend
- **React** with hooks (useState, useRef, useEffect)
- **HTML5 Canvas** for drawing
- **Bootstrap** for layout
- **Dexie.js** for offline caching

### Backend
- **FastAPI** REST endpoints
- **SQLAlchemy ORM** for database
- **ReplayService** for replay recording
- **CryptoService** for encryption

### Database
- **PostgreSQL** for persistent storage
- **JSON columns** for complex data (replay_dados)

---

## API Integration

### Pattern Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/os/{id}/senhas/pattern` | Save pattern with replay |
| GET | `/api/os/{id}/senhas/replay` | Get replay for visualization |
| POST | `/api/os/{id}/senhas` | Create password (generic) |
| GET | `/api/os/{id}/senhas` | Get password info |
| DELETE | `/api/os/{id}/senhas` | Delete password |

### Frontend API Calls

```javascript
// Save pattern
await api.post(`/api/os/${ordemId}/senhas/pattern`, {
  pattern: "1-2-3-4-5",
  sequence: [...],
  duracao_ms: 300,
  dispositivo: {...},
  timestamp: "..."
});

// Get replay
const res = await api.get(`/api/os/${ordemId}/senhas/replay`);
// Use res.sequence for replay visualization
```

---

## Error Handling

### Frontend Validation
```javascript
// PatternDraw validates minimum 4 dots
if (connectedDots.length < MIN_DOTS) {
  flash('warning', 'Padrão deve ter pelo menos 4 pontos');
  return;
}
```

### Backend Validation
```python
# Validate pattern before saving
pattern_dots = request.pattern.split('-')
if len(pattern_dots) < 4:
    raise HTTPException(detail="Padrão deve conectar pelo menos 4 pontos")

# Validate replay sequence
valido, msg = ReplayService.validar_replay(request.sequence)
if not valido:
    raise HTTPException(detail=f"Sequência inválida: {msg}")
```

---

## Testing the Feature

### Manual Testing Steps

1. **Create OS:**
   - Click "Gerar Nova OS"
   - Enter Client ID
   - Note the OS ID

2. **Draw Pattern:**
   - Click "Ferramentas OS" → "Senha"
   - Select "Padrão (Desenho)"
   - Click "Desenhar Padrão"
   - Draw pattern (4+ dots)
   - Click "Salvar Senha"

3. **Verify Saving:**
   - Refresh page
   - Load same OS
   - Check "Status da Senha" shows pattern type
   - See "Ver Replay do Padrão" button

4. **Test Replay:**
   - Click "Ver Replay do Padrão"
   - Watch animation showing pattern being drawn
   - Verify dots connect in correct order

### Sample Test Data

```javascript
// Pattern: 1 → 2 → 3 → 5 (zigzag)
{
  "pattern": "1-2-3-5",
  "sequence": [
    {"x": 100, "y": 100, "t": 0, "tipo": "toque"},
    {"x": 200, "y": 100, "t": 100, "tipo": "toque"},
    {"x": 100, "y": 200, "t": 200, "tipo": "toque"},
    {"x": 200, "y": 300, "t": 300, "tipo": "toque"}
  ],
  "duracao_ms": 300
}
```

---

## Future Enhancements

- [ ] Difficulty levels (simple/medium/hard)
- [ ] Pattern strength indicator
- [ ] Visual pattern hints
- [ ] Biometric fallback
- [ ] Pattern history/audit log
- [ ] Multi-pattern support
- [ ] Screenshot before/after pattern drawing
- [ ] Haptic feedback (mobile)
- [ ] Pattern complexity scoring

---

## Troubleshooting

### Pattern not saving
- Check minimum 4 dots are connected
- Verify API endpoint is accessible
- Check browser console for errors
- Ensure OS is loaded before drawing

### Replay not playing
- Verify pattern was saved with replay
- Check `/api/os/{id}/senhas` shows `tem_replay: true`
- Reload page and try again
- Check database for `replay_dados` field

### Canvas not responding
- Check touch-action: none in CSS
- Verify browser supports Canvas API
- Try different browser
- Clear browser cache

---

## Files Modified/Created

### New Files
- `frontend/src/components/PatternDraw.jsx` - Main component
- `frontend/src/components/PatternDraw.css` - Styling
- `PATTERN_DRAWING_FEATURE.md` - This documentation

### Modified Files
- `frontend/src/pages/OSPage.jsx` - Integrated pattern into Senha tab
- `backend/routes/senhas.py` - Added pattern endpoints
- `backend/services/replay_service.py` - Already existed (used for replay)

---

## References

- [Android Pattern Lock Implementation](https://en.wikipedia.org/wiki/Pattern_lock)
- [HTML5 Canvas Drawing](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [ReplayService Documentation](./backend/services/replay_service.py)
- [SenhaService Documentation](./backend/services/senha_service.py)

---

**Last Updated:** 2026-07-16
**Version:** 1.0
**Status:** ✅ Production Ready
