import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from "./components/login/login"
import Usuario from "./components/usuario/usuario"
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Usuario />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App