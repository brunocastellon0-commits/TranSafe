import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./usuario.css";
import { handleRegister } from "./usuarioService";

export default function Usuario() {
  const [form, setForm] = useState({ 
    name: "", 
    email: "", 
    password: "", 
    confirmPassword: "" 
  });
  const [visible, setVisible] = useState(false);
  const [focus, setFocus] = useState(null);
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();

  useEffect(() => setVisible(true), []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    handleRegister(form);
  };

  const goToLogin = () => {
    navigate('/login');
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
      {/* Resto del JSX igual pero actualizando el footer */}
      <p className="footer">
        ¿Ya tienes una cuenta?{" "}
        <a href="#" onClick={(e) => { e.preventDefault(); goToLogin(); }} className="link">
          Inicia sesión
        </a>
      </p>
    </div>
  );
}