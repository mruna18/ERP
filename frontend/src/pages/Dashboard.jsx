import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { toast } from 'react-toastify'
import './Dashboard.css'

const Dashboard = () => {
  const { user, logout, selectedCompany, selectCompany } = useAuth()
  const navigate = useNavigate()
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    try {
      const response = await api.post('/company/list/')
      setCompanies(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch companies:', error)
      toast.error('Failed to load companies')
    } finally {
      setLoading(false)
    }
  }

  const handleCompanySelect = (companyId) => {
    selectCompany(companyId)
    toast.success('Company selected')
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>ERP Dashboard</h1>
        <div className="header-actions">
          {user && <span className="user-info">Welcome, {user.username}</span>}
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="company-section">
          <h2>Select Company</h2>
          {loading ? (
            <p>Loading companies...</p>
          ) : companies.length === 0 ? (
            <div className="empty-state">
              <p>No companies found. Create a company to get started.</p>
            </div>
          ) : (
            <div className="company-list">
              {companies.map((company) => (
                <div
                  key={company.id}
                  className={`company-card ${
                    selectedCompany?.id === company.id ? 'selected' : ''
                  }`}
                  onClick={() => handleCompanySelect(company.id)}
                >
                  <h3>{company.name}</h3>
                  <p>GST: {company.gst_number}</p>
                  <p>Phone: {company.phone}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedCompany && (
          <div className="features-section">
            <h2>Quick Actions</h2>
            <div className="feature-grid">
              <div className="feature-card">
                <h3>Invoices</h3>
                <p>Manage sales and purchase invoices</p>
              </div>
              <div className="feature-card">
                <h3>Items</h3>
                <p>Manage inventory and products</p>
              </div>
              <div className="feature-card">
                <h3>Parties</h3>
                <p>Manage customers and suppliers</p>
              </div>
              <div className="feature-card">
                <h3>Payments</h3>
                <p>Track payments and transactions</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard
