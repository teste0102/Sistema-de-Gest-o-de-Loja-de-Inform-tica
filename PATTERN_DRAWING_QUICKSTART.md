# 🎨 Pattern Drawing - Quick Start Guide

## What is This?

Pattern Drawing allows technicians to visually record how a phone's unlock pattern looks. This is **not a password**, but a **visual record** of the pattern for documentation purposes during service orders (OS).

**Example Use Case:**
- Customer brings broken phone with pattern lock
- Technician draws the pattern on screen to record it
- System captures the drawing sequence with timestamps
- Later, technician can replay the pattern to verify it

---

## Getting Started (5 minutes)

### Step 1: Create/Load an Order of Service (OS)

1. Go to "Ferramentas OS" page
2. Either:
   - **Create new:** Enter Client ID → Click "🆕 Gerar Número OS"
   - **Load existing:** Enter OS ID → Click "📂 Carregar OS"

Example:
```
Client ID: 1
→ Creates: OS-20260716-00001
```

### Step 2: Draw a Pattern

1. Click "🔐 Senha" tab
2. In the dropdown, select **"Padrão (Desenho)"**
3. Click **"🎨 Desenhar Padrão"** button

A canvas will appear with a 3×3 grid of dots:
```
⭕ ⭕ ⭕
⭕ ⭕ ⭕
⭕ ⭕ ⭕
```

### Step 3: Draw by Connecting Dots

- **Click/Touch the first dot**
- **Move to next dot** (a line will draw)
- **Continue connecting** (minimum 4 dots required)
- **Lift your finger/mouse** to finish

**Visual Feedback:**
- ✅ Green dots = connected
- ⚪ Gray dots = not connected yet
- Numbers show the order: 1 → 2 → 3 → 4 → ...

**Example pattern:**
```
1️⃣ — 2️⃣ ⭕
⭕ — 3️⃣ ⭕
⭕ ⭕ — 4️⃣
```

### Step 4: Save the Pattern

After drawing:
- Pattern info shows at bottom:
  - "Pontos Conectados: 1 → 2 → 3 → 4"
  - "Duração: 234ms"
- Click **"💾 Salvar Senha"** to save

✅ **Success message:** "Padrão salvo com sucesso! (4 pontos conectados)"

---

## Viewing a Saved Pattern

### Replay the Pattern

1. Load an OS with a saved pattern
2. Click "🔐 Senha" tab
3. Status shows: "✅ Padrão criado"
4. Click **"▶️ Ver Replay do Padrão"**

The pattern will **automatically animate**, showing:
- Each dot being connected in sequence
- Lines drawn between dots
- Full replay of how it was originally drawn

### Pattern Info

The status area shows:
- ✅ **Padrão criado** = Pattern is saved
- 📅 **Data criação** = When it was created
- ⏱️ **Duração** = How long it took to draw

---

## Tips & Tricks

### Drawing Patterns

**✅ DO:**
- Connect at least 4 dots
- Draw steadily for better recording
- Use dots in sequence (1→2→3→4...)
- Dots can be connected horizontally, vertically, or diagonally

**❌ DON'T:**
- Connect fewer than 4 dots (will be rejected)
- Skip dots (must connect consecutively)
- Draw too fast (causes jitter)

### Pattern Examples

**Simple (4 dots):**
```
1️⃣ 2️⃣ ⭕
⭕ ⭕ ⭕
⭕ ⭕ 4️⃣
```

**Medium (6 dots):**
```
1️⃣ 2️⃣ 3️⃣
⭕ 4️⃣ ⭕
⭕ 5️⃣ 6️⃣
```

**Complex (9 dots - all connected):**
```
1️⃣ 2️⃣ 3️⃣
4️⃣ 5️⃣ 6️⃣
7️⃣ 8️⃣ 9️⃣
```

---

## Troubleshooting

### "Padrão deve ter pelo menos 4 pontos"

**Problem:** Pattern was rejected
**Solution:** Make sure you connected at least 4 dots

### Pattern won't save

**Problem:** "Erro ao salvar padrão"
**Solution:**
1. Make sure OS is loaded (check the blue badge at top)
2. Check internet connection
3. Try drawing with 5+ dots to be safe

### Can't see replay button

**Problem:** "▶️ Ver Replay do Padrão" is missing
**Solution:**
1. Refresh page
2. Load OS again
3. Pattern may not have been saved - try drawing again

### Drawing is too slow/jittery

**Problem:** Animation doesn't look smooth
**Solution:**
1. Draw with steady, continuous motion
2. Don't stop between dots
3. Close other browser tabs to free up resources

---

## How It Works (Technical Overview)

### What Gets Recorded?

For each touch, the system records:
- **x, y coordinates** - Position on screen
- **t (time)** - When the touch happened (milliseconds)
- **tipo** - Type of action (toque=touch, movimento=movement)

**Example:**
```
[
  {x: 150, y: 200, t: 0, tipo: "toque"},
  {x: 200, y: 250, t: 50, tipo: "movimento"},
  {x: 250, y: 200, t: 100, tipo: "toque"}
]
```

### Storage

- Pattern is **encrypted** before storage (AES-256)
- **Never stored as plain text** in database
- Replay data stored for replay visualization
- Device info (browser, resolution) also recorded for audit trail

### Security

✅ **Encrypted** in database
✅ **Never exposed** in API responses
✅ **Audit trail** with timestamps
✅ **Cannot be recovered** once deleted

---

## Use Cases

### 1. Phone with Pattern Lock

**Technician's workflow:**
1. Customer brings phone with pattern lock
2. Technician asks: "What's the pattern?"
3. Customer draws it on the tablet
4. System records it in the OS
5. Later, tech can verify with replay

### 2. Pattern Verification

**Before repair:**
1. Load the OS
2. View replay of the pattern
3. Verify it matches phone before modification
4. Proceed with repair

### 3. Pattern Documentation

**For records:**
- Pattern captured with timestamp
- Visual proof of pattern at time of service
- Useful if disputes arise about phone security

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Draw Pattern | Click/Touch + Drag |
| Clear Pattern | Click "Limpar" button |
| Cancel | Click "Cancelar" button |
| Replay | Click "▶️ Ver Replay" |

---

## FAQ

**Q: Can I redraw the pattern if I make a mistake?**
A: Yes! Click "Limpar" to clear and start over, or click "✏️ Redefinir Padrão" after saving.

**Q: Is this secure?**
A: Yes! The pattern is encrypted (AES-256) and never stored as plain text.

**Q: Can multiple patterns be saved?**
A: Currently, one pattern per OS. To save a new one, delete the old pattern first.

**Q: Why minimum 4 dots?**
A: Android standard requires at least 4 points for pattern locks.

**Q: Can I use this offline?**
A: Yes! The system supports offline-first mode with Dexie caching.

**Q: How do I delete a pattern?**
A: Click "🗑️ Remover" button in the Senha tab.

---

## Next Steps

- ✅ Pattern drawing implemented
- 📋 Pattern replay working
- 🔐 Encryption in place
- 📊 Database storage configured

**Coming Soon:**
- Pattern strength indicator
- Difficulty levels
- Pattern history tracking
- Multi-pattern support

---

## Need Help?

1. Check the **Troubleshooting** section above
2. Review **PATTERN_DRAWING_FEATURE.md** for detailed docs
3. Check browser console (F12) for error messages
4. Verify internet connection and API access

---

**Last Updated:** 2026-07-16
**Feature Status:** ✅ Live & Ready
