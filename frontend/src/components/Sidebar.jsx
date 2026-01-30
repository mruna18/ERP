import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Sidebar.css'

const Sidebar = () => {
  const location = useLocation()
  const { selectedCompany } = useAuth()

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/invoices', label: 'Invoices' },
    { path: '/items', label: 'Items' },
    { path: '/parties', label: 'Parties' },
    { path: '/payments', label: 'Payments' },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>ERP System</h2>
        {selectedCompany && (
          <div className="selected-company-info">
            <span className="company-name">{selectedCompany.name}</span>
          </div>
        )}
      </div>
      <nav className="sidebar-nav">
        <ul>
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={isActive ? 'active' : ''}
                >
                  <span className="label">{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
        <ul className="sidebar-nav-footer">
          <li>
            <Link
              to="/settings"
              className={location.pathname === '/settings' ? 'active' : ''}
            >
              <span className="label">Settings</span>
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  )
}

export default Sidebar
