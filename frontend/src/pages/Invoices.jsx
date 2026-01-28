import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { toast } from 'react-toastify'
import ActionIcons from '../components/ActionIcons'
import './Invoices.css'

const Invoices = () => {
  const { selectedCompany, user } = useAuth()
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showPdfPreviewModal, setShowPdfPreviewModal] = useState(false)
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState(null)
  const [pdfPreviewBlob, setPdfPreviewBlob] = useState(null)
  const [previewInvoiceNumber, setPreviewInvoiceNumber] = useState(null)
  const [creating, setCreating] = useState(false)
  const [editing, setEditing] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingInvoiceId, setEditingInvoiceId] = useState(null)
  const [editForm, setEditForm] = useState({
    party: '',
    invoice_type: '',
    notes: '',
    items: [{ item: '', quantity: 1 }],
    amount_paid: 0,
    discount_percent: 0,
  })
  const [selectedInvoice, setSelectedInvoice] = useState(null)
  const [parties, setParties] = useState([])
  const [invoiceTypes, setInvoiceTypes] = useState([])
  const [itemsList, setItemsList] = useState([])
  const [createForm, setCreateForm] = useState({
    party: '',
    invoice_type: '',
    notes: '',
    items: [{ item: '', quantity: 1 }],
    amount_paid: 0,
    discount_percent: 0,
  })

  useEffect(() => {
    if (selectedCompany && user) {
      fetchInvoices()
    }
  }, [selectedCompany, user])

  useEffect(() => {
    if ((showCreateModal || showEditModal) && selectedCompany && user) {
      fetchParties()
      fetchInvoiceTypes()
      fetchItemsForCompany()
    }
  }, [showCreateModal, showEditModal, selectedCompany, user])

  const fetchInvoices = async () => {
    try {
      const response = await api.post('/invoice/list/', {
        company: selectedCompany.id,
      })
      setInvoices(response.data || [])
    } catch (error) {
      console.error('Failed to fetch invoices:', error)
      toast.error('Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  const fetchParties = async () => {
    try {
      const response = await api.post('/parties/', { company: selectedCompany.id })
      setParties(response.data?.data || [])
    } catch (e) {
      toast.error('Failed to load parties')
    }
  }

  const fetchInvoiceTypes = async () => {
    try {
      const response = await api.get('/invoice/types/')
      const typesData = response.data || []
      setInvoiceTypes(typesData)
      if (typesData.length === 0) {
        toast.warning('No invoice types available. Please contact administrator.')
      }
    } catch (e) {
      console.error('Failed to fetch invoice types:', e)
      toast.error('Failed to load invoice types')
    }
  }

  const fetchItemsForCompany = async () => {
    try {
      const response = await api.post('/items/', {
        company: selectedCompany.id,
        customer_id: user.id,
      })
      setItemsList(response.data || [])
    } catch (e) {
      toast.error('Failed to load items')
    }
  }

  const handleCreateInvoice = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !createForm.party || !createForm.invoice_type) {
      toast.error('Party and invoice type are required')
      return
    }
    const lineItems = createForm.items.filter((row) => row.item && Number(row.quantity) > 0)
    if (lineItems.length === 0) {
      toast.error('Add at least one item with quantity')
      return
    }

    setCreating(true)
    try {
      const payload = {
        company: selectedCompany.id,
        party: Number(createForm.party),
        invoice_type: Number(createForm.invoice_type),
        notes: createForm.notes || '',
        items: lineItems.map((row) => ({
          item: Number(row.item),
          quantity: Number(row.quantity),
          discount_percent: 0,
        })),
        amount_paid: Number(createForm.amount_paid) || 0,
        discount_percent: Number(createForm.discount_percent) || 0,
      }
      const response = await api.post('/invoice/create/', payload)
      toast.success(response.data?.msg || 'Invoice created successfully')
      setShowCreateModal(false)
      setCreateForm({
        party: '',
        invoice_type: '',
        notes: '',
        items: [{ item: '', quantity: 1 }],
        amount_paid: 0,
        discount_percent: 0,
      })
      fetchInvoices()
    } catch (error) {
      const msg =
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Failed to create invoice'
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setCreating(false)
    }
  }

  const updateCreateForm = (field, value) => {
    setCreateForm((prev) => ({ ...prev, [field]: value }))
  }

  const updateLineItem = (index, field, value) => {
    setCreateForm((prev) => ({
      ...prev,
      items: prev.items.map((row, i) =>
        i === index ? { ...row, [field]: value } : row
      ),
    }))
  }

  const addLineItem = () => {
    setCreateForm((prev) => ({
      ...prev,
      items: [...prev.items, { item: '', quantity: 1 }],
    }))
  }

  const removeLineItem = (index) => {
    if (createForm.items.length <= 1) return
    setCreateForm((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }))
  }

  const updateEditForm = (field, value) => {
    setEditForm((prev) => ({ ...prev, [field]: value }))
  }

  const updateEditLineItem = (index, field, value) => {
    setEditForm((prev) => ({
      ...prev,
      items: prev.items.map((row, i) =>
        i === index ? { ...row, [field]: value } : row
      ),
    }))
  }

  const addEditLineItem = () => {
    setEditForm((prev) => ({
      ...prev,
      items: [...prev.items, { item: '', quantity: 1 }],
    }))
  }

  const removeEditLineItem = (index) => {
    if (editForm.items.length <= 1) return
    setEditForm((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }))
  }

  const handleEditInvoice = async (invoiceId) => {
    try {
      const response = await api.get(`/invoice/${invoiceId}/`)
      const inv = response.data || null
      if (!inv) return
      const items = (inv.items || []).map((row) => ({
        item: String(row.item_id ?? row.item),
        quantity: Number(row.quantity) || 1,
        discount_percent: Number(row.discount_percent) || 0,
      }))
      setEditForm({
        party: String(inv.party_id ?? inv.party),
        invoice_type: String(inv.invoice_type_id ?? inv.invoice_type),
        notes: inv.notes || '',
        items: items.length > 0 ? items : [{ item: '', quantity: 1 }],
        amount_paid: Number(inv.amount_paid) || 0,
        discount_percent: Number(inv.discount_percent) || 0,
      })
      setEditingInvoiceId(inv.invoice_id ?? inv.id)
      setShowEditModal(true)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load invoice for edit')
    }
  }

  const handleUpdateInvoice = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !editingInvoiceId || !editForm.party || !editForm.invoice_type) {
      toast.error('Party and invoice type are required')
      return
    }
    const lineItems = editForm.items.filter((row) => row.item && Number(row.quantity) > 0)
    if (lineItems.length === 0) {
      toast.error('Add at least one item with quantity')
      return
    }
    setEditing(true)
    try {
      const payload = {
        company: selectedCompany.id,
        party: Number(editForm.party),
        invoice_type: Number(editForm.invoice_type),
        notes: editForm.notes || '',
        items: lineItems.map((row) => ({
          item: Number(row.item),
          quantity: Number(row.quantity),
          discount_percent: Number(row.discount_percent) || 0,
        })),
        amount_paid: Number(editForm.amount_paid) || 0,
        discount_percent: Number(editForm.discount_percent) || 0,
      }
      const response = await api.put(`/invoice/${editingInvoiceId}/update/`, payload)
      toast.success(response.data?.msg || 'Invoice updated successfully')
      setShowEditModal(false)
      setEditingInvoiceId(null)
      setEditForm({
        party: '',
        invoice_type: '',
        notes: '',
        items: [{ item: '', quantity: 1 }],
        amount_paid: 0,
        discount_percent: 0,
      })
      fetchInvoices()
    } catch (error) {
      const msg =
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Failed to update invoice'
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setEditing(false)
    }
  }

  const handleViewInvoice = async (invoiceId) => {
    try {
      const response = await api.get(`/invoice/${invoiceId}/`)
      setSelectedInvoice(response.data || null)
      setShowViewModal(true)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load invoice details')
    }
  }

  const handlePreviewPDF = async (invoiceId, invoiceNumber) => {
    try {
      const response = await api.get(`/invoice/${invoiceId}/pdf/`, {
        responseType: 'blob',
      })
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      setPdfPreviewBlob(blob)
      setPdfPreviewUrl(url)
      setPreviewInvoiceNumber(invoiceNumber || invoiceId)
      setShowPdfPreviewModal(true)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load PDF preview')
    }
  }

  const handleClosePdfPreview = () => {
    if (pdfPreviewUrl) {
      window.URL.revokeObjectURL(pdfPreviewUrl)
    }
    setPdfPreviewUrl(null)
    setPdfPreviewBlob(null)
    setPreviewInvoiceNumber(null)
    setShowPdfPreviewModal(false)
  }

  const handleDownloadFromPreview = () => {
    if (!pdfPreviewBlob || !previewInvoiceNumber) return
    const url = window.URL.createObjectURL(pdfPreviewBlob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Invoice_${previewInvoiceNumber}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    toast.success('Invoice PDF downloaded')
  }

  const handleDownloadPDF = async (invoiceId, invoiceNumber) => {
    try {
      const response = await api.get(`/invoice/${invoiceId}/pdf/`, {
        responseType: 'blob',
      })
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Invoice_${invoiceNumber || invoiceId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Invoice PDF downloaded')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to download PDF')
    }
  }

  if (!selectedCompany) {
    return (
      <div className="page-container">
        <div className="no-company-message">
          <h2>Please select a company first</h2>
          <p>Go to Dashboard and select a company to view invoices.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Invoices</h1>
        <button
          type="button"
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          + Create Invoice
        </button>
      </div>

      <div className="content-card">
        {loading ? (
          <p>Loading invoices...</p>
        ) : invoices.length === 0 ? (
          <div className="empty-state">
            <p>No invoices found. Create your first invoice to get started.</p>
            <button
              type="button"
              className="btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              Create Invoice
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Invoice Number</th>
                  <th>Date</th>
                  <th>Party</th>
                  <th>Type</th>
                  <th>Total</th>
                  <th>Amount Paid</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.invoice_id ?? inv.id}>
                    <td>{inv.invoice_number || 'N/A'}</td>
                    <td>{inv.created_at ? new Date(inv.created_at).toLocaleDateString() : 'N/A'}</td>
                    <td>{inv.party_name ?? inv.party?.name ?? 'N/A'}</td>
                    <td>{inv.invoice_type ?? (inv.invoice_type === 1 ? 'Sale' : 'Purchase')}</td>
                    <td>₹{inv.total ?? '0.00'}</td>
                    <td>₹{inv.amount_paid != null ? Number(inv.amount_paid).toFixed(2) : '0.00'}</td>
                    <td>
                      <span className={`status-badge status-${(inv.payment_status || 'Unpaid').toLowerCase().replace(/\s+/g, '-')}`}>
                        {inv.payment_status || 'Unpaid'}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleViewInvoice(inv.invoice_id ?? inv.id)}
                          title="View"
                        >
                          <ActionIcons.View size={18} title="View" />
                        </button>
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handlePreviewPDF(inv.invoice_id ?? inv.id, inv.invoice_number)}
                          title="Preview PDF"
                        >
                          <ActionIcons.Preview size={18} title="Preview PDF" />
                        </button>
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleDownloadPDF(inv.invoice_id ?? inv.id, inv.invoice_number)}
                          title="Download PDF"
                        >
                          <ActionIcons.Download size={18} title="Download PDF" />
                        </button>
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleEditInvoice(inv.invoice_id ?? inv.id)}
                          title="Edit"
                        >
                          <ActionIcons.Edit size={18} title="Edit" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div
          className="modal-overlay"
          onClick={() => !creating && setShowCreateModal(false)}
        >
          <div
            className="modal-content modal-content--wide"
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ margin: 0 }}>Create Invoice</h2>
            </div>
            <form onSubmit={handleCreateInvoice} className="modal-form">
              <div className="modal-grid">
                <div className="form-group">
                  <label>Party *</label>
                  <select
                    name="party"
                    value={createForm.party}
                    onChange={(e) => updateCreateForm('party', e.target.value)}
                    required
                  >
                    <option value="">Select party</option>
                    {parties.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.party_type_name || (p.party_type === 1 ? 'Customer' : 'Supplier')})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Invoice Type *</label>
                  <select
                    name="invoice_type"
                    value={createForm.invoice_type}
                    onChange={(e) => updateCreateForm('invoice_type', e.target.value)}
                    required
                  >
                    <option value="">Select type</option>
                    {invoiceTypes.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <div className="line-items-section">
                  <div className="line-items-header">
                    <label>Line Items *</label>
                  </div>
                  {createForm.items.map((row, index) => (
                    <div key={index} className="line-item-row">
                      <select
                        value={row.item}
                        onChange={(e) => updateLineItem(index, 'item', e.target.value)}
                        required={index === 0}
                      >
                        <option value="">Select item</option>
                        {itemsList.map((it) => (
                          <option key={it.id} value={it.id}>
                            {it.name} (₹{it.sales_price ?? it.price ?? 0})
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        min="1"
                        value={row.quantity}
                        onChange={(e) => updateLineItem(index, 'quantity', e.target.value)}
                        placeholder="Qty"
                        className="line-item-qty"
                        required={index === 0}
                      />
                      <button
                        type="button"
                        className="btn-remove"
                        onClick={() => removeLineItem(index)}
                        disabled={createForm.items.length <= 1}
                        title="Remove item"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <button type="button" className="btn-add-line" onClick={addLineItem}>
                    + Add Item Line
                  </button>
                </div>
              </div>
              
              <div className="modal-grid">
                <div className="form-group">
                  <label>Discount %</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    value={createForm.discount_percent}
                    onChange={(e) => updateCreateForm('discount_percent', e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="form-group">
                  <label>Amount Paid</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={createForm.amount_paid}
                    onChange={(e) => updateCreateForm('amount_paid', e.target.value)}
                    placeholder="0.00"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea
                  rows="2"
                  value={createForm.notes}
                  onChange={(e) => updateCreateForm('notes', e.target.value)}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => !creating && setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : 'Create Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && editingInvoiceId && (
        <div
          className="modal-overlay"
          onClick={() => !editing && setShowEditModal(false)}
        >
          <div
            className="modal-content modal-content--wide"
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ margin: 0 }}>Edit Invoice</h2>
            </div>
            <form onSubmit={handleUpdateInvoice} className="modal-form">
              <div className="modal-grid">
                <div className="form-group">
                  <label>Party *</label>
                  <select
                    name="party"
                    value={editForm.party}
                    onChange={(e) => updateEditForm('party', e.target.value)}
                    required
                  >
                    <option value="">Select party</option>
                    {parties.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.party_type_name || (p.party_type === 1 ? 'Customer' : 'Supplier')})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Invoice Type *</label>
                  <select
                    name="invoice_type"
                    value={editForm.invoice_type}
                    onChange={(e) => updateEditForm('invoice_type', e.target.value)}
                    required
                  >
                    <option value="">Select type</option>
                    {invoiceTypes.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <div className="line-items-section">
                  <div className="line-items-header">
                    <label>Line Items *</label>
                  </div>
                  {editForm.items.map((row, index) => (
                    <div key={index} className="line-item-row">
                      <select
                        value={row.item}
                        onChange={(e) => updateEditLineItem(index, 'item', e.target.value)}
                        required={index === 0}
                      >
                        <option value="">Select item</option>
                        {itemsList.map((it) => (
                          <option key={it.id} value={it.id}>
                            {it.name} (₹{it.sales_price ?? it.price ?? 0})
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        min="1"
                        value={row.quantity}
                        onChange={(e) => updateEditLineItem(index, 'quantity', e.target.value)}
                        placeholder="Qty"
                        className="line-item-qty"
                        required={index === 0}
                      />
                      <button
                        type="button"
                        className="btn-remove"
                        onClick={() => removeEditLineItem(index)}
                        disabled={editForm.items.length <= 1}
                        title="Remove item"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <button type="button" className="btn-add-line" onClick={addEditLineItem}>
                    + Add Item Line
                  </button>
                </div>
              </div>
              <div className="modal-grid">
                <div className="form-group">
                  <label>Discount %</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    value={editForm.discount_percent}
                    onChange={(e) => updateEditForm('discount_percent', e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="form-group">
                  <label>Amount Paid</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={editForm.amount_paid}
                    onChange={(e) => updateEditForm('amount_paid', e.target.value)}
                    placeholder="0.00"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea
                  rows="2"
                  value={editForm.notes}
                  onChange={(e) => updateEditForm('notes', e.target.value)}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => !editing && setShowEditModal(false)}
                  disabled={editing}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={editing}>
                  {editing ? 'Updating...' : 'Update Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showViewModal && selectedInvoice && (
        <div
          className="modal-overlay"
          onClick={() => setShowViewModal(false)}
        >
          <div
            className="modal-content modal-content--wide"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Invoice Details</h2>
            <div className="view-details">
              <div className="detail-row">
                <span className="detail-label">Invoice Number:</span>
                <span className="detail-value">{selectedInvoice.invoice_number || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Date:</span>
                <span className="detail-value">
                  {selectedInvoice.created_at
                    ? new Date(selectedInvoice.created_at).toLocaleDateString()
                    : 'N/A'}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Party:</span>
                <span className="detail-value">{selectedInvoice.party_name || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Invoice Type:</span>
                <span className="detail-value">{selectedInvoice.invoice_type_name || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Payment Status:</span>
                <span className={`detail-value status-badge status-${(selectedInvoice.payment_status || 'Unpaid').toLowerCase().replace(/\s+/g, '-')}`}>
                  {selectedInvoice.payment_status || 'Unpaid'}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Subtotal:</span>
                <span className="detail-value">₹{selectedInvoice.subtotal?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Tax Amount:</span>
                <span className="detail-value">₹{selectedInvoice.tax_amount?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Discount:</span>
                <span className="detail-value">
                  {selectedInvoice.discount_percent || 0}% (₹{selectedInvoice.discount_amount?.toFixed(2) || '0.00'})
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Total:</span>
                <span className="detail-value" style={{ fontWeight: 600, fontSize: '1rem' }}>
                  ₹{selectedInvoice.total?.toFixed(2) || '0.00'}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Amount Paid:</span>
                <span className="detail-value">₹{selectedInvoice.amount_paid != null ? selectedInvoice.amount_paid.toFixed(2) : '0.00'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Remaining Balance:</span>
                <span className="detail-value">₹{selectedInvoice.remaining_balance != null ? selectedInvoice.remaining_balance.toFixed(2) : '0.00'}</span>
              </div>
              {selectedInvoice.items && selectedInvoice.items.length > 0 && (
                <div className="detail-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.5rem' }}>
                  <span className="detail-label">Items:</span>
                  <div style={{ width: '100%' }}>
                    <table style={{ width: '100%', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ background: '#f8f9fa' }}>
                          <th style={{ padding: '0.5rem', textAlign: 'left' }}>Item</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right' }}>Qty</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right' }}>Rate</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right' }}>Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedInvoice.items.map((item, idx) => (
                          <tr key={idx} style={{ borderBottom: '1px solid #ecf0f1' }}>
                            <td style={{ padding: '0.5rem' }}>{item.item_name}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right' }}>{item.quantity}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right' }}>₹{item.rate?.toFixed(2)}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right' }}>₹{item.amount?.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {selectedInvoice.notes && (
                <div className="detail-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.25rem' }}>
                  <span className="detail-label">Notes:</span>
                  <span className="detail-value">{selectedInvoice.notes}</span>
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button
                type="button"
                className="btn-primary"
                onClick={() => handlePreviewPDF(selectedInvoice.invoice_id ?? selectedInvoice.id, selectedInvoice.invoice_number)}
              >
                Preview PDF
              </button>
              <button
                type="button"
                className="btn-primary"
                onClick={() => handleDownloadPDF(selectedInvoice.invoice_id ?? selectedInvoice.id, selectedInvoice.invoice_number)}
              >
                Download PDF
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowViewModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {showPdfPreviewModal && pdfPreviewUrl && (
        <div
          className="modal-overlay pdf-preview-overlay"
          onClick={handleClosePdfPreview}
        >
          <div
            className="modal-content pdf-preview-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="pdf-preview-header">
              <h2>Invoice PDF Preview</h2>
              <div className="pdf-preview-actions">
                <button
                  type="button"
                  className="btn-primary"
                  onClick={handleDownloadFromPreview}
                >
                  Download PDF
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleClosePdfPreview}
                >
                  Close
                </button>
              </div>
            </div>
            <div className="pdf-preview-frame-wrap">
              <iframe
                title="Invoice PDF Preview"
                src={pdfPreviewUrl}
                className="pdf-preview-iframe"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Invoices
