import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { toast } from 'react-toastify'
import ActionIcons from '../components/ActionIcons'
import './Parties.css'

const Parties = () => {
  const { selectedCompany } = useAuth()
  const [parties, setParties] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [selectedParty, setSelectedParty] = useState(null)
  const [partyTypes, setPartyTypes] = useState([])
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    gst_number: '',
    address: '',
    party_type: '',
  })

  useEffect(() => {
    if (selectedCompany) {
      fetchParties()
    }
  }, [selectedCompany])

  useEffect(() => {
    if (showCreateModal || showEditModal) {
      fetchPartyTypes()
    }
  }, [showCreateModal, showEditModal])

  const fetchParties = async () => {
    try {
      const response = await api.post('/parties/', {
        company: selectedCompany.id,
      })
      setParties(response.data?.data || [])
    } catch (error) {
      console.error('Failed to fetch parties:', error)
      toast.error('Failed to load parties')
    } finally {
      setLoading(false)
    }
  }

  const fetchPartyTypes = async () => {
    try {
      const response = await api.get('/parties/types/')
      setPartyTypes(response.data || [])
      // Set default to first party type if available
      if (response.data && response.data.length > 0 && !formData.party_type) {
        setFormData((prev) => ({ ...prev, party_type: response.data[0].id }))
      }
    } catch (error) {
      console.error('Failed to fetch party types:', error)
      toast.error('Failed to load party types')
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'party_type' ? (value ? Number(value) : '') : value,
    }))
  }

  const handleViewParty = async (partyId) => {
    try {
      const response = await api.get(`/parties/${selectedCompany.id}/${partyId}/`)
      setSelectedParty(response.data?.data || null)
      setShowViewModal(true)
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load party details')
    }
  }

  const handleEditParty = async (partyId) => {
    try {
      const response = await api.get(`/parties/${selectedCompany.id}/${partyId}/`)
      const party = response.data?.data || null
      if (party) {
        setSelectedParty(party)
        setFormData({
          name: party.name || '',
          email: party.email || '',
          phone: party.phone || '',
          gst_number: party.gst_number || '',
          address: party.address || '',
          party_type: party.party_type || '',
        })
        setShowEditModal(true)
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load party details')
    }
  }

  const handleUpdateParty = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !selectedParty || !formData.party_type) {
      toast.error('Party type is required')
      return
    }
    setUpdating(true)

    try {
      const payload = {
        ...formData,
        company: selectedCompany.id,
        party_type: Number(formData.party_type),
      }
      const response = await api.put(`/parties/${selectedParty.id}/update/`, payload)
      if (response.data?.error) {
        toast.error(response.data.error)
        return
      }

      toast.success(response.data?.message || 'Party updated successfully')
      setShowEditModal(false)
      setSelectedParty(null)
      setFormData({
        name: '',
        email: '',
        phone: '',
        gst_number: '',
        address: '',
        party_type: '',
      })
      setLoading(true)
      fetchParties()
    } catch (error) {
      const msg =
        error.response?.data?.error ||
        error.response?.data?.detail ||
        'Failed to update party'
      toast.error(msg)
    } finally {
      setUpdating(false)
    }
  }

  const handleCreateParty = async (e) => {
    e.preventDefault()
    if (!selectedCompany || !formData.party_type) {
      toast.error('Party type is required')
      return
    }
    setCreating(true)

    try {
      const payload = {
        ...formData,
        company: selectedCompany.id,
        party_type: Number(formData.party_type),
      }
      const response = await api.post('/parties/create/', payload)
      if (response.data?.error) {
        toast.error(response.data.error)
        return
      }

      toast.success(response.data?.message || 'Party created successfully')
      setShowCreateModal(false)
      setFormData({
        name: '',
        email: '',
        phone: '',
        gst_number: '',
        address: '',
        party_type: partyTypes.length > 0 ? partyTypes[0].id : '',
      })
      setLoading(true)
      fetchParties()
    } catch (error) {
      const msg =
        error.response?.data?.error ||
        error.response?.data?.detail ||
        'Failed to create party'
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
          <p>Go to Dashboard and select a company to view parties.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Parties</h1>
        <button
          className="btn-primary"
          type="button"
          onClick={() => setShowCreateModal(true)}
        >
          + Create Party
        </button>
      </div>

      <div className="content-card">
        {loading ? (
          <p>Loading parties...</p>
        ) : parties.length === 0 ? (
          <div className="empty-state">
            <p>No parties found. Create your first party to get started.</p>
            <button
              className="btn-primary"
              type="button"
              onClick={() => setShowCreateModal(true)}
            >
              Create Party
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th>Address</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {parties.map((party) => (
                  <tr key={party.id}>
                    <td>{party.name || 'N/A'}</td>
                    <td>{party.party_type_name || 'N/A'}</td>
                    <td>{party.phone || 'N/A'}</td>
                    <td>{party.email || 'N/A'}</td>
                    <td>{party.address || 'N/A'}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleViewParty(party.id)}
                          title="View"
                        >
                          <ActionIcons.View size={18} title="View" />
                        </button>
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => handleEditParty(party.id)}
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
            <h2>Create Party</h2>
            <form onSubmit={handleCreateParty} className="modal-form">
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
                  <label>Type *</label>
                  <select
                    name="party_type"
                    value={formData.party_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Select type</option>
                    {partyTypes.map((pt) => (
                      <option key={pt.id} value={pt.id}>
                        {pt.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>GST Number</label>
                  <input
                    name="gst_number"
                    type="text"
                    value={formData.gst_number}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Address</label>
                <textarea
                  name="address"
                  rows="3"
                  value={formData.address}
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
                  {creating ? 'Saving...' : 'Save Party'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showViewModal && selectedParty && (
        <div
          className="modal-overlay"
          onClick={() => setShowViewModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Party Details</h2>
            <div className="view-details">
              <div className="detail-row">
                <span className="detail-label">Name:</span>
                <span className="detail-value">{selectedParty.name || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{selectedParty.party_type_name || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Phone:</span>
                <span className="detail-value">{selectedParty.phone || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Email:</span>
                <span className="detail-value">{selectedParty.email || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">GST Number:</span>
                <span className="detail-value">{selectedParty.gst_number || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Address:</span>
                <span className="detail-value">{selectedParty.address || 'N/A'}</span>
              </div>
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

      {showEditModal && selectedParty && (
        <div
          className="modal-overlay"
          onClick={() => !updating && setShowEditModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Edit Party</h2>
            <form onSubmit={handleUpdateParty} className="modal-form">
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
                  <label>Type *</label>
                  <select
                    name="party_type"
                    value={formData.party_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Select type</option>
                    {partyTypes.map((pt) => (
                      <option key={pt.id} value={pt.id}>
                        {pt.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>GST Number</label>
                  <input
                    name="gst_number"
                    type="text"
                    value={formData.gst_number}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Address</label>
                <textarea
                  name="address"
                  rows="3"
                  value={formData.address}
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
                  {updating ? 'Updating...' : 'Update Party'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Parties
