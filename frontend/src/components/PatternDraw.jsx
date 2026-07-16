import React, { useRef, useEffect, useState } from 'react';
import './PatternDraw.css';

const PatternDraw = ({ onPatternComplete, onReplay = false, replayData = null }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [connectedDots, setConnectedDots] = useState([]);
  const [sequence, setSequence] = useState([]);
  const [startTime, setStartTime] = useState(null);
  const [isReplaying, setIsReplaying] = useState(false);
  const [gridSize, setGridSize] = useState(3);
  const [dotRadius, setDotRadius] = useState(20);
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

  // Auto-replay if replayData provided
  useEffect(() => {
    if (onReplay && replayData && !isReplaying) {
      replayPattern(replayData);
    }
  }, [onReplay, replayData]);

  const generateDots = (width, height) => {
    const dotSpacing = width / (GRID_SIZE + 1);
    const newDots = [];

    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        newDots.push({
          id: row * GRID_SIZE + col + 1,
          x: (col + 1) * dotSpacing,
          y: (row + 1) * dotSpacing,
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
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
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
      ctx.fillStyle = isConnected ? '#4CAF50' : '#E0E0E0';
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, DOT_RADIUS, 0, 2 * Math.PI);
      ctx.fill();

      // Dot border
      ctx.strokeStyle = isConnected ? '#388E3C' : '#999';
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
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
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
    setIsReplaying(true);
    const canvas = canvasRef.current;
    setConnectedDots([]);

    for (let i = 0; i < data.sequence.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 100));

      if (i === 0) {
        setConnectedDots([data.pattern.split('-')[0]]);
      } else {
        const patternArray = data.pattern.split('-').map(Number);
        setConnectedDots(patternArray.slice(0, i + 1));
      }
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
