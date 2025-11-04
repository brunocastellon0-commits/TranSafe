import api from './api';

export const transactionService = {
  // Crear una nueva transacción
  async createTransaction(transactionData) {
    try {
      const response = await api.post('/transactions/', transactionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al crear transacción');
    }
  },

  // Obtener transacciones del usuario
  async getUserTransactions() {
    try {
      const response = await api.get('/transactions/');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al obtener transacciones');
    }
  },

  // Obtener una transacción específica
  async getTransactionById(id) {
    try {
      const response = await api.get(`/transactions/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al obtener transacción');
    }
  },

  // Actualizar una transacción
  async updateTransaction(id, transactionData) {
    try {
      const response = await api.put(`/transactions/${id}`, transactionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al actualizar transacción');
    }
  },

  // Eliminar una transacción
  async deleteTransaction(id) {
    try {
      const response = await api.delete(`/transactions/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Error al eliminar transacción');
    }
  }
};