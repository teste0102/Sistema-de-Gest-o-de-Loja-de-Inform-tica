import React, { useRef, useState, useEffect } from 'react';

// Captura de assinatura digital via canvas.
// Funciona com mouse, touch e canetas USB que emulam mouse/tablet.
// Props:
//   onChange(base64|null) - chamado quando a assinatura muda
//   valorInicial (base64) - assinatura já existente (modo edição)
const AssinaturaDigital = ({ onChange, valorInicial = null }) => {
  const canvasRef = useRef(null);
  const [desenhando, setDesenhando] = useState(false);
  const [temAssinatura, setTemAssinatura] = useState(false);
  const ultimoPonto = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Ajustar resolução do canvas ao tamanho exibido
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Carregar assinatura existente (modo edição)
    if (valorInicial) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        setTemAssinatura(true);
      };
      img.src = valorInicial;
    }
  }, [valorInicial]);

  const getPos = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  };

  const iniciar = (e) => {
    e.preventDefault();
    setDesenhando(true);
    ultimoPonto.current = getPos(e);
  };

  const mover = (e) => {
    if (!desenhando) return;
    e.preventDefault();
    const ctx = canvasRef.current.getContext('2d');
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(ultimoPonto.current.x, ultimoPonto.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ultimoPonto.current = pos;
    setTemAssinatura(true);
  };

  const finalizar = () => {
    if (!desenhando) return;
    setDesenhando(false);
    if (onChange && temAssinatura) {
      onChange(canvasRef.current.toDataURL('image/png'));
    }
  };

  const limpar = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setTemAssinatura(false);
    if (onChange) onChange(null);
  };

  return (
    <div>
      <div style={{ fontSize: 13, color: '#666', marginBottom: 6 }}>
        ✍️ Assine no quadro abaixo (caneta USB, mouse ou toque)
      </div>
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: 180,
          border: '2px dashed #999',
          borderRadius: 6,
          background: '#fff',
          touchAction: 'none',
          cursor: 'crosshair',
          display: 'block',
        }}
        onMouseDown={iniciar}
        onMouseMove={mover}
        onMouseUp={finalizar}
        onMouseLeave={finalizar}
        onTouchStart={iniciar}
        onTouchMove={mover}
        onTouchEnd={finalizar}
      />
      <div style={{ marginTop: 8, display: 'flex', gap: 8, alignItems: 'center' }}>
        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={limpar}>
          🧹 Limpar Assinatura
        </button>
        {temAssinatura && (
          <span style={{ color: '#198754', fontSize: 13 }}>✅ Assinatura capturada</span>
        )}
      </div>
    </div>
  );
};

export default AssinaturaDigital;
