import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { toast } from 'react-toastify'
import ActionIcons from '../components/ActionIcons'
import './Items.css'

const Items = () => {
  const { selectedCompany, user } = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [units, setUnits] = useState([])
  const [unitsLoading, setUnitsLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    unit: '',
    quantity: 0,
    price: 0,
    sales_price: 0,
    tax_applied: false,
    tax_percent: 0,
  })

  useEffect(() => {
    if (selectedCompany && user) {
      fetchItems()
    }
  }, [selectedCompany, user])

  useEffect(() => {
    fetchUnits()
  }, [])

  const fetchItems = async () => {
    try {
      const response = await api.post('/items/', {
        company: selectedCompany.id,
        customer_id: user.id,
      })
      setItems(response.data || [])
    } catch (error) {
      console.error('Failed to fetch items:', error)
      toast.error('Failed to load items')
    } finally {
      setLoading(false)
    }
  }

  const fetchUnits = async () => {
    setUnitsLoading(true)
    try {
      const response = await api.get('/items/units/')
      const unitsData = response.data || []
      setUnits(unitsData)
      if (unitsData.length === 0) {
        toast.warning('No units available. Please contact administrator.')
      }
    } catch (error) {
      console.error('Failed to fetch units:', error)
      toast.error('Failed to load units')
    } finally {
      setUnitsLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleViewItem = async (itemId) => {
    try {
      const response = await api.get(`/items/${selectedCompany.id}/${itemId}/`)
      setSelectedItem(response.data || null)
      setShowViewModal(true)
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load item details')
    }
  }

  const handleEditItem = async (itemId) => {
    try {
      const response = await api.get(`/items/${selectedCompany.id}/${itemId}/`)
      const item = response.data || null
      if (item) {
        setSelectedItem(item)
        setFormData({
          name: item.name || '',
          code: item.code || '',
          description: item.description || '',
          unit: item.unit || '',
          quantity: item.quantity || 0,
          price: item.price || 0,
          sales_price: item.sales_price || 0,
          tax_applied: item.tax_applied || false,
          tax_percent: item.tax_percent || 0,
        })
        setShowEditModal(true)
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load item details')
    }
  }

  const handleUpdateItem = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !selectedItem) return
    setUpdating(true)

    try {
      const payload = {
        ...formData,
        company: selectedCompany.id,
        unit: Number(formData.unit),
      }
      const response = await api.put(`/items/${selectedCompany.id}/${selectedItem.id}/update/`, payload)
      if (response.data?.error) {
        toast.error(response.data.error)
        return
      }

      toast.success(response.data?.message || 'Item updated successfully')
      setShowEditModal(false)
      setSelectedItem(null)
      setFormData({
        name: '',
        code: '',
        description: '',
        unit: '',
        quantity: 0,
        price: 0,
        sales_price: 0,
        tax_applied: false,
        tax_percent: 0,
      })
      setLoading(true)
      fetchItems()
    } catch (error) {
      const msg =
        error.response?.data?.error ||
        error.response?.data?.detail ||
        'Failed to update item'
      toast.error(msg)
    } finally {
      setUpdating(false)
    }
  }

  const handleCreateItem = async (e) => {
    e.preventDefault()
    if (!selectedCompany) return
    setCreating(true)

    try {
      const payload = {
        ...formData,
        company: selectedCompany.id,
        // Ensure unit is sent as an ID (integer)
        unit: formData.unit ? Number(formData.unit) : null,
      }
      const response = await api.post('/items/create/', payload)
      toast.success(response.data?.message || 'Item created successfully')
      setShowCreateModal(false)
      setFormData({
        name: '',
        code: '',
        description: '',
        unit: '',
        quantity: 0,
        price: 0,
        sales_price: 0,
        tax_applied: false,
        tax_percent: 0,
      })
      setLoading(true)
      fetchItems()
    } catch (error) {
      const msg =
        error.response?.data?.error ||
        error.response?.data?.detail ||
        'Failed to create item'
      toast.error(msg)
    } finally {
      setCreating(false)
    }
  }

  if (!selectedCompany) {
    return (
      <div className="page-container">
        <div className="no-company-message">
          <h2>Please select a company first</h2>
          <p>Go to Dashboard and select a company to view items.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Items</h1>
        <button
          className="btn-primary"
          type="button"
          onClick={() => setShowCreateModal(true)}
        >
          + Create Item
        </button>
      </div>

      <div className="content-card">
        {loading ? (
          <p>Loading items...</p>
        ) : items.length === 0 ? (
          <div className="empty-state">
            <p>No items found. Create your first item to get started.</p>
            <button
              className="btn-primary"
              type="button"
              onClick={() => setShowCreateModal(true)}
            >
              Create Item
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>SKU</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Unit</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.name || 'N/A'}</td>
                    <td>{item.sku || 'N/A'}</td>
                    <td>₹{item.price || '0.00'}</td>
                    <td>{item.stock || '0'}</td>
                    <td>{item.unit || 'N/A'}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleViewItem(item.id)}
                          title="View"
                        >
                          <ActionIcons.View size={18} title="View" />
                        </button>
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleEditItem(item.id)}
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
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Create Item</h2>
            <form onSubmit={handleCreateItem} className="modal-form">
              <div className="modal-grid">
                <div className="form-group">
                  <label>Name *</label>
                  <input
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Code *</label>
                  <input
                    name="code"
                    type="text"
                    value={formData.code}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Unit *</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleInputChange}
                    required
                    disabled={unitsLoading}
                  >
                    <option value="">Select unit</option>
                    {units.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name} {u.code ? `(${u.code})` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Quantity</label>
                  <input
                    name="quantity"
                    type="number"
                    min="0"
                    step="1"
                    value={formData.quantity}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Cost Price</label>
                  <input
                    name="price"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.price}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Sales Price</label>
                  <input
                    name="sales_price"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.sales_price}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group form-group--inline">
                  <label>
                    <input
                      type="checkbox"
                      name="tax_applied"
                      checked={formData.tax_applied}
                      onChange={handleInputChange}
                    />{' '}
                    Tax Applied
                  </label>
                </div>
                <div className="form-group">
                  <label>Tax Percent</label>
                  <input
                    name="tax_percent"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.tax_percent}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  rows="3"
                  value={formData.description}
                  onChange={handleInputChange}
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
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={creating}
                >
                  {creating ? 'Saving...' : 'Save Item'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showViewModal && selectedItem && (
        <div
          className="modal-overlay"
          onClick={() => setShowViewModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Item Details</h2>
            <div className="view-details">
              <div className="detail-row">
                <span className="detail-label">Name:</span>
                <span className="detail-value">{selectedItem.name || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">SKU/Code:</span>
                <span className="detail-value">{selectedItem.code || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Unit:</span>
                <span className="detail-value">{selectedItem.unit_name || selectedItem.unit || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Quantity/Stock:</span>
                <span className="detail-value">{selectedItem.quantity || selectedItem.stock || '0'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Purchase Price:</span>
                <span className="detail-value">₹{selectedItem.price?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Sales Price:</span>
                <span className="detail-value">₹{selectedItem.sales_price?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Tax Applied:</span>
                <span className="detail-value">{selectedItem.tax_applied ? 'Yes' : 'No'}</span>
              </div>
              {selectedItem.tax_applied && (
                <div className="detail-row">
                  <span className="detail-label">Tax %:</span>
                  <span className="detail-value">{selectedItem.tax_percent || 0}%</span>
                </div>
              )}
              {selectedItem.description && (
                <div className="detail-row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.25rem' }}>
                  <span className="detail-label">Description:</span>
                  <span className="detail-value">{selectedItem.description}</span>
                </div>
              )}
            </div>
            <div className="modal-actions">
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

      {showEditModal && selectedItem && (
        <div
          className="modal-overlay"
          onClick={() => !updating && setShowEditModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Edit Item</h2>
            <form onSubmit={handleUpdateItem} className="modal-form">
              <div className="modal-grid">
                <div className="form-group">
                  <label>Name *</label>
                  <input
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>SKU/Code</label>
                  <input
                    name="code"
                    type="text"
                    value={formData.code}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Unit *</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Select unit</option>
                    {units.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Quantity</label>
                  <input
                    name="quantity"
                    type="number"
                    min="0"
                    value={formData.quantity}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Purchase Price</label>
                  <input
                    name="price"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.price}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Sales Price</label>
                  <input
                    name="sales_price"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.sales_price}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Tax Applied</label>
                  <input
                    name="tax_applied"
                    type="checkbox"
                    checked={formData.tax_applied}
                    onChange={(e) => setFormData((prev) => ({ ...prev, tax_applied: e.target.checked }))}
                  />
                </div>
                {formData.tax_applied && (
                  <div className="form-group">
                    <label>Tax %</label>
                    <input
                      name="tax_percent"
                      type="number"
                      min="0"
                      max="100"
                      step="0.01"
                      value={formData.tax_percent}
                      onChange={handleInputChange}
                    />
                  </div>
                )}
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  rows="3"
                  value={formData.description}
                  onChange={handleInputChange}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => !updating && setShowEditModal(false)}
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={updating}
                >
                  {updating ? 'Updating...' : 'Update Item'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Items
