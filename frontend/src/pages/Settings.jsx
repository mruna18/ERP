import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { authService } from '../services/authService'
import { toast } from 'react-toastify'
import './Settings.css'

const THEME_KEY = 'app_theme'
const NOTIFICATIONS_KEY = 'app_notifications'

const defaultNotifications = {
  email: true,
  invoiceCreated: true,
  paymentReceived: true,
  partyAdded: true,
  reportSummary: false,
}

const getStoredNotifications = () => {
  try {
    const raw = localStorage.getItem(NOTIFICATIONS_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      return { ...defaultNotifications, ...parsed }
    }
  } catch (_) {}
  return { ...defaultNotifications }
}

const Settings = () => {
  const { user, refreshUser } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
  })
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [preferences, setPreferences] = useState({ theme: 'light' })
  const [notifications, setNotifications] = useState(getStoredNotifications)
  const [saving, setSaving] = useState(false)
  const [changingPassword, setChangingPassword] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name ?? '',
        last_name: user.last_name ?? '',
        email: user.email ?? '',
        phone: user.phone ?? '',
        address: user.address ?? '',
      })
    }
    setPreferences((p) => ({ ...p, theme: localStorage.getItem(THEME_KEY) || 'light' }))
    setNotifications(getStoredNotifications())
    setLoading(false)
  }, [user])

  const applyTheme = (theme) => {
    const root = document.documentElement
    root.classList.remove('theme-light', 'theme-dark')
    if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      root.classList.add('theme-dark')
    } else {
      root.classList.add('theme-light')
    }
  }

  useEffect(() => {
    const stored = localStorage.getItem(THEME_KEY) || 'light'
    applyTheme(stored)
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handlePasswordChange = (e) => {
    const { name, value } = e.target
    setPasswordForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmitProfile = async (e) => {
    e.preventDefault()
    if (!user?.id) return
    setSaving(true)
    try {
      await authService.updateProfile(user.id, {
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        phone: form.phone,
        address: form.address,
      })
      toast.success('Profile updated successfully')
      await refreshUser()
    } catch (error) {
      const msg = error.response?.data?.username?.[0] || error.response?.data?.email?.[0] || error.response?.data?.detail || 'Failed to update profile'
      toast.error(typeof msg === 'string' ? msg : 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('New passwords do not match')
      return
    }
    if (passwordForm.new_password.length < 8) {
      toast.error('New password must be at least 8 characters')
      return
    }
    setChangingPassword(true)
    try {
      await authService.changePassword(passwordForm.current_password, passwordForm.new_password)
      toast.success('Password changed successfully')
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' })
    } catch (error) {
      const msg = error.response?.data?.error || 'Failed to change password'
      toast.error(msg)
    } finally {
      setChangingPassword(false)
    }
  }

  const handleThemeChange = (e) => {
    const theme = e.target.value
    setPreferences((p) => ({ ...p, theme }))
    localStorage.setItem(THEME_KEY, theme)
    applyTheme(theme)
    toast.success('Theme updated')
  }

  const handleNotificationChange = (key, value) => {
    const next = { ...notifications, [key]: value }
    setNotifications(next)
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(next))
    toast.success('Notification preferences saved')
  }

  const handleNotificationToggle = (e) => {
    const checked = e.target.checked
    handleNotificationChange('email', checked)
  }

  const handleNotificationOptionToggle = (key) => (e) => {
    handleNotificationChange(key, e.target.checked)
  }

  if (loading || !user) {
    return (
      <div className="page-container settings-page">
        <div className="settings-loading">Loading...</div>
      </div>
    )
  }

  const tabs = [
    { id: 'profile', label: 'Profile' },
    { id: 'password', label: 'Password' },
    { id: 'preferences', label: 'Preferences' },
    { id: 'notifications', label: 'Notifications' },
  ]

  return (
    <div className="page-container settings-page">
      <header className="settings-header">
        <h1>Settings</h1>
        <p className="settings-desc">Manage your account, security, and preferences.</p>
      </header>

      <div className="settings-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="settings-content">
        {activeTab === 'profile' && (
          <section className="settings-card">
            <h2 className="settings-card-title">Profile details</h2>
            <p className="settings-card-desc">Update your name, email, and contact information.</p>
            <form onSubmit={handleSubmitProfile} className="settings-form">
              <div className="settings-form-row">
                <div className="form-group">
                  <label htmlFor="first_name">First name</label>
                  <input
                    id="first_name"
                    type="text"
                    name="first_name"
                    value={form.first_name}
                    onChange={handleChange}
                    placeholder="First name"
                    autoComplete="given-name"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="last_name">Last name</label>
                  <input
                    id="last_name"
                    type="text"
                    name="last_name"
                    value={form.last_name}
                    onChange={handleChange}
                    placeholder="Last name"
                    autoComplete="family-name"
                  />
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  autoComplete="email"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone">Phone</label>
                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  placeholder="Phone number"
                  autoComplete="tel"
                />
              </div>
              <div className="form-group">
                <label htmlFor="address">Address</label>
                <textarea
                  id="address"
                  name="address"
                  value={form.address}
                  onChange={handleChange}
                  placeholder="Address"
                  rows={3}
                />
              </div>
              <div className="settings-form-actions">
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : 'Save changes'}
                </button>
              </div>
            </form>
          </section>
        )}

        {activeTab === 'password' && (
          <section className="settings-card">
            <h2 className="settings-card-title">Change password</h2>
            <p className="settings-card-desc">Update your password to keep your account secure.</p>
            <form onSubmit={handleChangePassword} className="settings-form">
              <div className="form-group">
                <label htmlFor="current_password">Current password</label>
                <input
                  id="current_password"
                  type="password"
                  name="current_password"
                  value={passwordForm.current_password}
                  onChange={handlePasswordChange}
                  placeholder="Enter current password"
                  autoComplete="current-password"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="new_password">New password</label>
                <input
                  id="new_password"
                  type="password"
                  name="new_password"
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                  placeholder="At least 8 characters"
                  autoComplete="new-password"
                  required
                  minLength={8}
                />
              </div>
              <div className="form-group">
                <label htmlFor="confirm_password">Confirm new password</label>
                <input
                  id="confirm_password"
                  type="password"
                  name="confirm_password"
                  value={passwordForm.confirm_password}
                  onChange={handlePasswordChange}
                  placeholder="Confirm new password"
                  autoComplete="new-password"
                  required
                />
              </div>
              <div className="settings-form-actions">
                <button type="submit" className="btn-primary" disabled={changingPassword}>
                  {changingPassword ? 'Updating…' : 'Change password'}
                </button>
              </div>
            </form>
          </section>
        )}

        {activeTab === 'preferences' && (
          <section className="settings-card">
            <h2 className="settings-card-title">Preferences</h2>
            <p className="settings-card-desc">Customize how the app looks and behaves.</p>
            <div className="settings-form">
              <div className="form-group">
                <label htmlFor="theme">Theme</label>
                <select
                  id="theme"
                  value={preferences.theme}
                  onChange={handleThemeChange}
                  className="settings-select"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System (match device)</option>
                </select>
                <span className="form-hint">Choose light, dark, or follow your device setting.</span>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'notifications' && (
          <section className="settings-card">
            <h2 className="settings-card-title">Notifications</h2>
            <p className="settings-card-desc">Choose when and how you want to be notified.</p>
            <div className="settings-form">
              <div className="settings-toggle-row">
                <div>
                  <span className="settings-toggle-label">Email notifications</span>
                  <span className="settings-toggle-desc">Enable or disable all email notifications.</span>
                </div>
                <label className="settings-switch">
                  <input
                    type="checkbox"
                    checked={notifications.email}
                    onChange={handleNotificationToggle}
                  />
                  <span className="settings-slider" />
                </label>
              </div>

              {notifications.email && (
                <div className="settings-notification-options">
                  <span className="settings-notification-options-title">Notify me by email when</span>
                  <div className="settings-toggle-row settings-toggle-row--sub">
                    <div>
                      <span className="settings-toggle-label">New invoice created</span>
                      <span className="settings-toggle-desc">An invoice is created for your company.</span>
                    </div>
                    <label className="settings-switch">
                      <input
                        type="checkbox"
                        checked={notifications.invoiceCreated}
                        onChange={handleNotificationOptionToggle('invoiceCreated')}
                      />
                      <span className="settings-slider" />
                    </label>
                  </div>
                  <div className="settings-toggle-row settings-toggle-row--sub">
                    <div>
                      <span className="settings-toggle-label">Payment received</span>
                      <span className="settings-toggle-desc">A payment is recorded (payment in or out).</span>
                    </div>
                    <label className="settings-switch">
                      <input
                        type="checkbox"
                        checked={notifications.paymentReceived}
                        onChange={handleNotificationOptionToggle('paymentReceived')}
                      />
                      <span className="settings-slider" />
                    </label>
                  </div>
                  <div className="settings-toggle-row settings-toggle-row--sub">
                    <div>
                      <span className="settings-toggle-label">New party added</span>
                      <span className="settings-toggle-desc">A customer or supplier is added to your company.</span>
                    </div>
                    <label className="settings-switch">
                      <input
                        type="checkbox"
                        checked={notifications.partyAdded}
                        onChange={handleNotificationOptionToggle('partyAdded')}
                      />
                      <span className="settings-slider" />
                    </label>
                  </div>
                  <div className="settings-toggle-row settings-toggle-row--sub">
                    <div>
                      <span className="settings-toggle-label">Report summary</span>
                      <span className="settings-toggle-desc">Optional daily or weekly summary (when available).</span>
                    </div>
                    <label className="settings-switch">
                      <input
                        type="checkbox"
                        checked={notifications.reportSummary}
                        onChange={handleNotificationOptionToggle('reportSummary')}
                      />
                      <span className="settings-slider" />
                    </label>
                  </div>
                </div>
              )}

              <div className="settings-notification-inapp">
                <span className="settings-toggle-label">In-app notifications</span>
                <span className="settings-toggle-desc">Toast messages in the app are always shown for important actions. You can dismiss them anytime.</span>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

export default Settings
