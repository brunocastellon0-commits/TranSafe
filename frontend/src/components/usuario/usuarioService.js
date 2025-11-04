import api from '../../services/api';

/**
 * Registra un nuevo usuario en el sistema
 * @param {Object} userData - Datos del usuario
 * @param {string} userData.username - Nombre de usuario
 * @param {string} userData.email - Correo electrónico
 * @param {string} userData.password - Contraseña
 * @param {string} userData.fullName - Nombre completo (opcional)
 * @returns {Promise<Object>} Respuesta del servidor con usuario y tokens
 */
export const registerUser = async (userData) => {
  console.log("=== INICIO REGISTRO ===");
  console.log("Datos recibidos:", {
    username: userData.username,
    email: userData.email,
    fullName: userData.fullName,
    password: "***"
  });
  
  try {
    // ✅ CORREGIDO: Enviar en el formato que espera el backend
    const requestData = {
      username: userData.username,     // ← El backend espera 'username'
      email: userData.email,
      password: userData.password,
      full_name: userData.fullName || userData.username  // ← Opcional pero útil
    };

    console.log("📤 Enviando al servidor:", {
      ...requestData,
      password: "***"
    });
    
    // Realizar petición al backend
    const response = await api.post('/api/auth/register', requestData);

    console.log("✅ Respuesta exitosa del servidor");
    console.log("Datos recibidos:", response.data);

    // Guardar tokens en localStorage si vienen en la respuesta
    if (response.data.tokens) {
      console.log("Guardando tokens en localStorage...");
      
      if (response.data.tokens.access_token) {
        localStorage.setItem('token', response.data.tokens.access_token);
        console.log("✅ Access token guardado");
      }
      
      if (response.data.tokens.refresh_token) {
        localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
        console.log("✅ Refresh token guardado");
      }
    }

    // Guardar información del usuario en localStorage
    if (response.data.user) {
      localStorage.setItem('user', JSON.stringify(response.data.user));
      console.log("✅ Usuario guardado en localStorage");
    }

    console.log("=== REGISTRO COMPLETADO ===");
    return response.data;
    
  } catch (error) {
    console.error("❌ ERROR EN REGISTRO");
    console.error("Error completo:", error);
    
    // Manejar errores de respuesta del servidor
    if (error.response) {
      console.error("Status:", error.response.status);
      console.error("Data:", error.response.data);
      
      // ✅ MEJORADO: Manejar errores de validación de Pydantic (422)
      if (error.response.status === 422) {
        const details = error.response.data?.detail;
        
        if (Array.isArray(details)) {
          // Errores de validación de Pydantic
          const errorMessages = details.map(err => {
            const field = err.loc[err.loc.length - 1];
            const msg = err.msg;
            
            // Traducir mensajes comunes
            if (field === 'username' && msg === 'Field required') {
              return 'El nombre de usuario es requerido';
            }
            if (field === 'username' && msg.includes('at least 3')) {
              return 'El nombre de usuario debe tener al menos 3 caracteres';
            }
            if (field === 'password' && msg.includes('at least 8 characters')) {
              return 'La contraseña debe tener al menos 8 caracteres';
            }
            if (field === 'email' && msg.includes('valid email')) {
              return 'El email no es válido';
            }
            
            return `${field}: ${msg}`;
          });
          
          throw new Error(errorMessages.join('. '));
        }
        
        throw new Error('Datos inválidos. Verifica tu información');
      }
      
      const errorDetail = error.response.data?.detail || error.response.data?.message;
      
      // Errores específicos por código de estado
      if (error.response.status === 400) {
        if (errorDetail) {
          if (typeof errorDetail === 'string' && 
              errorDetail.toLowerCase().includes('email') && 
              (errorDetail.toLowerCase().includes('existe') || 
               errorDetail.toLowerCase().includes('registrado'))) {
            throw new Error('Este email ya está registrado');
          }
          throw new Error(errorDetail);
        }
        throw new Error('Datos de registro inválidos');
      }
      
      if (error.response.status === 500) {
        throw new Error('Error en el servidor. Intenta nuevamente más tarde');
      }
      
      throw new Error(errorDetail || 'Error al registrar usuario');
      
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      console.error("❌ Sin respuesta del servidor");
      console.error("Request:", error.request);
      throw new Error('No se pudo conectar con el servidor. Verifica tu conexión a internet');
      
    } else {
      // Error al configurar la petición
      console.error("❌ Error al configurar petición:", error.message);
      throw new Error('Error inesperado: ' + error.message);
    }
  }
};

/**
 * Valida el formato del email
 */
export const validateEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.trim());
};

/**
 * Valida el nombre de usuario
 */
export const validateUsername = (username) => {
  if (!username || typeof username !== 'string') {
    return false;
  }
  
  const trimmedUsername = username.trim();
  return trimmedUsername.length >= 3 && trimmedUsername.length <= 100;
};

/**
 * Valida la contraseña
 * ✅ CORREGIDO: Mínimo 8 caracteres como requiere el backend
 */
export const validatePassword = (password) => {
  if (!password || typeof password !== 'string') {
    return false;
  }
  
  return password.length >= 8 && password.length <= 100;
};

/**
 * Valida todos los datos del formulario de registro
 */
export const validateRegistrationForm = (formData) => {
  // Validar username
  if (!formData.username || !formData.username.trim()) {
    return { valid: false, error: 'El nombre de usuario es requerido' };
  }
  
  if (!validateUsername(formData.username)) {
    return { valid: false, error: 'El nombre de usuario debe tener entre 3 y 100 caracteres' };
  }

  // Validar email
  if (!formData.email || !formData.email.trim()) {
    return { valid: false, error: 'El email es requerido' };
  }
  
  if (!validateEmail(formData.email)) {
    return { valid: false, error: 'El email no es válido' };
  }

  // Validar contraseña
  if (!formData.password) {
    return { valid: false, error: 'La contraseña es requerida' };
  }
  
  if (!validatePassword(formData.password)) {
    return { valid: false, error: 'La contraseña debe tener al menos 8 caracteres' };
  }

  // Validar confirmación de contraseña
  if (!formData.confirmPassword) {
    return { valid: false, error: 'Debes confirmar tu contraseña' };
  }
  
  if (formData.password !== formData.confirmPassword) {
    return { valid: false, error: 'Las contraseñas no coinciden' };
  }

  return { valid: true, error: null };
};

export default {
  registerUser,
  validateEmail,
  validateUsername,
  validatePassword,
  validateRegistrationForm
};