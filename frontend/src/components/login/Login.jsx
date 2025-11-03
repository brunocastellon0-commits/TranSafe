import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";
import { handleLogin } from "./loginService";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [visible, setVisible] = useState(false);
  const [focus, setFocus] = useState(null);
  const [showPass, setShowPass] = useState(false);
  const navigate = useNavigate();

  useEffect(() => setVisible(true), []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    handleLogin(form);
  };

  const goToRegister = () => {
    navigate('/register');
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
    <div className="login-container">
      {/* Background Circles */}
      <div className="circles-wrapper">
        {circles.map((c, i) => (
          <div
            key={i}
            className={`circle bg-${c.color} ${c.pos}`}
            style={{ width: c.size, height: c.size, animationDelay: `${c.delay}s` }}
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

      {/* Login Card */}
      <div className={`card ${visible ? "visible" : ""}`}>
        <div className="header">
          <div className="icon-wrapper">
            <div className="icon-circle">
              <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" 
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
            </div>
          </div>
          <h1 className="title">Bienvenido</h1>
          <p className="subtitle">Inicia sesión para continuar</p>
        </div>

        <div className="form-wrapper">
          {/* Email */}
          <div className="input-group">
            <label className="label">Correo electrónico</label>
            <div className="input-wrapper">
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                onFocus={() => setFocus("email")}
                onBlur={() => setFocus(null)}
                placeholder="tu@email.com"
                required
                className="input"
              />
              <div className={`glow ${focus === "email" ? "active" : ""}`} />
            </div>
          </div>

          {/* Password */}
          <div className="input-group">
            <label className="label">Contraseña</label>
            <div className="input-wrapper">
              <input
                type={showPass ? "text" : "password"}
                name="password"
                value={form.password}
                onChange={handleChange}
                onFocus={() => setFocus("password")}
                onBlur={() => setFocus(null)}
                placeholder="••••••••"
                required
                className="input input-with-icon"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="eye-btn"
              >
                {showPass ? (
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
              <div className={`glow ${focus === "password" ? "active" : ""}`} />
            </div>
          </div>

          {/* Button */}
          <button type="button" onClick={handleSubmit} className="btn">
            <span className="btn-text">Iniciar sesión</span>
            <div className="btn-bg" />
            <div className="btn-shine-wrapper">
              <div className="btn-shine" />
            </div>
          </button>
        </div>

        <p className="footer">
          ¿No tienes una cuenta?{" "}
          <a href="#" onClick={(e) => { e.preventDefault(); goToRegister(); }} className="link">
            Regístrate
          </a>
        </p>
      </div>
    </div>
  );
}