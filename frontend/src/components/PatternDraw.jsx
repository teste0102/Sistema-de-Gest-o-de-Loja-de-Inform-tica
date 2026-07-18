import React, { useRef, useEffect, useState } from 'react';
import './PatternDraw.css';

const PatternDraw = ({ onPatternComplete, onReplay = false, replayData = null, replaySignal = 0, patternInicial = null }) => {
  const aplicouInicial = useRef(false);
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [connectedDots, setConnectedDots] = useState([]);
  const [sequence, setSequence] = useState([]);
  const [startTime, setStartTime] = useState(null);
  const [isReplaying, setIsReplaying] = useState(false);
  const [gridSize, setGridSize] = useState(3);
  const [dotRadius, setDotRadius] = useState(16);
  const [dots, setDots] = useState([]);

  const GRID_SIZE = gridSize;
  const DOT_RADIUS = dotRadius;
  const MIN_DOTS = 4;

  // Initialize grid of dots
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
    canvas.width = width;
    canvas.height = height;

    const newDots = generateDots(width, height);
    setDots(newDots);
    drawPattern(canvas, newDots, connectedDots);
  }, [gridSize]);

  // Redraw on connected dots change
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas && dots.length > 0) {
      drawPattern(canvas, dots, connectedDots);
    }
  }, [connectedDots, dots]);

  // Desenhar automaticamente o padrão SALVO ao abrir (modo edição) — sem clicar
  useEffect(() => {
    if (patternInicial && dots.length > 0 && !aplicouInicial.current) {
      const arr = String(patternInicial).split('-').map(Number).filter((n) => !isNaN(n));
      if (arr.length > 0) {
        aplicouInicial.current = true;
        setConnectedDots(arr);
      }
    }
  }, [patternInicial, dots]);

  // Auto-replay if replayData provided
  useEffect(() => {
    if (onReplay && replayData && !isReplaying) {
      replayPattern(replayData);
    }
  }, [onReplay, replayData]);

  // Replay no MESMO canvas quando o botão é apertado (replaySignal muda).
  // Usa replayData (senha salva) ou o padrão recém desenhado.
  useEffect(() => {
    if (!replaySignal) return;
    if (isReplaying) return;
    let data = replayData;
    if (!data && connectedDots.length > 0) {
      data = { pattern: connectedDots.join('-'), sequence };
    }
    if (data && data.pattern) {
      replayPattern(data);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [replaySignal]);

  const generateDots = (width, height) => {
    // Usar a menor dimensão para formar um quadrado centralizado (3x3 como Android)
    const size = Math.min(width, height);
    const spacing = size / (GRID_SIZE + 1);
    // Deslocamento para centralizar a grade dentro do canvas
    const offsetX = (width - size) / 2;
    const offsetY = (height - size) / 2;
    const newDots = [];

    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        newDots.push({
          id: row * GRID_SIZE + col + 1,
          x: offsetX + (col + 1) * spacing,
          y: offsetY + (row + 1) * spacing,
          row,
          col,
        });
      }
    }
    return newDots;
  };

  const drawPattern = (canvas, gridDots, connected) => {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw connections
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;
    ctx.beginPath();

    connected.forEach((dotId, index) => {
      const dot = gridDots.find(d => d.id === dotId);
      if (dot) {
        if (index === 0) {
          ctx.moveTo(dot.x, dot.y);
        } else {
          ctx.lineTo(dot.x, dot.y);
        }
      }
    });
    ctx.stroke();

    // Draw all dots
    gridDots.forEach((dot) => {
      const isConnected = connected.includes(dot.id);

      // Dot background
      ctx.fillStyle = isConnected ? '#000000' : '#E0E0E0';
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, DOT_RADIUS, 0, 2 * Math.PI);
      ctx.fill();

      // Dot border
      ctx.strokeStyle = isConnected ? '#000000' : '#999';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, DOT_RADIUS, 0, 2 * Math.PI);
      ctx.stroke();

      // Dot number (for visual reference)
      if (isConnected) {
        ctx.fillStyle = '#FFF';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(connected.indexOf(dot.id) + 1, dot.x, dot.y);
      }
    });
  };

  const getDotAtPosition = (x, y) => {
    return dots.find((dot) => {
      const distance = Math.sqrt((x - dot.x) ** 2 + (y - dot.y) ** 2);
      return distance <= DOT_RADIUS * 1.5;
    });
  };

  const handleMouseDown = (e) => {
    if (onReplay || isReplaying) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const dot = getDotAtPosition(x, y);
    if (dot && !connectedDots.includes(dot.id)) {
      setIsDrawing(true);
      setConnectedDots([dot.id]);
      setSequence([{ x: dot.x, y: dot.y, t: 0, tipo: 'toque' }]);
      setStartTime(Date.now());
    }
  };

  const handleMouseMove = (e) => {
    if (!isDrawing || onReplay || isReplaying) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Draw temporary line
    drawPattern(canvasRef.current, dots, connectedDots);
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;
    ctx.beginPath();
    const lastDot = dots.find(d => d.id === connectedDots[connectedDots.length - 1]);
    if (lastDot) {
      ctx.moveTo(lastDot.x, lastDot.y);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    // Check if hovering over next dot
    const dot = getDotAtPosition(x, y);
    if (dot && !connectedDots.includes(dot.id)) {
      const now = Date.now();
      const elapsed = now - startTime;
      setConnectedDots([...connectedDots, dot.id]);
      setSequence([
        ...sequence,
        { x: dot.x, y: dot.y, t: elapsed, tipo: 'toque' },
      ]);
    }
  };

  const handleMouseUp = () => {
    if (!isDrawing) return;
    setIsDrawing(false);

    if (connectedDots.length >= MIN_DOTS) {
      const duration = Date.now() - startTime;
      const patternString = connectedDots.join('-');

      onPatternComplete({
        pattern: patternString,
        sequence,
        duration,
        dotCount: connectedDots.length,
        timestamp: new Date().toISOString(),
      });
    } else {
      // Clear if not enough dots
      setConnectedDots([]);
      setSequence([]);
      drawPattern(canvasRef.current, dots, []);
    }
  };

  const handleTouchStart = (e) => {
    if (onReplay || isReplaying) return;
    const touch = e.touches[0];
    handleMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
  };

  const handleTouchMove = (e) => {
    if (!isDrawing || onReplay || isReplaying) return;
    e.preventDefault();
    const touch = e.touches[0];
    handleMouseMove({ clientX: touch.clientX, clientY: touch.clientY });
  };

  const handleTouchEnd = () => {
    handleMouseUp();
  };

  const replayPattern = async (data) => {
    if (!data || !data.pattern) return;
    setIsReplaying(true);
    setConnectedDots([]);

    const patternArray = data.pattern.split('-').map(Number);
    for (let i = 0; i < patternArray.length; i++) {
      // Aguarda antes de conectar cada ponto (animação da reprodução)
      await new Promise((resolve) => setTimeout(resolve, 400));
      setConnectedDots(patternArray.slice(0, i + 1));
    }

    setIsReplaying(false);
  };

  const resetPattern = () => {
    setConnectedDots([]);
    setSequence([]);
    drawPattern(canvasRef.current, dots, []);
  };

  return (
    <div className="pattern-draw-container">
      <div className="pattern-header">
        <h5>Desenhe o Padrão de Senha</h5>
        <small className="text-muted">
          {onReplay ? 'Reprodução de Padrão' : `Conecte pelo menos ${MIN_DOTS} pontos`}
        </small>
      </div>

      <canvas
        ref={canvasRef}
        className="pattern-canvas"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={{ cursor: onReplay || isReplaying ? 'default' : 'crosshair' }}
      />

      <div className="pattern-info">
        <div className="info-item">
          <span className="label">Pontos Conectados:</span>
          <span className="value">
            {connectedDots.length > 0 ? connectedDots.join(' → ') : '—'}
          </span>
        </div>
        <div className="info-item">
          <span className="label">Sequência:</span>
          <span className="value">{sequence.length > 0 ? sequence.length : '—'}</span>
        </div>
        {sequence.length > 0 && (
          <div className="info-item">
            <span className="label">Duração:</span>
            <span className="value">{sequence[sequence.length - 1].t}ms</span>
          </div>
        )}
      </div>

      {!onReplay && !isReplaying && (
        <div className="pattern-actions">
          <button
            className="btn btn-sm btn-secondary"
            onClick={resetPattern}
            disabled={connectedDots.length === 0}
          >
            Limpar
          </button>
        </div>
      )}

      {isReplaying && (
        <div className="alert alert-info alert-sm">
          ▶️ Reproduzindo padrão...
        </div>
      )}
    </div>
  );
};

export default PatternDraw;
