import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./usuario.css";
import api from '../../services/api';

export default function Usuario() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    fullName: ""
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isVisible, setIsVisible] = useState(false);
  const [focusedField, setFocusedField] = useState(null);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setErrorMessage("");
  };

  const validateForm = () => {
    // Validar username
    if (!formData.username.trim()) {
      setErrorMessage("El nombre de usuario es requerido");
      return false;
    }

    if (formData.username.trim().length < 3) {
      setErrorMessage("El nombre de usuario debe tener al menos 3 caracteres");
      return false;
    }

    if (formData.username.trim().length > 100) {
      setErrorMessage("El nombre de usuario no puede tener más de 100 caracteres");
      return false;
    }

    // Validar email
    if (!formData.email.trim()) {
      setErrorMessage("El email es requerido");
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setErrorMessage("El email no es válido");
      return false;
    }

    // Validar contraseña
    if (!formData.password) {
      setErrorMessage("La contraseña es requerida");
      return false;
    }

    if (formData.password.length < 8) {
      setErrorMessage("La contraseña debe tener al menos 8 caracteres");
      return false;
    }

    // Validar confirmación
    if (formData.password !== formData.confirmPassword) {
      setErrorMessage("Las contraseñas no coinciden");
      return false;
    }

    return true;
  };

  const onSubmit = async () => {
    console.log("========================================");
    console.log("🔵 INICIANDO REGISTRO");
    console.log("========================================");
    
    setErrorMessage("");
    setSuccessMessage("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // ✅ FORMATO EXACTO QUE ESPERA EL BACKEND
      const userData = {
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        full_name: formData.fullName.trim() || formData.username.trim()
      };

      console.log("📤 Enviando al servidor:", {
        ...userData,
        password: "***" // Ocultar password en logs
      });
      
      const response = await api.post('/api/auth/register', userData);
      
      console.log("✅ Registro exitoso:", response.data);

      // Guardar tokens
      if (response.data.tokens) {
        if (response.data.tokens.access_token) {
          localStorage.setItem('token', response.data.tokens.access_token);
        }
        if (response.data.tokens.refresh_token) {
          localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
        }
      }

      // Guardar usuario
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      setSuccessMessage("¡Cuenta creada exitosamente!");
      
      // Limpiar formulario
      setFormData({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        fullName: ""
      });

      // Redirigir después de 2 segundos
      setTimeout(() => {
        navigate("/login");
      }, 2000);

    } catch (error) {
      console.error("❌ Error en registro:", error);
      
      // Manejar errores específicos
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;

        console.error("Status:", status);
        console.error("Data:", data);

        if (status === 422) {
          // Errores de validación de Pydantic
          if (Array.isArray(data.detail)) {
            const errors = data.detail.map(err => {
              const field = err.loc[err.loc.length - 1];
              const msg = err.msg;
              
              // Traducir errores comunes
              if (field === 'username' && msg === 'Field required') {
                return 'El nombre de usuario es requerido';
              }
              if (field === 'username' && msg.includes('at least 3')) {
                return 'El nombre de usuario debe tener al menos 3 caracteres';
              }
              if (field === 'password' && msg.includes('at least 8')) {
                return 'La contraseña debe tener al menos 8 caracteres';
              }
              if (field === 'email') {
                return 'El email no es válido';
              }
              
              return `${field}: ${msg}`;
            });
            
            setErrorMessage(errors.join('. '));
          } else {
            setErrorMessage('Datos inválidos. Verifica tu información');
          }
        } else if (status === 400) {
          const detail = data.detail || data.message;
          if (typeof detail === 'string' && detail.toLowerCase().includes('email')) {
            setErrorMessage('Este email ya está registrado');
          } else {
            setErrorMessage(detail || 'Error al registrar usuario');
          }
        } else if (status === 500) {
          setErrorMessage('Error en el servidor. Intenta nuevamente más tarde');
        } else {
          setErrorMessage(data.detail || data.message || 'Error al registrar usuario');
        }
      } else if (error.request) {
        setErrorMessage('No se pudo conectar con el servidor. Verifica tu conexión');
      } else {
        setErrorMessage('Error inesperado: ' + error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const circles = [
    { size: 500, color: "blue-900", pos: "-top-64 -left-64", delay: 0 },
    { size: 400, color: "slate-700", pos: "top-20 -right-48", delay: 2 },
    { size: 450, color: "blue-800", pos: "-bottom-56 left-1/4", delay: 4 },
    { size: 350, color: "slate-600", pos: "bottom-10 -right-32", delay: 1 },
    { size: 480, color: "blue-950", pos: "top-1/3 -left-48", delay: 3 },
    { size: 380, color: "slate-800", pos: "-bottom-32 right-1/3", delay: 5 },
  ];

  return (
    <div className="register-container">
      {/* Background Circles */}
      <div className="circles-wrapper">
        {circles.map((c, i) => (
          <div
            key={i}
            className={`circle bg-${c.color} ${c.pos}`}
            style={{ 
              width: c.size, 
              height: c.size, 
              animationDelay: `${c.delay}s` 
            }}
          />
        ))}
      </div>

      {/* Particles */}
      {[...Array(30)].map((_, i) => (
        <div
          key={i}
          className="particle"
          style={{
            width: Math.random() * 4 + 1,
            height: Math.random() * 4 + 1,
            backgroundColor: Math.random() > 0.5 ? "#fff" : "#60a5fa",
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animation: `float ${5 + Math.random() * 10}s ease-in-out infinite`,
            animationDelay: `${Math.random() * 5}s`
          }}
        />
      ))}

      {/* Register Card */}
      <div className={`card ${isVisible ? "visible" : ""}`}>
        <div className="header">
          <div className="icon-wrapper">
            <div className="icon-circle">
              <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" 
                  d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" 
                />
              </svg>
            </div>
          </div>
          <h1 className="title">Crear Cuenta</h1>
          <p className="subtitle">Regístrate para comenzar</p>
        </div>

        <div className="form-wrapper">
          {/* Success Message */}
          {successMessage && (
            <div style={{
              padding: '0.75rem',
              backgroundColor: '#dcfce7',
              color: '#16a34a',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              textAlign: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}>
              <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              {successMessage}
            </div>
          )}

          {/* Error Message */}
          {errorMessage && (
            <div style={{
              padding: '0.75rem',
              backgroundColor: '#fee2e2',
              color: '#dc2626',
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              textAlign: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}>
              <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {errorMessage}
            </div>
          )}

          {/* Username Input */}
          <div className="input-group">
            <label className="label">Nombre de usuario *</label>
            <div className="input-wrapper">
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                onFocus={() => setFocusedField("username")}
                onBlur={() => setFocusedField(null)}
                placeholder="juanperez123"
                disabled={isLoading || successMessage}
                className="input"
                autoComplete="username"
              />
              <div className={`glow ${focusedField === "username" ? "active" : ""}`} />
            </div>
            <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
              Mínimo 3 caracteres, máximo 100
            </p>
          </div>

          {/* Full Name Input (Optional) */}
          <div className="input-group">
            <label className="label">Nombre completo (opcional)</label>
            <div className="input-wrapper">
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                onFocus={() => setFocusedField("fullName")}
                onBlur={() => setFocusedField(null)}
                placeholder="Juan Pérez"
                disabled={isLoading || successMessage}
                className="input"
                autoComplete="name"
              />
              <div className={`glow ${focusedField === "fullName" ? "active" : ""}`} />
            </div>
          </div>

          {/* Email Input */}
          <div className="input-group">
            <label className="label">Correo electrónico *</label>
            <div className="input-wrapper">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                onFocus={() => setFocusedField("email")}
                onBlur={() => setFocusedField(null)}
                placeholder="tu@email.com"
                disabled={isLoading || successMessage}
                className="input"
                autoComplete="email"
              />
              <div className={`glow ${focusedField === "email" ? "active" : ""}`} />
            </div>
          </div>

          {/* Password Input */}
          <div className="input-group">
            <label className="label">Contraseña *</label>
            <div className="input-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                onFocus={() => setFocusedField("password")}
                onBlur={() => setFocusedField(null)}
                placeholder="••••••••"
                disabled={isLoading || successMessage}
                className="input input-with-icon"
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="eye-btn"
                disabled={isLoading || successMessage}
                tabIndex={-1}
              >
                {showPassword ? (
                  <svg className="eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
              <div className={`glow ${focusedField === "password" ? "active" : ""}`} />
            </div>
            <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
              Mínimo 8 caracteres
            </p>
          </div>

          {/* Confirm Password Input */}
          <div className="input-group">
            <label className="label">Confirmar contraseña *</label>
            <div className="input-wrapper">
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                onFocus={() => setFocusedField("confirmPassword")}
                onBlur={() => setFocusedField(null)}
                placeholder="••••••••"
                disabled={isLoading || successMessage}
                className="input input-with-icon"
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="eye-btn"
                disabled={isLoading || successMessage}
                tabIndex={-1}
              >
                {showConfirmPassword ? (
                  <svg className="eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="eye-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
              <div className={`glow ${focusedField === "confirmPassword" ? "active" : ""}`} />
            </div>
          </div>

          {/* Submit Button */}
          <div style={{ position: 'relative', marginTop: '0.5rem' }}>
            <button 
              type="button"
              onClick={onSubmit}
              disabled={isLoading || successMessage}
              style={{
                position: 'relative',
                width: '100%',
                background: 'linear-gradient(to right, #1e3a8a, #1e40af)',
                color: 'white',
                padding: '1rem',
                borderRadius: '1rem',
                fontWeight: 600,
                border: 'none',
                cursor: isLoading || successMessage ? 'not-allowed' : 'pointer',
                opacity: isLoading || successMessage ? 0.6 : 1,
                fontSize: '1rem',
                zIndex: 10,
                transition: 'all 0.3s'
              }}
            >
              {isLoading ? "Creando cuenta..." : successMessage ? "¡Cuenta creada!" : "Crear cuenta"}
            </button>
          </div>
        </div>

        <p className="footer">
          ¿Ya tienes una cuenta?{" "}
          <button 
            onClick={() => navigate('/login')}
            className="link"
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer'
            }}
          >
            Inicia sesión
          </button>
        </p>
      </div>
    </div>
  );
}