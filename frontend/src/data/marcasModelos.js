// Marcas e modelos comuns pré-cadastrados para o assistente de OS.
// O usuário pode escolher da lista ou digitar um valor livre ("Outra" / "Outro modelo").

export const MARCAS_CELULAR = [
  'Samsung',
  'Apple',
  'Xiaomi',
  'Motorola',
  'LG',
  'Asus',
  'Realme',
  'Outra',
];

export const MODELOS_POR_MARCA = {
  Samsung: [
    'Galaxy S24', 'Galaxy S23', 'Galaxy S22', 'Galaxy S21', 'Galaxy S20',
    'Galaxy A54', 'Galaxy A34', 'Galaxy A14', 'Galaxy A13', 'Galaxy A03',
    'Galaxy M54', 'Galaxy Note 20', 'Galaxy Z Flip', 'Galaxy Z Fold', 'Outro modelo',
  ],
  Apple: [
    'iPhone 15 Pro Max', 'iPhone 15 Pro', 'iPhone 15', 'iPhone 14 Pro', 'iPhone 14',
    'iPhone 13', 'iPhone 12', 'iPhone 11', 'iPhone XR', 'iPhone SE', 'Outro modelo',
  ],
  Xiaomi: [
    'Redmi Note 13', 'Redmi Note 12', 'Redmi Note 11', 'Redmi 12', 'Redmi 10',
    'Poco X6', 'Poco X5', 'Poco M5', 'Mi 11', 'Outro modelo',
  ],
  Motorola: [
    'Moto G84', 'Moto G73', 'Moto G54', 'Moto G32', 'Moto G22',
    'Moto E32', 'Moto Edge 40', 'Moto Edge 30', 'Outro modelo',
  ],
  LG: [
    'K62', 'K52', 'K42', 'K22', 'Velvet', 'G8', 'Outro modelo',
  ],
  Asus: [
    'Zenfone 10', 'Zenfone 9', 'Zenfone 8', 'ROG Phone 7', 'ROG Phone 6', 'Outro modelo',
  ],
  Realme: [
    'Realme 11', 'Realme 10', 'Realme 9', 'Realme C55', 'Realme C35', 'Outro modelo',
  ],
  Outra: ['Outro modelo'],
};

// Tipos de produto suportados no assistente
export const TIPOS_PRODUTO = [
  { valor: 'celular', label: '📱 Celular' },
  { valor: 'pc', label: '🖥️ PC' },
  { valor: 'pc_gamer', label: '🎮 PC Gamer' },
  { valor: 'outro', label: '📦 Outro' },
];
