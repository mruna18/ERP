import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { toast } from 'react-toastify'
import './Dashboard.css'

const NOTIFICATIONS_KEY = 'app_notifications'

function isReportSummaryEnabled() {
  try {
    const raw = localStorage.getItem(NOTIFICATIONS_KEY)
    if (raw) {
      const data = JSON.parse(raw)
      return data.reportSummary === true
    }
  } catch (_) {}
  return false
}

const Dashboard = () => {
  const { user, selectedCompany, selectCompany, clearCompany } = useAuth()
  const navigate = useNavigate()
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [statsLoading, setStatsLoading] = useState(false)
  const [statsError, setStatsError] = useState(null)
  const [dashboardStats, setDashboardStats] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [companyToDelete, setCompanyToDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    gst_number: '',
    phone: '',
    address: '',
  })
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchCompanies()
  }, [])

  useEffect(() => {
    if (!selectedCompany?.id) {
      setDashboardStats(null)
      setStatsError(null)
      return
    }
    fetchDashboardStats()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCompany?.id])

  const fetchCompanies = async () => {
    try {
      const response = await api.get('/company/list/')
      setCompanies(response.data || [])
    } catch (error) {
      console.error('Failed to fetch companies:', error)
      toast.error('Failed to load companies')
    } finally {
      setLoading(false)
    }
  }

  const fetchDashboardStats = async () => {
    setStatsLoading(true)
    setStatsError(null)
    try {
      const response = await api.get('/company/dashboard/')
      setDashboardStats(response.data?.stats || null)
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
      setStatsError(error.response?.data?.error || 'Failed to load dashboard reports')
    } finally {
      setStatsLoading(false)
    }
  }

  const handleCompanySelect = (companyId) => {
    selectCompany(companyId)
    toast.success('Company selected')
  }

  const handleCardClick = (path) => {
    if (!selectedCompany) {
      toast.warning('Please select a company first')
      return
    }
    navigate(path)
  }

  const handleCreateCompany = async (e) => {
    e.preventDefault()
    setCreating(true)

    try {
      const response = await api.post('/company/create/', formData)
      toast.success('Company created successfully!')
      setShowCreateModal(false)
      setFormData({ name: '', gst_number: '', phone: '', address: '' })
      fetchCompanies()
      // Auto-select the newly created company
      if (response.data.company_id) {
        selectCompany(response.data.company_id)
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to create company'
      toast.error(errorMessage)
    } finally {
      setCreating(false)
    }
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleDeleteCompany = async () => {
    if (!companyToDelete) return
    setDeleting(true)
    try {
      await api.delete(`/company/${companyToDelete.id}/delete/`, {
        headers: { company: companyToDelete.id },
      })
      toast.success('Company deleted successfully')
      if (selectedCompany?.id === companyToDelete.id) {
        clearCompany()
      }
      setCompanyToDelete(null)
      fetchCompanies()
    } catch (error) {
      const msg = error.response?.data?.error || error.response?.data?.message || 'Failed to delete company'
      toast.error(msg)
    } finally {
      setDeleting(false)
    }
  }

  const formatCurrency = (value) => {
    const num = Number(value || 0)
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
      }).format(num)
    } catch {
      return `₹${Math.round(num).toLocaleString('en-IN')}`
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-content">
        <div className="company-section">
          <header className="company-section-header">
            <div className="company-section-heading">
              <h2 className="company-section-title">Select Company</h2>
              <p className="company-section-desc">Choose a company to work with or create a new one.</p>
            </div>
            <button
              type="button"
              onClick={() => setShowCreateModal(true)}
              className="btn-create-company"
            >
              + Create Company
            </button>
          </header>
          {loading ? (
            <div className="company-loading">
              <span className="company-loading-text">Loading companies...</span>
            </div>
          ) : companies.length === 0 ? (
            <div className="company-empty">
              <p className="company-empty-text">No companies yet. Create your first company to get started.</p>
              <button
                type="button"
                onClick={() => setShowCreateModal(true)}
                className="btn-create-company btn-create-company--primary"
              >
                + Create Company
              </button>
            </div>
          ) : (
            <div className="company-list">
              {companies.map((company) => {
                const isSelected = selectedCompany?.id === company.id
                return (
                  <div
                    key={company.id}
                    className={`company-card-wrap ${isSelected ? 'is-selected' : ''}`}
                  >
                    <button
                      type="button"
                      className="company-card"
                      onClick={() => handleCompanySelect(company.id)}
                    >
                      {isSelected && <span className="company-card-badge">Selected</span>}
                      <span className="company-card-name">{company.name}</span>
                      <dl className="company-card-meta-list">
                        <div className="company-card-meta-row">
                          <dt>GST</dt>
                          <dd>{company.gst_number}</dd>
                        </div>
                        <div className="company-card-meta-row">
                          <dt>Phone</dt>
                          <dd>{company.phone}</dd>
                        </div>
                      </dl>
                    </button>
                    <button
                      type="button"
                      className="company-card-delete"
                      onClick={(e) => {
                        e.stopPropagation()
                        setCompanyToDelete(company)
                      }}
                      title="Delete company"
                      aria-label="Delete company"
                    >
                      <span className="company-card-delete-icon" aria-hidden>×</span>
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {selectedCompany && (
          <div className="reports-section">
            <div className="reports-header">
              <div className="reports-title-wrap">
                <h2 className="reports-title">Reports</h2>
                <p className="reports-desc">Live snapshot for the selected company.</p>
              </div>
              <div className="reports-actions">
                <button type="button" className="btn-secondary" onClick={fetchDashboardStats} disabled={statsLoading}>
                  Refresh
                </button>
              </div>
            </div>

            {statsLoading ? (
              <div className="reports-loading">Loading reports...</div>
            ) : statsError ? (
              <div className="reports-error">
                <div className="reports-error-text">{statsError}</div>
                <button type="button" className="btn-secondary" onClick={fetchDashboardStats}>
                  Try again
                </button>
              </div>
            ) : dashboardStats ? (
              <>
                {isReportSummaryEnabled() && (
                <div className="report-summary-card">
                  <div className="report-summary-header">
                    <h3 className="report-summary-title">Report summary</h3>
                    <p className="report-summary-desc">Key figures for the selected company.</p>
                  </div>
                  <div className="report-summary-body">
                    <div className="report-summary-block">
                      <h4 className="report-summary-block-title">Activity</h4>
                      <div className="report-summary-rows">
                        <div className="report-summary-row">
                          <span className="report-summary-label">Total Sales</span>
                          <span className="report-summary-value">{dashboardStats.total_sales ?? 0}</span>
                        </div>
                        <div className="report-summary-row">
                          <span className="report-summary-label">Total Purchases</span>
                          <span className="report-summary-value">{dashboardStats.total_purchases ?? 0}</span>
                        </div>
                        <div className="report-summary-row">
                          <span className="report-summary-label">Today Sales</span>
                          <span className="report-summary-value">{dashboardStats.today_sales ?? 0}</span>
                        </div>
                      </div>
                    </div>
                    <div className="report-summary-block">
                      <h4 className="report-summary-block-title">Cash flow</h4>
                      <div className="report-summary-rows">
                        <div className="report-summary-row">
                          <span className="report-summary-label">Total Received</span>
                          <span className="report-summary-value report-summary-value--in">{formatCurrency(dashboardStats.total_received)}</span>
                        </div>
                        <div className="report-summary-row">
                          <span className="report-summary-label">Total Paid</span>
                          <span className="report-summary-value report-summary-value--out">{formatCurrency(dashboardStats.total_paid)}</span>
                        </div>
                        <div className="report-summary-row">
                          <span className="report-summary-label">Receivables</span>
                          <span className="report-summary-value report-summary-value--amount">{formatCurrency(dashboardStats.receivables)}</span>
                        </div>
                        <div className="report-summary-row">
                          <span className="report-summary-label">Payables</span>
                          <span className="report-summary-value report-summary-value--amount">{formatCurrency(dashboardStats.payables)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="report-summary-block">
                      <h4 className="report-summary-block-title">Balances</h4>
                      <div className="report-summary-rows">
                        <div className="report-summary-row">
                          <span className="report-summary-label">Cash</span>
                          <span className="report-summary-value report-summary-value--balance">{formatCurrency(dashboardStats.cash_balance)}</span>
                        </div>
                        <div className="report-summary-row">
                          <span className="report-summary-label">Bank</span>
                          <span className="report-summary-value report-summary-value--balance">{formatCurrency(dashboardStats.bank_balance)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                )}

                <div className="kpi-grid">
                  <button type="button" className="kpi-card" onClick={() => navigate('/invoices')}>
                    <div className="kpi-label">Total Sales (count)</div>
                    <div className="kpi-value">{dashboardStats.total_sales ?? 0}</div>
                  </button>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Today Sales (count)</div>
                    <div className="kpi-value">{dashboardStats.today_sales ?? 0}</div>
                  </div>
                  <button type="button" className="kpi-card" onClick={() => navigate('/invoices')}>
                    <div className="kpi-label">Total Purchases (count)</div>
                    <div className="kpi-value">{dashboardStats.total_purchases ?? 0}</div>
                  </button>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Total Received</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.total_received)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Total Paid</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.total_paid)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Receivables</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.receivables)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Payables</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.payables)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Advance From Customers</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.advance_from_customers)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Advance To Suppliers</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.advance_to_suppliers)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Cash Balance</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.cash_balance)}</div>
                  </div>
                  <div className="kpi-card kpi-card--static">
                    <div className="kpi-label">Bank Balance</div>
                    <div className="kpi-value">{formatCurrency(dashboardStats.bank_balance)}</div>
                  </div>
                </div>

                {dashboardStats.chart_data && (
                  <div className="charts-section">
                    <h3 className="charts-section-title">Charts</h3>
                    <div className="charts-grid">
                      <div className="chart-card">
                        <h4 className="chart-title">Sales vs Purchases (Count)</h4>
                        <div className="chart-wrap chart-bar-wrap">
                          {(dashboardStats.chart_data.sales_vs_purchases || []).map((item) => {
                            const maxCount = Math.max(1, ...(dashboardStats.chart_data.sales_vs_purchases || []).map((d) => d.count))
                            const pct = (item.count / maxCount) * 100
                            return (
                              <div key={item.name} className="chart-bar-row">
                                <span className="chart-bar-label">{item.name}</span>
                                <div className="chart-bar-track">
                                  <div className="chart-bar-fill" style={{ width: `${pct}%`, backgroundColor: item.fill || '#3498db' }} title={`${item.count}`} />
                                </div>
                                <span className="chart-bar-value">{item.count}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                      <div className="chart-card">
                        <h4 className="chart-title">Cash Flow (Amount)</h4>
                        <div className="chart-wrap chart-bar-wrap">
                          {(dashboardStats.chart_data.cash_flow || []).map((item) => {
                            const maxVal = Math.max(1, ...(dashboardStats.chart_data.cash_flow || []).map((d) => Number(d.value)))
                            const pct = (Number(item.value) / maxVal) * 100
                            return (
                              <div key={item.name} className="chart-bar-row">
                                <span className="chart-bar-label">{item.name}</span>
                                <div className="chart-bar-track">
                                  <div className="chart-bar-fill" style={{ width: `${pct}%`, backgroundColor: item.fill || '#3498db' }} title={formatCurrency(item.value)} />
                                </div>
                                <span className="chart-bar-value">{formatCurrency(item.value)}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                      <div className="chart-card chart-card--full">
                        <h4 className="chart-title">Balance Breakdown</h4>
                        <div className="chart-wrap chart-pie-wrap">
                          {(() => {
                            const breakdown = (dashboardStats.chart_data.balance_breakdown || []).filter((d) => Number(d.value) > 0)
                            const total = breakdown.reduce((s, d) => s + Number(d.value), 0) || 1
                            const conicParts = breakdown.map((d, i) => {
                              const pct = (Number(d.value) / total) * 100
                              const start = breakdown.slice(0, i).reduce((s, x) => s + (Number(x.value) / total) * 100, 0)
                              return `${d.fill || '#95a5a6'} ${start}% ${start + pct}%`
                            }).join(', ')
                            return (
                              <>
                                <div className="chart-pie" style={{ background: `conic-gradient(${conicParts})` }} aria-hidden />
                                <ul className="chart-legend">
                                  {breakdown.map((d) => (
                                    <li key={d.name}>
                                      <span className="chart-legend-dot" style={{ backgroundColor: d.fill || '#95a5a6' }} />
                                      <span>{d.name}: {formatCurrency(d.value)}</span>
                                    </li>
                                  ))}
                                </ul>
                              </>
                            )
                          })()}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="reports-grid">
                  <div className="report-card">
                    <div className="report-card-header">
                      <h3>Advances From Customers</h3>
                    </div>
                    <div className="report-card-body">
                      {Array.isArray(dashboardStats.advance_customers) && dashboardStats.advance_customers.length > 0 ? (
                        <div className="table-wrap">
                          <table className="report-table">
                            <thead>
                              <tr>
                                <th>Party</th>
                                <th className="num">Advance</th>
                              </tr>
                            </thead>
                            <tbody>
                              {dashboardStats.advance_customers.slice(0, 8).map((row) => (
                                <tr key={`${row.party_id}-${row.party__name}`}>
                                  <td>{row.party__name}</td>
                                  <td className="num">{formatCurrency(row.total_advance)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div className="report-empty">No customer advances found.</div>
                      )}
                    </div>
                  </div>

                  <div className="report-card">
                    <div className="report-card-header">
                      <h3>Payables by Party</h3>
                    </div>
                    <div className="report-card-body">
                      {Array.isArray(dashboardStats.payable_parties) && dashboardStats.payable_parties.length > 0 ? (
                        <div className="table-wrap">
                          <table className="report-table">
                            <thead>
                              <tr>
                                <th>Party</th>
                                <th className="num">Due</th>
                              </tr>
                            </thead>
                            <tbody>
                              {dashboardStats.payable_parties.slice(0, 8).map((row) => (
                                <tr key={`${row.party_id}-${row.party__name}`}>
                                  <td>{row.party__name}</td>
                                  <td className="num">{formatCurrency(row.total_due)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div className="report-empty">No payables found.</div>
                      )}
                    </div>
                  </div>

                  <div className="report-card">
                    <div className="report-card-header">
                      <h3>Payable Invoices</h3>
                    </div>
                    <div className="report-card-body">
                      {Array.isArray(dashboardStats.payable_invoices) && dashboardStats.payable_invoices.length > 0 ? (
                        <div className="table-wrap">
                          <table className="report-table">
                            <thead>
                              <tr>
                                <th>Invoice</th>
                                <th>Party</th>
                                <th className="num">Due</th>
                              </tr>
                            </thead>
                            <tbody>
                              {dashboardStats.payable_invoices.slice(0, 8).map((row) => (
                                <tr key={row.id}>
                                  <td>{row.invoice_number || row.id}</td>
                                  <td>{row.party__name}</td>
                                  <td className="num">{formatCurrency(row.due_amount)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div className="report-empty">No payable invoices found.</div>
                      )}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="reports-empty">No report data available.</div>
            )}
          </div>
        )}

        {/* Create Company Modal */}
        {showCreateModal && (
          <div 
            className="modal-overlay"
            onClick={() => setShowCreateModal(false)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              zIndex: 1000,
            }}
          >
            <div 
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
              style={{
                backgroundColor: 'white',
                padding: '2rem',
                borderRadius: '10px',
                width: '90%',
                maxWidth: '500px',
                maxHeight: '90vh',
                overflow: 'auto',
              }}
            >
              <h2 style={{ marginTop: 0 }}>Create New Company</h2>
              <form onSubmit={handleCreateCompany}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    Company Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px',
                      fontSize: '1rem',
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    GST Number *
                  </label>
                  <input
                    type="text"
                    name="gst_number"
                    value={formData.gst_number}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px',
                      fontSize: '1rem',
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    Phone (10 digits) *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    required
                    pattern="[0-9]{10}"
                    maxLength="10"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px',
                      fontSize: '1rem',
                    }}
                  />
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    Address
                  </label>
                  <textarea
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    rows="3"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px',
                      fontSize: '1rem',
                      fontFamily: 'inherit',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    style={{
                      padding: '0.75rem 1.5rem',
                      backgroundColor: '#95a5a6',
                      color: '#2c3e50',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: 500,
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating}
                    style={{
                      padding: '0.75rem 1.5rem',
                      backgroundColor: '#34495e',
                      color: '#ecf0f1',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: creating ? 'not-allowed' : 'pointer',
                      fontSize: '1rem',
                      opacity: creating ? 0.6 : 1,
                      fontWeight: 500,
                    }}
                  >
                    {creating ? 'Creating...' : 'Create Company'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Delete Company Confirmation Modal */}
        {companyToDelete && (
          <div
            className="modal-overlay"
            onClick={() => !deleting && setCompanyToDelete(null)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              zIndex: 1000,
            }}
          >
            <div
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
              style={{
                backgroundColor: 'white',
                padding: '2rem',
                borderRadius: '10px',
                width: '90%',
                maxWidth: '420px',
              }}
            >
              <h2 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Delete company?</h2>
              <p style={{ color: '#7f8c8d', marginBottom: '1.5rem' }}>
                <strong>{companyToDelete.name}</strong> will be deactivated. You will no longer be able to use it or see its data. This cannot be undone.
              </p>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => !deleting && setCompanyToDelete(null)}
                  disabled={deleting}
                  className="btn-secondary"
                  style={{ padding: '0.75rem 1.5rem' }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDeleteCompany}
                  disabled={deleting}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#c0392b',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: deleting ? 'not-allowed' : 'pointer',
                    fontSize: '1rem',
                    fontWeight: 500,
                    opacity: deleting ? 0.7 : 1,
                  }}
                >
                  {deleting ? 'Deleting...' : 'Delete company'}
                </button>
              </div>
            </div>
          </div>
        )}

        {selectedCompany && (
          <div className="features-section">
            <h2>Quick Actions</h2>
            <div className="feature-grid">
              <div 
                className="feature-card" 
                onClick={() => handleCardClick('/invoices')}
              >
                <h3>Invoices</h3>
                <p>Manage sales and purchase invoices</p>
              </div>
              <div 
                className="feature-card" 
                onClick={() => handleCardClick('/items')}
              >
                <h3>Items</h3>
                <p>Manage inventory and products</p>
              </div>
              <div 
                className="feature-card" 
                onClick={() => handleCardClick('/parties')}
              >
                <h3>Parties</h3>
                <p>Manage customers and suppliers</p>
              </div>
              <div 
                className="feature-card" 
                onClick={() => handleCardClick('/payments')}
              >
                <h3>Payments</h3>
                <p>Track payments and transactions</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
