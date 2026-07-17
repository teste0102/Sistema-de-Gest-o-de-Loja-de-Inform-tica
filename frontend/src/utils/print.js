// Utilitário de impressão: abre uma janela limpa com cabeçalho da loja
// e imprime apenas o conteúdo passado (uma seção/janela por vez).

export function abrirImpressao(subtitulo, htmlConteudo) {
  const win = window.open('', '_blank', 'width=820,height=640');
  if (!win) {
    alert('Permita pop-ups para imprimir.');
    return;
  }
  const data = new Date().toLocaleString('pt-BR');
  win.document.write(`
    <!doctype html>
    <html lang="pt-BR"><head><meta charset="utf-8" />
    <title>${subtitulo || 'Impressão'}</title>
    <style>
      * { box-sizing: border-box; }
      body { font-family: Arial, Helvetica, sans-serif; color: #222; padding: 28px; }
      .cab { border-bottom: 3px solid #333; padding-bottom: 10px; margin-bottom: 18px; display:flex; justify-content:space-between; align-items:flex-end; }
      .cab h1 { margin: 0; font-size: 20px; }
      .cab .sub { color: #555; font-size: 13px; text-align:right; }
      h2 { font-size: 16px; margin: 0 0 12px; }
      .campo { margin: 6px 0; font-size: 14px; }
      .campo b { display: inline-block; min-width: 150px; color:#333; }
      table { width: 100%; border-collapse: collapse; margin-top: 8px; }
      td, th { border: 1px solid #ccc; padding: 6px 8px; text-align: left; font-size: 13px; }
      img { max-width: 320px; border: 1px solid #ddd; }
      .assinatura-linha { margin-top: 40px; border-top: 1px solid #333; width: 300px; text-align:center; padding-top:4px; font-size:12px; }
      @media print { .noprint { display: none; } }
    </style></head>
    <body>
      <div class="cab">
        <h1>💼 Loja de Informática</h1>
        <div class="sub">${subtitulo || ''}<br/>${data}</div>
      </div>
      ${htmlConteudo}
      <script>window.onload = function(){ setTimeout(function(){ window.print(); }, 200); };</script>
    </body></html>
  `);
  win.document.close();
}

// Helpers para montar linhas de campo
export function campo(rotulo, valor) {
  if (valor === undefined || valor === null || valor === '') return '';
  return `<div class="campo"><b>${rotulo}:</b> ${String(valor)}</div>`;
}
