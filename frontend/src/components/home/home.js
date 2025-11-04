import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from '../../services/authService';
import { transactionService } from '../../services/transactionService'; // ✅ AGREGADO

export default function useHome() {
  const navigate = useNavigate();
  const [showBalance, setShowBalance] = useState(true);
  const [user, setUser] = useState(null);
  const [balance, setBalance] = useState(0);
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserData();
    loadTransactions();
  }, []);

  const loadUserData = async () => {
    try {
      // Obtener datos del usuario actual
      const userData = await authService.getCurrentUser();
      setUser(userData);
      
      // Aquí podrías cargar el balance real desde tu API
      setBalance(15420.50); // Por ahora datos de ejemplo
      
    } catch (error) {
      console.error("Error cargando datos del usuario:", error);
      authService.logout();
    }
  };

  const loadTransactions = async () => {
    try {
      // Cargar transacciones reales desde la API
      const transactions = await transactionService.getUserTransactions();
      setMovements(transactions);
    } catch (error) {
      console.error("Error cargando transacciones:", error);
      // Mientras tanto usar datos de ejemplo
      setMovements([
        { id: 1, type: "in", desc: "Transferencia recibida", name: "Juan Pérez", amount: 500.00, date: "Hoy, 14:30" },
        { id: 2, type: "out", desc: "Pago QR - Supermercado", name: "Mercado Central", amount: -125.50, date: "Hoy, 12:15" },
        { id: 3, type: "out", desc: "Transferencia enviada", name: "María López", amount: -200.00, date: "Ayer, 18:45" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
  };

  return {
    showBalance,
    setShowBalance,
    balance,
    movements,
    user,
    loading,
    handleLogout
  };
}