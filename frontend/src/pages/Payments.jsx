import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { toast } from 'react-toastify'
import './Payments.css'

const Payments = () => {
  const { selectedCompany } = useAuth()
  const [paymentIns, setPaymentIns] = useState([])
  const [paymentOuts, setPaymentOuts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPaymentInModal, setShowPaymentInModal] = useState(false)
  const [showPaymentOutModal, setShowPaymentOutModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [invoices, setInvoices] = useState([])
  const [bankAccounts, setBankAccounts] = useState([])
  const [paymentTypes, setPaymentTypes] = useState([])
  const [activeTab, setActiveTab] = useState('all') // 'all' | 'in' | 'out'
  const [paymentInForm, setPaymentInForm] = useState({
    invoice: '',
    amount: '',
    bank_account: '',
    note: '',
  })
  const [paymentOutForm, setPaymentOutForm] = useState({
    invoice: '',
    amount: '',
    payment_type: '',
    bank_account: '',
    note: '',
  })

  useEffect(() => {
    if (selectedCompany) {
      fetchPayments()
    }
  }, [selectedCompany])

  useEffect(() => {
    if ((showPaymentInModal || showPaymentOutModal) && selectedCompany) {
      fetchInvoices()
      fetchBankAccounts()
      if (showPaymentOutModal) fetchPaymentTypes()
    }
  }, [showPaymentInModal, showPaymentOutModal, selectedCompany])

  const fetchPayments = async () => {
    if (!selectedCompany) return
    setLoading(true)
    try {
      const response = await api.post('/payments/list/', { company: selectedCompany.id })
      setPaymentIns(response.data?.payment_ins || [])
      setPaymentOuts(response.data?.payment_outs || [])
    } catch (error) {
      console.error('Failed to fetch payments:', error)
      toast.error('Failed to load payments')
    } finally {
      setLoading(false)
    }
  }

  const fetchInvoices = async () => {
    try {
      const response = await api.post('/invoice/list/', { company: selectedCompany.id })
      setInvoices(response.data || [])
    } catch (e) {
      toast.error('Failed to load invoices')
    }
  }

  const fetchBankAccounts = async () => {
    try {
      const response = await api.post('/invoice/bank-accounts/', { company: selectedCompany.id })
      setBankAccounts(response.data?.data || [])
    } catch (e) {
      setBankAccounts([])
    }
  }

  const fetchPaymentTypes = async () => {
    try {
      const response = await api.get('/invoice/payment-types/')
      setPaymentTypes(response.data || [])
    } catch (e) {
      toast.error('Failed to load payment types')
    }
  }

  const unpaidInvoices = invoices.filter((inv) => (inv.remaining_balance ?? 0) > 0)

  const handlePaymentInSubmit = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !paymentInForm.invoice || !paymentInForm.amount || Number(paymentInForm.amount) <= 0) {
      toast.error('Select an invoice and enter a valid amount')
      return
    }
    setSubmitting(true)
    try {
      const payload = {
        company: selectedCompany.id,
        invoice: paymentInForm.invoice,
        amount: Number(paymentInForm.amount),
        note: paymentInForm.note || '',
      }
      if (paymentInForm.bank_account) payload.bank_account = paymentInForm.bank_account
      const response = await api.post('/payments/payment-in/', payload)
      if (response.data?.status === 200) {
        toast.success(response.data.message || 'Payment In recorded')
        setShowPaymentInModal(false)
        setPaymentInForm({ invoice: '', amount: '', bank_account: '', note: '' })
        fetchPayments()
      } else {
        toast.error(response.data?.message || 'Payment failed')
      }
    } catch (error) {
      const msg = error.response?.data?.message || error.message || 'Payment In failed'
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handlePaymentOutSubmit = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !paymentOutForm.amount || Number(paymentOutForm.amount) <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    const paymentType = paymentTypes.find((t) => t.id === Number(paymentOutForm.payment_type))
    const isBank = paymentType && paymentType.name?.toLowerCase() !== 'cash'
    if (isBank && !paymentOutForm.bank_account) {
      toast.error('Select a bank account for bank payment')
      return
    }
    setSubmitting(true)
    try {
      const payload = {
        company: selectedCompany.id,
        amount: Number(paymentOutForm.amount),
        payment_type: paymentOutForm.payment_type,
        note: paymentOutForm.note || '',
      }
      if (paymentOutForm.invoice) payload.invoice = paymentOutForm.invoice
      if (isBank && paymentOutForm.bank_account) payload.bank_account = paymentOutForm.bank_account
      const response = await api.post('/payments/payment-out/', payload)
      if (response.data?.status === 200) {
        toast.success(response.data.message || 'Payment Out recorded')
        setShowPaymentOutModal(false)
        setPaymentOutForm({ invoice: '', amount: '', payment_type: '', bank_account: '', note: '' })
        fetchPayments()
      } else {
        toast.error(response.data?.message || 'Payment failed')
      }
    } catch (error) {
      const msg = error.response?.data?.message || error.message || 'Payment Out failed'
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const totalIn = paymentIns.reduce((sum, p) => sum + (p.amount || 0), 0)
  const totalOut = paymentOuts.reduce((sum, p) => sum + (p.amount || 0), 0)

  const combinedList = [
    ...paymentIns.map((p) => ({ ...p, type: 'in' })),
    ...paymentOuts.map((p) => ({ ...p, type: 'out' })),
  ].sort((a, b) => new Date(b.payment_date || 0) - new Date(a.payment_date || 0))

  const displayList = activeTab === 'in' ? paymentIns : activeTab === 'out' ? paymentOuts : combinedList

  if (!selectedCompany) {
    return (
      <div className="page-container payments-page">
        <div className="no-company-message">
          <h2>Please select a company first</h2>
          <p>Go to Dashboard and select a company to view payments.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container payments-page">
      <div className="page-header payments-header">
        <h1>Payments</h1>
        <div className="payments-actions">
          <button type="button" className="btn-primary btn-payment-in" onClick={() => setShowPaymentInModal(true)}>
            + Payment In
          </button>
          <button type="button" className="btn-primary btn-payment-out" onClick={() => setShowPaymentOutModal(true)}>
            + Payment Out
          </button>
        </div>
      </div>

      <div className="payments-summary">
        <div className="summary-card summary-in">
          <span className="summary-label">Total Received</span>
          <span className="summary-value">₹{totalIn.toFixed(2)}</span>
        </div>
        <div className="summary-card summary-out">
          <span className="summary-label">Total Paid Out</span>
          <span className="summary-value">₹{totalOut.toFixed(2)}</span>
        </div>
      </div>

      <div className="content-card payments-content">
        <div className="payments-tabs">
          <button
            type="button"
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All
          </button>
          <button
            type="button"
            className={`tab-btn ${activeTab === 'in' ? 'active' : ''}`}
            onClick={() => setActiveTab('in')}
          >
            Payment In
          </button>
          <button
            type="button"
            className={`tab-btn ${activeTab === 'out' ? 'active' : ''}`}
            onClick={() => setActiveTab('out')}
          >
            Payment Out
          </button>
        </div>

        {loading ? (
          <p className="loading-text">Loading payments...</p>
        ) : displayList.length === 0 ? (
          <div className="empty-state">
            <p>No payments found. Record a Payment In or Payment Out to get started.</p>
            <div className="empty-state-actions">
              <button type="button" className="btn-primary" onClick={() => setShowPaymentInModal(true)}>
                Payment In
              </button>
              <button type="button" className="btn-primary" onClick={() => setShowPaymentOutModal(true)}>
                Payment Out
              </button>
            </div>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table payments-table">
              <thead>
                <tr>
                  <th>Date</th>
                  {activeTab === 'all' && <th>Type</th>}
                  <th>Party / Ref</th>
                  <th>Invoice</th>
                  <th>Amount</th>
                  <th>Method</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody>
                {displayList.map((row) => (
                  <tr key={row.type === 'in' ? `in-${row.id}` : `out-${row.id}`}>
                    <td>{row.payment_date ? new Date(row.payment_date).toLocaleDateString() : 'N/A'}</td>
                    {activeTab === 'all' && (
                      <td>
                        <span className={`payment-type-badge ${row.type === 'in' ? 'type-in' : 'type-out'}`}>
                          {row.type === 'in' ? 'In' : 'Out'}
                        </span>
                      </td>
                    )}
                    <td>{row.party_name || '—'}</td>
                    <td>{row.invoice_number || '—'}</td>
                    <td className="amount-cell">₹{Number(row.amount || 0).toFixed(2)}</td>
                    <td>{row.bank_name || '—'}</td>
                    <td className="note-cell">{row.note || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Payment In Modal */}
      {showPaymentInModal && (
        <div className="modal-overlay" onClick={() => !submitting && setShowPaymentInModal(false)}>
          <div className="modal-content payment-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Payment In</h2>
            <p className="modal-hint">Record money received (e.g. against an invoice).</p>
            <form onSubmit={handlePaymentInSubmit}>
              <div className="form-group">
                <label>Invoice *</label>
                <select
                  value={paymentInForm.invoice}
                  onChange={(e) => setPaymentInForm((f) => ({ ...f, invoice: e.target.value }))}
                  required
                >
                  <option value="">Select invoice</option>
                  {unpaidInvoices.map((inv) => (
                    <option key={inv.invoice_id} value={inv.invoice_id}>
                      {inv.invoice_number} — {inv.party_name} (₹{inv.remaining_balance?.toFixed(2) ?? 0} due)
                    </option>
                  ))}
                  {unpaidInvoices.length === 0 && <option value="" disabled>No unpaid invoices</option>}
                </select>
              </div>
              <div className="form-group">
                <label>Amount (₹) *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={paymentInForm.amount}
                  onChange={(e) => setPaymentInForm((f) => ({ ...f, amount: e.target.value }))}
                  placeholder="0.00"
                  required
                />
              </div>
              <div className="form-group">
                <label>Bank account (optional)</label>
                <select
                  value={paymentInForm.bank_account}
                  onChange={(e) => setPaymentInForm((f) => ({ ...f, bank_account: e.target.value }))}
                >
                  <option value="">— None —</option>
                  {bankAccounts.map((b) => (
                    <option key={b.id} value={b.id}>{b.bank_name} — {b.account_no}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Note</label>
                <input
                  type="text"
                  value={paymentInForm.note}
                  onChange={(e) => setPaymentInForm((f) => ({ ...f, note: e.target.value }))}
                  placeholder="Optional note"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => !submitting && setShowPaymentInModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? 'Saving…' : 'Record Payment In'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Payment Out Modal */}
      {showPaymentOutModal && (
        <div className="modal-overlay" onClick={() => !submitting && setShowPaymentOutModal(false)}>
          <div className="modal-content payment-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Payment Out</h2>
            <p className="modal-hint">Record money paid out (cash or bank).</p>
            <form onSubmit={handlePaymentOutSubmit}>
              <div className="form-group">
                <label>Payment type *</label>
                <select
                  value={paymentOutForm.payment_type}
                  onChange={(e) => setPaymentOutForm((f) => ({ ...f, payment_type: e.target.value, bank_account: '' }))}
                  required
                >
                  <option value="">Select type</option>
                  {paymentTypes.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
              {paymentOutForm.payment_type && paymentTypes.find((t) => t.id === Number(paymentOutForm.payment_type))?.name?.toLowerCase() !== 'cash' && (
                <div className="form-group">
                  <label>Bank account *</label>
                  <select
                    value={paymentOutForm.bank_account}
                    onChange={(e) => setPaymentOutForm((f) => ({ ...f, bank_account: e.target.value }))}
                    required
                  >
                    <option value="">Select account</option>
                    {bankAccounts.map((b) => (
                      <option key={b.id} value={b.id}>{b.bank_name} — {b.account_no}</option>
                    ))}
                  </select>
                </div>
              )}
              <div className="form-group">
                <label>Invoice (optional)</label>
                <select
                  value={paymentOutForm.invoice}
                  onChange={(e) => setPaymentOutForm((f) => ({ ...f, invoice: e.target.value }))}
                >
                  <option value="">— None —</option>
                  {invoices.map((inv) => (
                    <option key={inv.invoice_id} value={inv.invoice_id}>
                      {inv.invoice_number} — {inv.party_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Amount (₹) *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={paymentOutForm.amount}
                  onChange={(e) => setPaymentOutForm((f) => ({ ...f, amount: e.target.value }))}
                  placeholder="0.00"
                  required
                />
              </div>
              <div className="form-group">
                <label>Note</label>
                <input
                  type="text"
                  value={paymentOutForm.note}
                  onChange={(e) => setPaymentOutForm((f) => ({ ...f, note: e.target.value }))}
                  placeholder="Optional note"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => !submitting && setShowPaymentOutModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? 'Saving…' : 'Record Payment Out'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Payments
