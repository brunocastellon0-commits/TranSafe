import "./home.css";
import useHome from "./home";

export default function Home() {
  const {
    showBalance,
    setShowBalance,
    balance,
    movements,
    handleLogout
  } = useHome();

  return (
    <div className="home-container">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div>
            <h2 className="welcome">Hola, Usuario</h2>
            <p className="account-info">Cuenta de Ahorros</p>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            <svg className="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>

      {/* Balance Card */}
      <div className="balance-card">
        <div className="balance-header">
          <span className="balance-label">Saldo disponible</span>
          <button onClick={() => setShowBalance(!showBalance)} className="eye-toggle">
            {showBalance ? (
              <svg className="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            ) : (
              <svg className="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            )}
          </button>
        </div>
        <h1 className="balance-amount">
          {showBalance ? `Bs ${balance.toFixed(2)}` : "Bs •••••"}
        </h1>
      </div>

      {/* Quick Actions */}
      <div className="actions-grid">
        <button className="action-btn">
          <div className="action-icon bg-blue">
            <svg className="icon-md" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
            </svg>
          </div>
          <span className="action-label">Pago QR</span>
        </button>

        <button className="action-btn">
          <div className="action-icon bg-green">
            <svg className="icon-md" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
            </svg>
          </div>
          <span className="action-label">Cobro QR</span>
        </button>

        <button className="action-btn">
          <div className="action-icon bg-purple">
            <svg className="icon-md" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </div>
          <span className="action-label">Transferir</span>
        </button>

        <button className="action-btn">
          <div className="action-icon bg-orange">
            <svg className="icon-md" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="action-label">Servicios</span>
        </button>
      </div>

      {/* Movements Section */}
      <div className="movements-section">
        <h3 className="section-title">Movimientos recientes</h3>
        <div className="movements-list">
          {movements.map((mov) => (
            <div key={mov.id} className="movement-item">
              <div className="movement-icon-wrapper">
                <div className={`movement-icon ${mov.type === 'in' ? 'icon-in' : 'icon-out'}`}>
                  {mov.type === 'in' ? (
                    <svg className="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  ) : (
                    <svg className="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                  )}
                </div>
              </div>
              <div className="movement-info">
                <p className="movement-desc">{mov.desc}</p>
                <p className="movement-name">{mov.name}</p>
                <p className="movement-date">{mov.date}</p>
              </div>
              <div className="movement-amount">
                <span className={mov.type === 'in' ? 'amount-in' : 'amount-out'}>
                  {mov.type === 'in' ? '+' : ''}Bs {Math.abs(mov.amount).toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}