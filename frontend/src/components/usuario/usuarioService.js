export const handleRegister = async (formData) => {
  try {
    // Validación de contraseñas
    if (formData.password !== formData.confirmPassword) {
      alert("Las contraseñas no coinciden");
      return;
    }

    // Validación de campos
    if (!validateName(formData.name)) {
      alert("Por favor ingresa un nombre válido");
      return;
    }

    if (!validateEmail(formData.email)) {
      alert("Por favor ingresa un email válido");
      return;
    }

    if (!validatePassword(formData.password)) {
      alert("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    console.log("Registro attempt:", formData);
    
    // Aquí iría tu lógica de registro
    // Por ejemplo:
    // const response = await fetch('/api/register', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(formData)
    // });
    
    // const data = await response.json();
    // return data;
    
  } catch (error) {
    console.error("Register error:", error);
    throw error;
  }
};

export const validateName = (name) => {
  return name.trim().length >= 2;
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password) => {
  return password.length >= 6;
};

// Esta función ya no es necesaria ya que usamos navigate en el componente
// export const goToLogin = () => {
//   window.location.href = "/login";
// };