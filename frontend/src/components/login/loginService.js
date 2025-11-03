export const handleLogin = async (formData) => {
  try {
    console.log("Login attempt:", formData);
    
    // Aquí iría tu lógica de autenticación
    // Por ejemplo:
    // const response = await fetch('/api/login', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(formData)
    // });
    
    // const data = await response.json();
    // return data;
    
  } catch (error) {
    console.error("Login error:", error);
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

export const goToRegister = () => {
  window.location.href = "/register";
};