import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import './Layout.css'

const Layout = ({ children }) => {
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <Sidebar />
      <div className="layout-content">
        <header className="layout-header">
          <div className="header-content">
            {user && <span className="user-info">Welcome, {user.username_display || user.email}</span>}
            <button onClick={handleLogout} className="btn-logout">
              Logout
            </button>
          </div>
        </header>
        <main className="layout-main">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
