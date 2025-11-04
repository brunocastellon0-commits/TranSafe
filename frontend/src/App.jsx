import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from "./components/login/login.jsx"  
import Usuario from "./components/usuario/usuario.jsx" 
import Home from "./components/home/home.jsx"  
import { authService } from './services/authService.js'
import './App.css'

const ProtectedRoute = ({ children }) => {
  return authService.isAuthenticated() ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Usuario />} />
          <Route 
            path="/home" 
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App