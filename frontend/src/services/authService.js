import api from './api';

export const authService = {
  // Registro de usuario
  async register(userData) {
    try {
      console.log('📝 Enviando registro:', userData);
      const response = await api.post('/api/auth/register', userData);
      console.log('✅ Registro exitoso:', response.data);
      
      // Si el registro devuelve tokens, guardarlos automáticamente
      if (response.data.tokens?.access_token) {
        localStorage.setItem('token', response.data.tokens.access_token);
        if (response.data.tokens.refresh_token) {
          localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
        }
      }
      
      // Guardar información del usuario
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      console.error('❌ Error en registro:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Error en el registro');
    }
  },

  // Login de usuario
  async login(credentials) {
    try {
      console.log('🔐 Enviando login:', credentials.email);
      const response = await api.post('/api/auth/login', credentials);
      console.log('✅ Login exitoso:', response.data);
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        
        // Guardar refresh token si viene
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        
        // Obtener y guardar información del usuario
        try {
          const userData = await this.getCurrentUser();
          localStorage.setItem('user', JSON.stringify(userData));
        } catch (err) {
          console.warn('⚠️ No se pudo obtener datos del usuario:', err);
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('❌ Error en login:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Error en el login');
    }
  },

  // Obtener información del usuario actual
  async getCurrentUser() {
    try {
      console.log('👤 Obteniendo usuario actual...');
      const response = await api.get('/api/auth/me');
      console.log('✅ Usuario obtenido:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error al obtener usuario:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Error al obtener usuario');
    }
  },

  // Actualizar usuario
  async updateUser(userData) {
    try {
      console.log('✏️ Actualizando usuario...');
      const response = await api.put('/api/auth/me', userData);
      console.log('✅ Usuario actualizado:', response.data);
      
      // Actualizar localStorage
      localStorage.setItem('user', JSON.stringify(response.data));
      
      return response.data;
    } catch (error) {
      console.error('❌ Error al actualizar usuario:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Error al actualizar usuario');
    }
  },

  // Refresh token
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No hay refresh token disponible');
      }

      console.log('🔄 Refrescando token...');
      const response = await api.post('/api/auth/refresh', {
        refresh_token: refreshToken
      });
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
      }
      
      console.log('✅ Token refrescado');
      return response.data;
    } catch (error) {
      console.error('❌ Error al refrescar token:', error.response?.data || error.message);
      // Si falla el refresh, hacer logout
      this.logout();
      throw new Error(error.response?.data?.detail || 'Error al refrescar token');
    }
  },

  // Logout
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        console.log('👋 Cerrando sesión...');
        await api.post('/api/auth/logout', {
          refresh_token: refreshToken
        });
      }
    } catch (error) {
      console.error('⚠️ Error al cerrar sesión en servidor:', error);
      // Continuar con el logout local aunque falle el servidor
    } finally {
      // Limpiar localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      // Redirigir al login
      window.location.href = '/login';
    }
  },

  // Logout de todas las sesiones
  async logoutAll() {
    try {
      console.log('👋👋 Cerrando todas las sesiones...');
      await api.post('/api/auth/logout-all');
    } catch (error) {
      console.error('⚠️ Error al cerrar todas las sesiones:', error);
    } finally {
      // Limpiar localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      // Redirigir al login
      window.location.href = '/login';
    }
  },

  // Verificar si el usuario está autenticado
  isAuthenticated() {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
      // Decodificar el token para verificar si expiró
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirado = payload.exp * 1000 < Date.now();
      
      if (expirado) {
        console.log('⚠️ Token expirado');
        this.logout();
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('❌ Error al verificar token:', error);
      return false;
    }
  },

  // Verificar token en el servidor
  async verifyToken() {
    try {
      const response = await api.get('/api/auth/verify');
      return response.data;
    } catch (error) {
      console.error('❌ Token inválido');
      throw error;
    }
  },

  // Obtener token
  getToken() {
    return localStorage.getItem('token');
  },

  // Obtener usuario del localStorage
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
};