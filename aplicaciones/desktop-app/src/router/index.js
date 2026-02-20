const BASE_URL = 'http://127.0.0.1:5000';

export const apiFetch = async (endpoint, options = {}) => {
  const url = `${BASE_URL}${endpoint}`;
  
  // Configuramos cabeceras por defecto
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Si tenemos un token guardado, lo añadimos automáticamente
  const token = localStorage.getItem('user-token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  // Fetch no lanza error en códigos 400 o 500, hay que manejarlo a mano
  if (!response.ok) {
    const errorData = await response.json();
    throw errorData; 
  }

  return response.json();
};

// TODO REVISAR