import { authService } from '../../services/authService';

export const handleLogin = async (formData, navigate) => {
  try {
    console.log('🔐 Intentando login con:', formData.email);
    
    const response = await authService.login({
      email: formData.email,
      password: formData.password
    });
    
    console.log("✅ Login exitoso:", response);
    
    // Redirigir al home después del login exitoso
    if (navigate) {
      navigate('/home');
    }
    
    return response;
    
  } catch (error) {
    console.error("❌ Login error:", error);
    throw error;
  }
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password) => {
  return password.length >= 6;
};