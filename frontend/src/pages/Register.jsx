import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { toast } from 'react-toastify'
import './Login.css'

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    phone: '',
    address: '',
  })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (formData.password !== formData.password2) {
      toast.error('Passwords do not match')
      return
    }

    setLoading(true)

    const userData = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      phone: formData.phone,
      address: formData.address,
    }

    const result = await register(userData)

    if (result.success) {
      toast.success('Registration successful! Please login.')
      navigate('/login')
    } else {
      toast.error(result.error?.detail || 'Registration failed')
    }

    setLoading(false)
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>ERP Management System</h1>
        <h2>Register</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="address">Address</label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
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
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password2">Confirm Password</label>
            <input
              type="password"
              id="password2"
              name="password2"
              value={formData.password2}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        <p className="register-link">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
